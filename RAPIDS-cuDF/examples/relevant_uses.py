"""pandas vs cuDF vs Dask-cuDF benchmark on real public data.

Downloads NYC TLC Yellow Taxi (~50MB), runs the same read -> filter ->
groupby -> top-N pipeline on each backend, and prints per-stage timings.
See ../README.md for context.
"""

import argparse
import os
import sys
import tempfile
import time
import urllib.request

URL = (
    "https://d37ci6vzurychx.cloudfront.net/trip-data/"
    "yellow_tripdata_2024-01.parquet"
)


def check_memory(file_size_mb, scale):
    """Bail if there isn't enough RAM for ~3 in-memory copies of the scaled data."""
    try:
        with open("/proc/meminfo") as f:
            avail_kb = next(int(l.split()[1]) for l in f if l.startswith("MemAvailable:"))
        avail_gb = avail_kb / 1024 / 1024
    except Exception:
        return

    needed_gb = (file_size_mb * 8 / 1024) * scale * 3 * 1.5
    if needed_gb > avail_gb:
        suggested = max(1, int(avail_gb / needed_gb * scale))
        sys.exit(
            f"FAIL: ~{needed_gb:.1f} GB needed at scale={scale}, "
            f"only ~{avail_gb:.1f} GB available. Try --scale {suggested}"
        )
    print(f"Memory: ~{needed_gb:.1f} GB needed / ~{avail_gb:.1f} GB available\n")


def benchmark(lib, path, sync, scale, lazy=False):
    """Run read -> filter -> groupby -> top-N. Returns ms per step."""
    times = {}

    if lazy:
        import dask
        import dask.dataframe as dd

        def go(x):
            with dask.config.set(scheduler="synchronous"):
                return x.persist()

        def replicate(df, n):
            return dd.concat([df] * n)
    else:
        def go(x):
            return x

        def replicate(df, n):
            return lib.concat([df] * n, ignore_index=True)

    # warm up the parquet reader -- cold start dominates the first read
    go(lib.read_parquet(path))
    sync()

    t0 = time.perf_counter()
    df = go(lib.read_parquet(path))
    sync()
    times["read"] = (time.perf_counter() - t0) * 1000

    big = go(replicate(df, scale))
    sync()

    t0 = time.perf_counter()
    over10 = go(big[big["fare_amount"] > 10])
    sync()
    times["filter"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    _ = go(over10.groupby("passenger_count").agg({
        "trip_distance": ["mean", "max"],
        "fare_amount":   ["mean", "sum"],
        "tip_amount":    "sum",
    }))
    sync()
    times["groupby"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    _ = go(over10.nlargest(100, "total_amount"))
    sync()
    times["top100"] = (time.perf_counter() - t0) * 1000

    return times


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scale", type=int, default=10,
                        help="replicate loaded data N times for post-read ops (default: 10)")
    args = parser.parse_args()

    try:
        import pandas as pd
        import cudf
        import cupy as cp
        import pyarrow.parquet as pq
    except ImportError as e:
        sys.exit(f"FAIL: missing dep -> {e}")

    try:
        import dask_cudf
        have_dask = True
    except ImportError:
        have_dask = False

    name = cp.cuda.runtime.getDeviceProperties(0)["name"].decode()
    bar = "=" * 60
    sub = "-" * 40

    tmp = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
    tmp.close()
    path = tmp.name

    try:
        print(f"Downloading {URL.split('/')[-1]} ...")
        urllib.request.urlretrieve(URL, path)
        file_size_mb = os.path.getsize(path) / 1e6
        print(f"  {file_size_mb:.1f} MB on disk\n")

        check_memory(file_size_mb, args.scale)

        n_base = pq.read_metadata(path).num_rows
        n_scaled = n_base * args.scale

        print(bar)
        print(f"GPU:     {name}")
        print(f"Dataset: NYC TLC Yellow Taxi 2024-01")
        print(f"         {n_base:,} rows, scaled {args.scale}x = {n_scaled:,} rows for ops")
        print(bar)
        print()

        # one-time GPU warmup so CUDA init isn't billed to anything
        cudf.Series([1, 2, 3]).sum()
        cp.cuda.runtime.deviceSynchronize()

        gpu_sync = cp.cuda.runtime.deviceSynchronize
        results = {
            "pandas": benchmark(pd, path, sync=lambda: None, scale=args.scale),
            "cuDF":   benchmark(cudf, path, sync=gpu_sync, scale=args.scale),
        }
        if have_dask:
            results["dask-cuDF"] = benchmark(
                dask_cudf, path, sync=gpu_sync, scale=args.scale, lazy=True
            )

        for step in results["pandas"]:
            print(f"[{step}]")
            print(sub)
            base = results["pandas"][step]
            for lib_name, t in results.items():
                ms = t[step]
                if lib_name == "pandas":
                    print(f"  {lib_name:<10} {ms:>8.1f} ms")
                else:
                    print(f"  {lib_name:<10} {ms:>8.1f} ms  ({base/ms:>5.1f}x vs pandas)")
            print()
    finally:
        if os.path.exists(path):
            os.remove(path)
            print(f"Cleaned up {path}")


if __name__ == "__main__":
    main()