# CUDA-Q QEC Result Summary

## Steane Code-Capacity Demo

| p | raw errors | decoded errors | raw rate | decoded rate |
| --- | ---: | ---: | ---: | ---: |
| 0.0010 | 5 | 0 | 0.005 | 0 |
| 0.0030 | 10 | 0 | 0.01 | 0 |
| 0.0100 | 26 | 3 | 0.026 | 0.003 |
| 0.0300 | 77 | 22 | 0.077 | 0.022 |
| 0.0500 | 127 | 37 | 0.127 | 0.037 |
| 0.1000 | 257 | 117 | 0.257 | 0.117 |

## Surface-Code Logical Error Results

| decoder | distance | rounds | p | shots | without decoding | with decoding |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nv-qldpc-decoder | 3 | 3 | 0.0010 | 1000 | 0.011 | 0.003 |
| nv-qldpc-decoder | 3 | 3 | 0.0030 | 1000 | 0.039 | 0.023 |
| nv-qldpc-decoder | 3 | 3 | 0.0050 | 1000 | 0.069 | 0.032 |
| nv-qldpc-decoder | 3 | 3 | 0.0100 | 1000 | 0.133 | 0.079 |
| nv-qldpc-decoder | 3 | 3 | 0.0300 | 1000 | 0.288 | 0.234 |
| nv-qldpc-decoder | 3 | 3 | 0.0500 | 1000 | 0.354 | 0.337 |
| nv-qldpc-decoder | 3 | 3 | 0.1000 | 1000 | 0.465 | 0.481 |
| nv-qldpc-decoder | 5 | 3 | 0.0010 | 1000 | 0.023 | 0.006 |
| nv-qldpc-decoder | 5 | 3 | 0.0030 | 1000 | 0.065 | 0.035 |
| nv-qldpc-decoder | 5 | 3 | 0.0050 | 1000 | 0.119 | 0.054 |
| nv-qldpc-decoder | 5 | 3 | 0.0100 | 1000 | 0.194 | 0.138 |
| nv-qldpc-decoder | 5 | 3 | 0.0300 | 1000 | 0.382 | 0.346 |
| nv-qldpc-decoder | 5 | 3 | 0.0500 | 1000 | 0.478 | 0.453 |
| nv-qldpc-decoder | 5 | 3 | 0.1000 | 1000 | 0.521 | 0.52 |
| nv-qldpc-decoder | 7 | 3 | 0.0010 | 1000 | 0.031 | 0.015 |
| nv-qldpc-decoder | 7 | 3 | 0.0030 | 1000 | 0.089 | 0.046 |
| nv-qldpc-decoder | 7 | 3 | 0.0050 | 1000 | 0.153 | 0.081 |
| nv-qldpc-decoder | 7 | 3 | 0.0100 | 1000 | 0.259 | 0.164 |
| nv-qldpc-decoder | 7 | 3 | 0.0300 | 1000 | 0.442 | 0.439 |
| nv-qldpc-decoder | 7 | 3 | 0.0500 | 1000 | 0.464 | 0.467 |
| nv-qldpc-decoder | 7 | 3 | 0.1000 | 1000 | 0.494 | 0.493 |
| nv-qldpc-decoder | 9 | 3 | 0.0010 | 1000 | 0.043 | 0.013 |
| nv-qldpc-decoder | 9 | 3 | 0.0030 | 1000 | 0.123 | 0.065 |
| nv-qldpc-decoder | 9 | 3 | 0.0050 | 1000 | 0.165 | 0.107 |
| nv-qldpc-decoder | 9 | 3 | 0.0100 | 1000 | 0.302 | 0.216 |
| nv-qldpc-decoder | 9 | 3 | 0.0300 | 1000 | 0.467 | 0.461 |
| nv-qldpc-decoder | 9 | 3 | 0.0500 | 1000 | 0.495 | 0.494 |
| nv-qldpc-decoder | 9 | 3 | 0.1000 | 1000 | 0.507 | 0.506 |
| nv-qldpc-decoder | 11 | 3 | 0.0010 | 1000 | 0.054 | 0.021 |
| nv-qldpc-decoder | 11 | 3 | 0.0030 | 1000 | 0.143 | 0.068 |
| nv-qldpc-decoder | 11 | 3 | 0.0050 | 1000 | 0.24 | 0.138 |
| nv-qldpc-decoder | 11 | 3 | 0.0100 | 1000 | 0.329 | 0.233 |
| nv-qldpc-decoder | 11 | 3 | 0.0300 | 1000 | 0.496 | 0.479 |
| nv-qldpc-decoder | 11 | 3 | 0.0500 | 1000 | 0.477 | 0.478 |
| nv-qldpc-decoder | 11 | 3 | 0.1000 | 1000 | 0.491 | 0.484 |
| single_error_lut | 3 | 3 | 0.0010 | 1000 | 0.009 | 0.008 |
| single_error_lut | 3 | 3 | 0.0030 | 1000 | 0.046 | 0.028 |
| single_error_lut | 3 | 3 | 0.0050 | 1000 | 0.055 | 0.031 |
| single_error_lut | 3 | 3 | 0.0100 | 1000 | 0.113 | 0.07 |
| single_error_lut | 3 | 3 | 0.0300 | 1000 | 0.291 | 0.266 |
| single_error_lut | 3 | 3 | 0.0500 | 1000 | 0.365 | 0.335 |
| single_error_lut | 3 | 3 | 0.1000 | 1000 | 0.454 | 0.442 |
| single_error_lut | 5 | 3 | 0.0010 | 1000 | 0.025 | 0.01 |
| single_error_lut | 5 | 3 | 0.0030 | 1000 | 0.085 | 0.047 |
| single_error_lut | 5 | 3 | 0.0050 | 1000 | 0.094 | 0.075 |
| single_error_lut | 5 | 3 | 0.0100 | 1000 | 0.196 | 0.158 |
| single_error_lut | 5 | 3 | 0.0300 | 1000 | 0.382 | 0.382 |
| single_error_lut | 5 | 3 | 0.0500 | 1000 | 0.453 | 0.453 |
| single_error_lut | 5 | 3 | 0.1000 | 1000 | 0.476 | 0.476 |
| single_error_lut | 7 | 3 | 0.0010 | 1000 | 0.026 | 0.022 |
| single_error_lut | 7 | 3 | 0.0030 | 1000 | 0.098 | 0.08 |
| single_error_lut | 7 | 3 | 0.0050 | 1000 | 0.144 | 0.123 |
| single_error_lut | 7 | 3 | 0.0100 | 1000 | 0.241 | 0.232 |
| single_error_lut | 7 | 3 | 0.0300 | 1000 | 0.431 | 0.431 |
| single_error_lut | 7 | 3 | 0.0500 | 1000 | 0.53 | 0.53 |
| single_error_lut | 7 | 3 | 0.1000 | 1000 | 0.521 | 0.521 |
| single_error_lut | 9 | 3 | 0.0010 | 1000 | 0.047 | 0.029 |
| single_error_lut | 9 | 3 | 0.0030 | 1000 | 0.129 | 0.117 |
| single_error_lut | 9 | 3 | 0.0050 | 1000 | 0.179 | 0.172 |
| single_error_lut | 9 | 3 | 0.0100 | 1000 | 0.292 | 0.293 |
| single_error_lut | 9 | 3 | 0.0300 | 1000 | 0.458 | 0.458 |
| single_error_lut | 9 | 3 | 0.0500 | 1000 | 0.486 | 0.486 |
| single_error_lut | 9 | 3 | 0.1000 | 1000 | 0.5 | 0.5 |
| single_error_lut | 11 | 3 | 0.0010 | 1000 | 0.054 | 0.038 |
| single_error_lut | 11 | 3 | 0.0030 | 1000 | 0.155 | 0.148 |
| single_error_lut | 11 | 3 | 0.0050 | 1000 | 0.214 | 0.209 |
| single_error_lut | 11 | 3 | 0.0100 | 1000 | 0.362 | 0.362 |
| single_error_lut | 11 | 3 | 0.0300 | 1000 | 0.492 | 0.492 |
| single_error_lut | 11 | 3 | 0.0500 | 1000 | 0.498 | 0.498 |
| single_error_lut | 11 | 3 | 0.1000 | 1000 | 0.482 | 0.482 |

## CPU vs GPU Syndrome Benchmark

| backend | median ms | syndromes/s | speedup vs CPU | scope |
| --- | ---: | ---: | ---: | --- |
| cpu_numpy | 324.627 | 308,046 | 1.00x | compute_only |
| gpu_cupy | 2.900 | 34,484,637 | 111.95x | compute_only |

## Decoder Benchmark Results

| variant | decoder | distance | median ms | decoded errors | decoded rate | speed vs LUT | rate vs LUT |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LUT | single_error_lut | 7 | 27.459 | 81/2000 | 0.0405 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 7 | 48.864 | 28/2000 | 0.014 | 0.56x | 0.35x |

## Decoder Comparison Takeaway

- d=7, BP=0: 0.56x LUT throughput and 0.35x LUT logical error rate.
