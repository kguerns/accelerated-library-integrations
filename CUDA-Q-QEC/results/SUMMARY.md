# CUDA-Q QEC Result Summary

## Steane Code-Capacity Demo

| p | raw errors | decoded errors | raw rate | decoded rate |
| --- | ---: | ---: | ---: | ---: |
| 0.0010 | 4 | 0 | 0.004 | 0 |
| 0.0030 | 11 | 0 | 0.011 | 0 |
| 0.0100 | 27 | 1 | 0.027 | 0.001 |
| 0.0300 | 91 | 21 | 0.091 | 0.021 |
| 0.0500 | 149 | 44 | 0.149 | 0.044 |
| 0.1000 | 275 | 137 | 0.275 | 0.137 |

## Surface-Code Logical Error Results

| decoder | distance | rounds | p | shots | without decoding | with decoding |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nv-qldpc-decoder | 3 | 3 | 0.0010 | 1000 | 0.01 | 0.001 |
| nv-qldpc-decoder | 3 | 3 | 0.0030 | 1000 | 0.031 | 0.018 |
| nv-qldpc-decoder | 3 | 3 | 0.0050 | 1000 | 0.056 | 0.034 |
| nv-qldpc-decoder | 3 | 3 | 0.0100 | 1000 | 0.132 | 0.08 |
| nv-qldpc-decoder | 3 | 3 | 0.0300 | 1000 | 0.28 | 0.212 |
| nv-qldpc-decoder | 3 | 3 | 0.0500 | 1000 | 0.363 | 0.337 |
| nv-qldpc-decoder | 3 | 3 | 0.1000 | 1000 | 0.486 | 0.476 |
| nv-qldpc-decoder | 5 | 3 | 0.0010 | 1000 | 0.016 | 0.009 |
| nv-qldpc-decoder | 5 | 3 | 0.0030 | 1000 | 0.068 | 0.03 |
| nv-qldpc-decoder | 5 | 3 | 0.0050 | 1000 | 0.101 | 0.063 |
| nv-qldpc-decoder | 5 | 3 | 0.0100 | 1000 | 0.215 | 0.145 |
| nv-qldpc-decoder | 5 | 3 | 0.0300 | 1000 | 0.384 | 0.375 |
| nv-qldpc-decoder | 5 | 3 | 0.0500 | 1000 | 0.466 | 0.473 |
| nv-qldpc-decoder | 5 | 3 | 0.1000 | 1000 | 0.515 | 0.513 |
| nv-qldpc-decoder | 7 | 3 | 0.0010 | 1000 | 0.038 | 0.01 |
| nv-qldpc-decoder | 7 | 3 | 0.0030 | 1000 | 0.096 | 0.045 |
| nv-qldpc-decoder | 7 | 3 | 0.0050 | 1000 | 0.145 | 0.081 |
| nv-qldpc-decoder | 7 | 3 | 0.0100 | 1000 | 0.262 | 0.149 |
| nv-qldpc-decoder | 7 | 3 | 0.0300 | 1000 | 0.471 | 0.429 |
| nv-qldpc-decoder | 7 | 3 | 0.0500 | 1000 | 0.49 | 0.496 |
| nv-qldpc-decoder | 7 | 3 | 0.1000 | 1000 | 0.495 | 0.496 |
| single_error_lut | 3 | 3 | 0.0010 | 1000 | 0.02 | 0.01 |
| single_error_lut | 3 | 3 | 0.0030 | 1000 | 0.034 | 0.018 |
| single_error_lut | 3 | 3 | 0.0050 | 1000 | 0.066 | 0.037 |
| single_error_lut | 3 | 3 | 0.0100 | 1000 | 0.113 | 0.071 |
| single_error_lut | 3 | 3 | 0.0300 | 1000 | 0.295 | 0.238 |
| single_error_lut | 3 | 3 | 0.0500 | 1000 | 0.349 | 0.336 |
| single_error_lut | 3 | 3 | 0.1000 | 1000 | 0.459 | 0.451 |
| single_error_lut | 5 | 3 | 0.0010 | 1000 | 0.019 | 0.015 |
| single_error_lut | 5 | 3 | 0.0030 | 1000 | 0.06 | 0.036 |
| single_error_lut | 5 | 3 | 0.0050 | 1000 | 0.099 | 0.081 |
| single_error_lut | 5 | 3 | 0.0100 | 1000 | 0.189 | 0.172 |
| single_error_lut | 5 | 3 | 0.0300 | 1000 | 0.388 | 0.39 |
| single_error_lut | 5 | 3 | 0.0500 | 1000 | 0.455 | 0.455 |
| single_error_lut | 5 | 3 | 0.1000 | 1000 | 0.504 | 0.504 |
| single_error_lut | 7 | 3 | 0.0010 | 1000 | 0.04 | 0.025 |
| single_error_lut | 7 | 3 | 0.0030 | 1000 | 0.094 | 0.063 |
| single_error_lut | 7 | 3 | 0.0050 | 1000 | 0.142 | 0.126 |
| single_error_lut | 7 | 3 | 0.0100 | 1000 | 0.256 | 0.258 |
| single_error_lut | 7 | 3 | 0.0300 | 1000 | 0.449 | 0.449 |
| single_error_lut | 7 | 3 | 0.0500 | 1000 | 0.488 | 0.488 |
| single_error_lut | 7 | 3 | 0.1000 | 1000 | 0.525 | 0.525 |

