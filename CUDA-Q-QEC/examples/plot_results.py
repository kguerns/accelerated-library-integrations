"""Generate presentation plots from CUDA-Q QEC result CSVs."""

import argparse
import csv
import sys
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def read_csv_rows(results_dir):
    rows = []
    for path in sorted(results_dir.glob("*.csv")):
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                row["_source"] = path.stem
                rows.append(row)
    return rows


def benchmark_rows(rows):
    return [
        row
        for row in rows
        if row.get("platform") and row.get("decoder") and row.get("syndromes_per_second")
    ]


def cpu_gpu_rows(rows):
    return [row for row in rows if row.get("benchmark") == "cpu_gpu_syndrome"]


def plot_steane(plt, rows, output_dir):
    grouped = {}
    for row in rows:
        if (
            row.get("code") == "steane"
            and row.get("raw_logical_error_rate")
            and row.get("decoded_logical_error_rate")
        ):
            grouped.setdefault(row["_source"], []).append(row)

    if not grouped:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    for label, group in grouped.items():
        ordered = sorted(group, key=lambda row: float(row["physical_error_probability"]))
        x = [float(row["physical_error_probability"]) for row in ordered]
        raw = [float(row["raw_logical_error_rate"]) for row in ordered]
        decoded = [float(row["decoded_logical_error_rate"]) for row in ordered]
        ax.plot(x, raw, marker="o", linestyle="--", label=f"{label} raw")
        ax.plot(x, decoded, marker="o", label=f"{label} decoded")

    ax.set(
        title="Steane Code Logical Error Rate",
        xlabel="Physical error probability",
        ylabel="Logical error rate",
    )
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    output = output_dir / "steane_logical_error_rates.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"Wrote {output}")
    return output


def plot_cpu_gpu_speedup(plt, rows, output_dir):
    comparison_rows = cpu_gpu_rows(rows)
    if not comparison_rows:
        return

    ordered = sorted(comparison_rows, key=lambda row: row["backend"])
    labels = [row["backend"].replace("_", " ").upper() for row in ordered]
    values = [float(row["syndromes_per_second"]) for row in ordered]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values)
    ax.set(title="CPU vs GPU QEC Syndrome Throughput", ylabel="Syndromes per second")
    ax.grid(True, axis="y", alpha=0.3)
    ax.bar_label(bars, fmt=lambda value: f"{value:,.0f}", padding=3)
    fig.tight_layout()

    output = output_dir / "cpu_gpu_speedup.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"Wrote {output}")
    return output


def decoder_label(row):
    decoder = row["decoder"].replace("single_error_lut", "LUT").replace("nv-qldpc-decoder", "QLDPC")
    label = f"d={row.get('distance', '?')}\n{decoder}"
    if row.get("mode"):
        label += f"\n{row['mode']}"
    if row.get("decode_path"):
        label += f"\n{row['decode_path'].replace('decode_', '')}"
    if row.get("bp_method"):
        label += f"\nbp={row['bp_method']}"
    return label


def decoder_rate(row):
    return float(row.get("logical_error_rate") or row.get("decoded_logical_error_rate"))


def decoder_errors(row):
    return row.get("logical_errors") or row.get("decoded_logical_errors")


def decoder_speedup(row):
    return row.get("speedup_vs_lut") or 1.0


def plot_decoder(plt, rows, output_dir):
    decoder_rows = benchmark_rows(rows)
    if not decoder_rows:
        return

    ordered = sorted(decoder_rows, key=lambda row: (int(row.get("distance", 0)), row["decoder"]))
    labels = [decoder_label(row) for row in ordered]
    values = [float(row["syndromes_per_second"]) for row in ordered]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values)
    ax.set(title="CUDA-Q QEC Decoder Throughput", ylabel="Syndromes per second")
    ax.grid(True, axis="y", alpha=0.3)
    ax.bar_label(bars, fmt=lambda value: f"{value:,.0f}", padding=3)
    fig.tight_layout()

    output = output_dir / "decoder_throughput.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"Wrote {output}")
    return output


def plot_decoder_accuracy(plt, rows, output_dir):
    decoder_rows = benchmark_rows(rows)
    if not decoder_rows:
        return

    ordered = sorted(decoder_rows, key=lambda row: (int(row["distance"]), row["decoder"]))
    labels = [decoder_label(row) for row in ordered]
    values = [decoder_rate(row) for row in ordered]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values)
    ax.set(title="CUDA-Q QEC Decoder Logical Error Rate", ylabel="Logical error rate")
    ax.grid(True, axis="y", alpha=0.3)
    ax.bar_label(bars, fmt=lambda value: f"{value:.3g}", padding=3)
    fig.tight_layout()

    output = output_dir / "decoder_logical_error_rate.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"Wrote {output}")
    return output


def plot_decoder_tradeoff(plt, rows, output_dir):
    decoder_rows = benchmark_rows(rows)
    if not decoder_rows:
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    for row in decoder_rows:
        throughput = float(row["syndromes_per_second"])
        rate = decoder_rate(row)
        if rate == 0:
            rate = 0.5 / float(row["shots"])
        marker = "o" if row["decoder"] == "nv-qldpc-decoder" else "s"
        ax.scatter(throughput, rate, marker=marker, s=70)
        ax.annotate(decoder_label(row).replace("\n", " "), (throughput, rate), xytext=(6, 5), textcoords="offset points")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set(
        title="Decoder Speed vs Logical Error Rate",
        xlabel="Syndromes per second",
        ylabel="Logical error rate",
    )
    ax.grid(True, which="both", alpha=0.3)
    fig.tight_layout()

    output = output_dir / "decoder_tradeoff.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"Wrote {output}")
    return output


def rate(value):
    return f"{float(value):.4g}"


