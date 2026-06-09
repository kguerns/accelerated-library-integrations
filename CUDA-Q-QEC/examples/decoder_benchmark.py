"""Benchmark CUDA-Q QEC decoder throughput on one surface-code workload."""

import argparse
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from surface_memory import (
    build_decoder,
    count_logical_errors,
    load_dependencies,
    preprocess_syndromes,
    write_csv,
)


PROJECT = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", default="brev_l4", help="label for this run, default: brev_l4")
    parser.add_argument("--decoder", default=None, help="run one decoder only")
    parser.add_argument("--decoders", nargs="+", default=["single_error_lut", "nv-qldpc-decoder"])
    parser.add_argument("--shots", type=int, default=2000)
    parser.add_argument("--distance", type=int, default=7)
    parser.add_argument("--rounds", type=int, default=None)
    parser.add_argument("--p", type=float, default=0.001)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--max-iterations", type=int, default=50)
    parser.add_argument("--bp-batch-size", type=int, default=10000)
    parser.add_argument("--bp-method", type=int, default=None, help="QLDPC BP method, e.g. 1 for min-sum")
    parser.add_argument("--output", help="CSV output path")
    return parser.parse_args()


def gpu_name():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader", "-i", "0"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return platform.processor() or platform.machine() or "unknown"
    return result.stdout.strip().splitlines()[0] if result.returncode == 0 and result.stdout.strip() else "unknown"


def synchronize_gpu():
    try:
        import cupy as cp

        cp.cuda.runtime.deviceSynchronize()
    except Exception:
        pass


def decode_single_loop(decoder, syndromes):
    return [decoder.decode(row) for row in syndromes]


def decode_batch(decoder, syndromes):
    if hasattr(decoder, "decode_batch"):
        return decoder.decode_batch(syndromes)
    return decode_single_loop(decoder, syndromes)


def decoder_path(decoder):
    return "decode_batch" if hasattr(decoder, "decode_batch") else "decode_loop"


def time_decode(decoder, syndromes, warmup, repeats):
    decode_fn = decode_batch
    for _ in range(warmup):
        decode_fn(decoder, syndromes)
    synchronize_gpu()

    samples = []
    last_results = None
    for _ in range(repeats):
        synchronize_gpu()
        start = time.perf_counter()
        last_results = decode_fn(decoder, syndromes)
        synchronize_gpu()
        samples.append((time.perf_counter() - start) * 1000)
    return samples, last_results


def improvement(raw_errors, decoded_errors):
    if decoded_errors == 0:
        return "inf" if raw_errors else ""
    return raw_errors / decoded_errors


def make_row(args, decoder_name, path, gpu, rounds, samples_ms, decoded, np, logical_z, observables, data):
    median_ms = statistics.median(samples_ms)
    logical_without, logical_with = count_logical_errors(np, logical_z, observables, data, decoded)
    return {
        "platform": args.platform,
        "gpu_name": gpu,
        "decoder": decoder_name,
        "decode_path": path,
        "code": "surface_code",
        "distance": args.distance,
        "rounds": rounds,
        "physical_error_probability": args.p,
        "shots": args.shots,
        "warmup": args.warmup,
        "repeats": args.repeats,
        "median_ms": median_ms,
        "min_ms": min(samples_ms),
        "max_ms": max(samples_ms),
        "syndromes_per_second": args.shots / (median_ms / 1000),
        "bp_method": args.bp_method if args.bp_method is not None else "",
        "raw_logical_errors": logical_without,
        "decoded_logical_errors": logical_with,
        "raw_logical_error_rate": logical_without / args.shots,
        "decoded_logical_error_rate": logical_with / args.shots,
        "logical_error_reduction_vs_raw": improvement(logical_without, logical_with),
        "speedup_vs_lut": "",
        "logical_error_ratio_vs_lut": "",
    }