## CPU vs GPU Syndrome Benchmark

| backend | median ms | syndromes/s | speedup vs CPU | scope |
| --- | ---: | ---: | ---: | --- |
| cpu_numpy | 330.050 | 302,984 | 1.00x | compute_only |
| gpu_cupy | 2.873 | 34,803,285 | 114.87x | compute_only |

## Decoder Benchmark Results

| variant | decoder | distance | median ms | decoded errors | decoded rate | speed vs LUT | rate vs LUT |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LUT | single_error_lut | 3 | 3.775 | 9/2000 | 0.0045 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 3 | 4.014 | 9/2000 | 0.0045 | 0.94x | 1.00x |
| BP=1 | nv-qldpc-decoder | 3 | 3.909 | 9/2000 | 0.0045 | 0.97x | 1.00x |
| LUT | single_error_lut | 5 | 10.793 | 41/2000 | 0.0205 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 5 | 17.733 | 25/2000 | 0.0125 | 0.61x | 0.61x |
| BP=1 | nv-qldpc-decoder | 5 | 14.371 | 20/2000 | 0.01 | 0.75x | 0.49x |
| LUT | single_error_lut | 7 | 27.464 | 94/2000 | 0.047 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 7 | 49.685 | 20/2000 | 0.01 | 0.55x | 0.21x |
| BP=1 | nv-qldpc-decoder | 7 | 38.330 | 22/2000 | 0.011 | 0.72x | 0.23x |
| LUT | single_error_lut | 9 | 56.752 | 215/2000 | 0.1075 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 9 | 123.718 | 45/2000 | 0.0225 | 0.46x | 0.21x |
| BP=1 | nv-qldpc-decoder | 9 | 85.474 | 46/2000 | 0.023 | 0.66x | 0.21x |

## Decoder Comparison Takeaway

- d=3, BP=0: 0.94x LUT throughput and 1.00x LUT logical error rate.
- d=3, BP=1: 0.97x LUT throughput and 1.00x LUT logical error rate.
- d=5, BP=0: 0.61x LUT throughput and 0.61x LUT logical error rate.
- d=5, BP=1: 0.75x LUT throughput and 0.49x LUT logical error rate.
- d=7, BP=0: 0.55x LUT throughput and 0.21x LUT logical error rate.
- d=7, BP=1: 0.72x LUT throughput and 0.23x LUT logical error rate.
- d=9, BP=0: 0.46x LUT throughput and 0.21x LUT logical error rate.
- d=9, BP=1: 0.66x LUT throughput and 0.21x LUT logical error rate.