def write_summary(rows, output_dir):
    lines = ["# CUDA-Q QEC Result Summary", ""]

    steane_rows = sorted(
        [row for row in rows if row.get("code") == "steane"],
        key=lambda row: float(row["physical_error_probability"]),
    )
    if steane_rows:
        lines += [
            "## Steane Code-Capacity Demo",
            "",
            "| p | raw errors | decoded errors | raw rate | decoded rate |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for row in steane_rows:
            lines.append(
                f"| {float(row['physical_error_probability']):.4f} "
                f"| {row['raw_logical_errors']} "
                f"| {row['decoded_logical_errors']} "
                f"| {rate(row['raw_logical_error_rate'])} "
                f"| {rate(row['decoded_logical_error_rate'])} |"
            )
        lines.append("")

    surface_rows = [
        row
        for row in rows
        if row.get("code") == "surface_code"
        and row.get("logical_error_rate_with_decoding")
        and not row.get("syndromes_per_second")
    ]
    if surface_rows:
        lines += [
            "## Surface-Code Logical Error Results",
            "",
            "| decoder | distance | p | shots | without decoding | with decoding |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in sorted(surface_rows, key=lambda row: (row["decoder"], int(row["distance"]), float(row["physical_error_probability"]))):
            lines.append(
                f"| {row['decoder']} "
                f"| {row['distance']} "
                f"| {float(row['physical_error_probability']):.4f} "
                f"| {row['shots']} "
                f"| {rate(row['logical_error_rate_without_decoding'])} "
                f"| {rate(row['logical_error_rate_with_decoding'])} |"
            )
        lines.append("")

    comparison_rows = cpu_gpu_rows(rows)
    if comparison_rows:
        lines += [
            "## CPU vs GPU Syndrome Benchmark",
            "",
            "| backend | median ms | syndromes/s | speedup vs CPU | scope |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
        for row in sorted(comparison_rows, key=lambda row: row["backend"]):
            lines.append(
                f"| {row['backend']} "
                f"| {float(row['median_ms']):.3f} "
                f"| {float(row['syndromes_per_second']):,.0f} "
                f"| {float(row['speedup_vs_cpu']):.2f}x "
                f"| {row.get('scope', '')} |"
            )
        lines.append("")

    decoder_rows = benchmark_rows(rows)
    if decoder_rows:
        lines += [
            "## Decoder Benchmark Results",
            "",
            "| decoder | path | distance | GPU | median ms | syndromes/s | speed vs LUT | raw errors | decoded errors | decoded rate | gain vs raw | rate vs LUT |",
            "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in sorted(decoder_rows, key=lambda row: (int(row["distance"]), row["decoder"], row.get("decode_path", row.get("mode", "")))):
            gain = row.get("logical_error_reduction_vs_raw", "")
            gain_text = f"{float(gain):.2f}x" if gain not in ("", "inf") else gain
            rate_ratio = row.get("logical_error_ratio_vs_lut", "")
            rate_ratio_text = f"{float(rate_ratio):.2f}x" if rate_ratio else ""
            lines.append(
                f"| {row['decoder']} "
                f"| {row.get('decode_path') or row.get('mode', '')} "
                f"| {row['distance']} "
                f"| {row.get('gpu_name', '')} "
                f"| {float(row['median_ms']):.3f} "
                f"| {float(row['syndromes_per_second']):,.0f} "
                f"| {float(decoder_speedup(row)):.2f}x "
                f"| {row.get('raw_logical_errors') or row.get('logical_errors_without_decoding', '')}/{row['shots']} "
                f"| {decoder_errors(row)}/{row['shots']} "
                f"| {rate(decoder_rate(row))} "
                f"| {gain_text} "
                f"| {rate_ratio_text} |"
            )
        lines.append("")

        lines += ["## Decoder Comparison Takeaway", ""]
        by_distance = {}
        for row in decoder_rows:
            by_distance.setdefault(row["distance"], {})[row["decoder"]] = row
        for distance, group in sorted(by_distance.items(), key=lambda item: int(item[0])):
            lut = group.get("single_error_lut")
            qldpc = group.get("nv-qldpc-decoder")
            if not lut or not qldpc:
                continue
            speed_ratio = float(qldpc["syndromes_per_second"]) / float(lut["syndromes_per_second"])
            lut_rate = decoder_rate(lut)
            qldpc_rate = decoder_rate(qldpc)
            rate_text = "undefined"
            if lut_rate:
                rate_text = f"{qldpc_rate / lut_rate:.2f}x the LUT logical error rate"
            lines.append(
                f"- d={distance}: QLDPC ran at {speed_ratio:.2f}x the LUT throughput "
                f"with {rate_text} on the same sampled workload."
            )
        lines.append("")

    output = output_dir / "SUMMARY.md"
    output.write_text("\n".join(lines))
    print(f"Wrote {output}")
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", default=str(PROJECT / "results"))
    parser.add_argument("--output-dir", default=str(PROJECT / "results"))
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = read_csv_rows(results_dir)
    if not rows:
        sys.exit(f"FAIL: no CSV files found in {results_dir}")

    try:
        import matplotlib.pyplot as plt
    except ImportError:
        sys.exit("FAIL: install matplotlib with: python -m pip install -r requirements.txt")

    outputs = [
        plot_steane(plt, rows, output_dir),
        plot_cpu_gpu_speedup(plt, rows, output_dir),
        plot_decoder(plt, rows, output_dir),
        plot_decoder_accuracy(plt, rows, output_dir),
        plot_decoder_tradeoff(plt, rows, output_dir),
        write_summary(rows, output_dir),
    ]
    if not any(outputs):
        sys.exit("FAIL: no Steane or decoder benchmark rows found to plot")


if __name__ == "__main__":
    main()