def main():
    args = parse_args()
    decoders = [args.decoder] if args.decoder else args.decoders

    if args.output is None:
        if set(decoders) == {"single_error_lut", "nv-qldpc-decoder"}:
            output_name = f"decoder_lut_vs_qldpc_d{args.distance}_{args.platform}.csv"
        else:
            label = "_".join(decoder.replace("single_error_lut", "lut").replace("nv-qldpc-decoder", "qldpc").replace("-", "_") for decoder in decoders)
            output_name = f"decoder_{label}_d{args.distance}_{args.platform}.csv"
        args.output = str(PROJECT / "results" / output_name)

    if args.shots < 1 or args.repeats < 1 or args.warmup < 0:
        sys.exit("FAIL: --shots and --repeats must be >= 1; --warmup must be >= 0")
    if args.distance < 3:
        sys.exit("FAIL: --distance must be >= 3")
    if args.p < 0 or args.p > 1:
        sys.exit("FAIL: --p must be in [0, 1]")

    np, cudaq, qec = load_dependencies()
    cudaq.set_target("stim")

    rounds = args.rounds if args.rounds is not None else args.distance
    if rounds < 1:
        sys.exit("FAIL: --rounds must be >= 1")

    code = qec.get_code("surface_code", distance=args.distance)
    logical_z = np.asarray(code.get_observables_z(), dtype=np.uint8)
    state_prep = qec.operation.prep0

    noise = cudaq.NoiseModel()
    noise.add_all_qubit_channel("x", cudaq.Depolarization2(args.p), 1)

    dem = qec.z_dem_from_memory_circuit(code, state_prep, rounds, noise)
    h_matrix = np.ascontiguousarray(dem.detector_error_matrix, dtype=np.uint8)
    observables = np.asarray(dem.observables_flips_matrix, dtype=np.uint8)

    print(
        f"Preparing one workload "
        f"(decoders={', '.join(decoders)}, shots={args.shots}, d={args.distance}, p={args.p})..."
    )
    syndromes, data = qec.sample_memory_circuit(code, state_prep, args.shots, rounds, noise)
    syndromes = preprocess_syndromes(np, syndromes, args.shots, rounds, h_matrix.shape[0])
    data = np.asarray(data, dtype=np.uint8)

    gpu = gpu_name()
    rows = []
    for decoder_name in decoders:
        decoder = build_decoder(
            qec,
            decoder_name,
            h_matrix,
            min(args.bp_batch_size, args.shots),
            args.max_iterations,
            args.p,
            args.bp_method,
        )
        path = decoder_path(decoder)
        print(f"Timing {decoder_name} ({path}, warmup={args.warmup}, repeats={args.repeats})...")
        samples_ms, decoded = time_decode(decoder, syndromes, args.warmup, args.repeats)
        rows.append(make_row(args, decoder_name, path, gpu, rounds, samples_ms, decoded, np, logical_z, observables, data))

    lut = next((row for row in rows if row["decoder"] == "single_error_lut"), None)
    if lut:
        for row in rows:
            row["speedup_vs_lut"] = float(row["syndromes_per_second"]) / float(lut["syndromes_per_second"])
            lut_rate = float(lut["decoded_logical_error_rate"])
            row_rate = float(row["decoded_logical_error_rate"])
            row["logical_error_ratio_vs_lut"] = row_rate / lut_rate if lut_rate else ""

    write_csv(Path(args.output), rows)

    print()
    print(f"GPU:      {gpu}")
    print(f"Workload: surface_code d={args.distance}, rounds={rounds}, p={args.p}, shots={args.shots}")
    if "nv-qldpc-decoder" in decoders:
        print(f"BP:      {args.bp_method if args.bp_method is not None else 'default'}")
    print()
    print(
        f"{'decoder':<18} {'path':<12} {'median ms':>10} {'syndromes/s':>14} "
        f"{'speed/LUT':>9} {'raw errs':>10} {'decoded errs':>13} "
        f"{'decoded rate':>13} {'gain':>8} {'rate/LUT':>9}"
    )
    print("-" * 122)
    for row in rows:
        speedup = row["speedup_vs_lut"]
        speedup_text = f"{float(speedup):.2f}x" if speedup != "" else ""
        gain = row["logical_error_reduction_vs_raw"]
        gain_text = f"{float(gain):.2f}x" if gain not in ("", "inf") else gain
        rate_ratio = row["logical_error_ratio_vs_lut"]
        rate_ratio_text = f"{float(rate_ratio):.2f}x" if rate_ratio != "" else ""
        print(
            f"{row['decoder']:<18} "
            f"{row['decode_path']:<12} "
            f"{row['median_ms']:>10.3f} "
            f"{row['syndromes_per_second']:>14,.1f} "
            f"{speedup_text:>9} "
            f"{row['raw_logical_errors']:>10} "
            f"{row['decoded_logical_errors']:>13} "
            f"{row['decoded_logical_error_rate']:>13.4g} "
            f"{gain_text:>8} "
            f"{rate_ratio_text:>9}"
        )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
