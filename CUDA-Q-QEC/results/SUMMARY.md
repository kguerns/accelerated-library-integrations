# CUDA-Q QEC Result Summary

## Steane Code-Capacity Demo

| p | raw errors | decoded errors | raw rate | decoded rate |
| --- | ---: | ---: | ---: | ---: |
| 0.0010 | 2 | 0 | 0.002 | 0 |
| 0.0030 | 12 | 0 | 0.012 | 0 |
| 0.0100 | 31 | 4 | 0.031 | 0.004 |
| 0.0300 | 103 | 16 | 0.103 | 0.016 |
| 0.0500 | 122 | 32 | 0.122 | 0.032 |
| 0.1000 | 243 | 118 | 0.243 | 0.118 |

## Surface-Code Logical Error Results

| decoder | distance | rounds | p | shots | without decoding | with decoding |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nv-qldpc-decoder | 3 | 3 | 0.0010 | 1000 | 0.014 | 0.006 |
| nv-qldpc-decoder | 3 | 3 | 0.0030 | 1000 | 0.036 | 0.02 |
| nv-qldpc-decoder | 3 | 3 | 0.0050 | 1000 | 0.061 | 0.03 |
| nv-qldpc-decoder | 3 | 3 | 0.0100 | 1000 | 0.113 | 0.072 |
| nv-qldpc-decoder | 3 | 3 | 0.0300 | 1000 | 0.261 | 0.221 |
| nv-qldpc-decoder | 3 | 3 | 0.0500 | 1000 | 0.368 | 0.345 |
| nv-qldpc-decoder | 3 | 3 | 0.1000 | 1000 | 0.497 | 0.487 |
| nv-qldpc-decoder | 5 | 3 | 0.0010 | 1000 | 0.032 | 0.014 |
| nv-qldpc-decoder | 5 | 3 | 0.0030 | 1000 | 0.066 | 0.039 |
| nv-qldpc-decoder | 5 | 3 | 0.0050 | 1000 | 0.104 | 0.043 |
| nv-qldpc-decoder | 5 | 3 | 0.0100 | 1000 | 0.182 | 0.12 |
| nv-qldpc-decoder | 5 | 3 | 0.0300 | 1000 | 0.402 | 0.378 |
| nv-qldpc-decoder | 5 | 3 | 0.0500 | 1000 | 0.465 | 0.474 |
| nv-qldpc-decoder | 5 | 3 | 0.1000 | 1000 | 0.508 | 0.511 |
| nv-qldpc-decoder | 7 | 3 | 0.0010 | 1000 | 0.029 | 0.01 |
| nv-qldpc-decoder | 7 | 3 | 0.0030 | 1000 | 0.101 | 0.037 |
| nv-qldpc-decoder | 7 | 3 | 0.0050 | 1000 | 0.148 | 0.09 |
| nv-qldpc-decoder | 7 | 3 | 0.0100 | 1000 | 0.254 | 0.164 |
| nv-qldpc-decoder | 7 | 3 | 0.0300 | 1000 | 0.454 | 0.445 |
| nv-qldpc-decoder | 7 | 3 | 0.0500 | 1000 | 0.483 | 0.474 |
| nv-qldpc-decoder | 7 | 3 | 0.1000 | 1000 | 0.493 | 0.494 |
| single_error_lut | 3 | 3 | 0.0010 | 1000 | 0.015 | 0.004 |
| single_error_lut | 3 | 3 | 0.0030 | 1000 | 0.024 | 0.011 |
| single_error_lut | 3 | 3 | 0.0050 | 1000 | 0.066 | 0.032 |
| single_error_lut | 3 | 3 | 0.0100 | 1000 | 0.113 | 0.069 |
| single_error_lut | 3 | 3 | 0.0300 | 1000 | 0.294 | 0.249 |
| single_error_lut | 3 | 3 | 0.0500 | 1000 | 0.395 | 0.366 |
| single_error_lut | 3 | 3 | 0.1000 | 1000 | 0.47 | 0.459 |
| single_error_lut | 5 | 3 | 0.0010 | 1000 | 0.019 | 0.01 |
| single_error_lut | 5 | 3 | 0.0030 | 1000 | 0.056 | 0.04 |
| single_error_lut | 5 | 3 | 0.0050 | 1000 | 0.088 | 0.066 |
| single_error_lut | 5 | 3 | 0.0100 | 1000 | 0.172 | 0.158 |
| single_error_lut | 5 | 3 | 0.0300 | 1000 | 0.387 | 0.386 |
| single_error_lut | 5 | 3 | 0.0500 | 1000 | 0.478 | 0.478 |
| single_error_lut | 5 | 3 | 0.1000 | 1000 | 0.514 | 0.514 |
| single_error_lut | 7 | 3 | 0.0010 | 1000 | 0.028 | 0.013 |
| single_error_lut | 7 | 3 | 0.0030 | 1000 | 0.087 | 0.067 |
| single_error_lut | 7 | 3 | 0.0050 | 1000 | 0.134 | 0.128 |
| single_error_lut | 7 | 3 | 0.0100 | 1000 | 0.282 | 0.269 |
| single_error_lut | 7 | 3 | 0.0300 | 1000 | 0.423 | 0.423 |
| single_error_lut | 7 | 3 | 0.0500 | 1000 | 0.496 | 0.496 |
| single_error_lut | 7 | 3 | 0.1000 | 1000 | 0.525 | 0.525 |

## CPU vs GPU Syndrome Benchmark

| backend | median ms | syndromes/s | speedup vs CPU | scope |
| --- | ---: | ---: | ---: | --- |
| cpu_numpy | 343.945 | 290,744 | 1.00x | compute_only |
| gpu_cupy | 2.852 | 35,060,212 | 120.59x | compute_only |

## Decoder Benchmark Results

| variant | decoder | distance | median ms | decoded errors | decoded rate | speed vs LUT | rate vs LUT |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LUT | single_error_lut | 3 | 3.962 | 9/2000 | 0.0045 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 3 | 3.927 | 9/2000 | 0.0045 | 1.01x | 1.00x |
| BP=1 | nv-qldpc-decoder | 3 | 3.753 | 9/2000 | 0.0045 | 1.06x | 1.00x |
| LUT | single_error_lut | 5 | 10.826 | 39/2000 | 0.0195 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 5 | 17.679 | 27/2000 | 0.0135 | 0.61x | 0.69x |
| BP=1 | nv-qldpc-decoder | 5 | 14.078 | 25/2000 | 0.0125 | 0.77x | 0.64x |
| LUT | single_error_lut | 7 | 27.534 | 88/2000 | 0.044 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 7 | 49.569 | 32/2000 | 0.016 | 0.56x | 0.36x |
| BP=1 | nv-qldpc-decoder | 7 | 38.357 | 34/2000 | 0.017 | 0.72x | 0.39x |
| LUT | single_error_lut | 9 | 57.000 | 199/2000 | 0.0995 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 9 | 117.511 | 42/2000 | 0.021 | 0.49x | 0.21x |
| BP=1 | nv-qldpc-decoder | 9 | 85.331 | 46/2000 | 0.023 | 0.67x | 0.23x |

## Decoder Comparison Takeaway

- d=3, BP=0: 1.01x LUT throughput and 1.00x LUT logical error rate.
- d=3, BP=1: 1.06x LUT throughput and 1.00x LUT logical error rate.
- d=5, BP=0: 0.61x LUT throughput and 0.69x LUT logical error rate.
- d=5, BP=1: 0.77x LUT throughput and 0.64x LUT logical error rate.
- d=7, BP=0: 0.56x LUT throughput and 0.36x LUT logical error rate.
- d=7, BP=1: 0.72x LUT throughput and 0.39x LUT logical error rate.
- d=9, BP=0: 0.49x LUT throughput and 0.21x LUT logical error rate.
- d=9, BP=1: 0.67x LUT throughput and 0.23x LUT logical error rate.
