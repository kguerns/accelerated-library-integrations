# CUDA-Q QEC Result Summary

## Steane Code-Capacity Demo

| p | raw errors | decoded errors | raw rate | decoded rate |
| --- | ---: | ---: | ---: | ---: |
| 0.0010 | 4 | 0 | 0.004 | 0 |
| 0.0030 | 13 | 0 | 0.013 | 0 |
| 0.0100 | 30 | 4 | 0.03 | 0.004 |
| 0.0300 | 84 | 28 | 0.084 | 0.028 |
| 0.0500 | 126 | 33 | 0.126 | 0.033 |
| 0.1000 | 248 | 127 | 0.248 | 0.127 |

## Surface-Code Sweep

This threshold-style sweep uses rounds=d, lower physical error rates, and more shots than the quick fixed-round demo.

It still may not match published threshold plots exactly because decoder choice, noise model, and shot count all affect the trend.

| decoder | distance | rounds | p | shots | without decoding | with decoding |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nv-qldpc-decoder | 3 | 3 | 0.0005 | 10000 | 0.0064 | 0.004 |
| nv-qldpc-decoder | 3 | 3 | 0.0010 | 10000 | 0.0126 | 0.0058 |
| nv-qldpc-decoder | 3 | 3 | 0.0020 | 10000 | 0.0238 | 0.0116 |
| nv-qldpc-decoder | 3 | 3 | 0.0030 | 10000 | 0.0374 | 0.0196 |
| nv-qldpc-decoder | 3 | 3 | 0.0050 | 10000 | 0.0598 | 0.0318 |
| nv-qldpc-decoder | 3 | 3 | 0.0070 | 10000 | 0.0808 | 0.0493 |
| nv-qldpc-decoder | 3 | 3 | 0.0100 | 10000 | 0.1133 | 0.0686 |
| nv-qldpc-decoder | 5 | 5 | 0.0005 | 10000 | 0.0205 | 0.0047 |
| nv-qldpc-decoder | 5 | 5 | 0.0010 | 10000 | 0.0393 | 0.011 |
| nv-qldpc-decoder | 5 | 5 | 0.0020 | 10000 | 0.0761 | 0.0237 |
| nv-qldpc-decoder | 5 | 5 | 0.0030 | 10000 | 0.1068 | 0.0366 |
| nv-qldpc-decoder | 5 | 5 | 0.0050 | 10000 | 0.1687 | 0.0736 |
| nv-qldpc-decoder | 5 | 5 | 0.0070 | 10000 | 0.2169 | 0.1107 |
| nv-qldpc-decoder | 5 | 5 | 0.0100 | 10000 | 0.2782 | 0.1718 |
| nv-qldpc-decoder | 7 | 7 | 0.0005 | 10000 | 0.0417 | 0.0083 |
| nv-qldpc-decoder | 7 | 7 | 0.0010 | 10000 | 0.0733 | 0.0131 |
| nv-qldpc-decoder | 7 | 7 | 0.0020 | 10000 | 0.1398 | 0.0327 |
| nv-qldpc-decoder | 7 | 7 | 0.0030 | 10000 | 0.1992 | 0.0584 |
| nv-qldpc-decoder | 7 | 7 | 0.0050 | 10000 | 0.2789 | 0.1141 |
| nv-qldpc-decoder | 7 | 7 | 0.0070 | 10000 | 0.3451 | 0.1806 |
| nv-qldpc-decoder | 7 | 7 | 0.0100 | 10000 | 0.4009 | 0.2746 |
| single_error_lut | 3 | 3 | 0.0005 | 10000 | 0.0072 | 0.0036 |
| single_error_lut | 3 | 3 | 0.0010 | 10000 | 0.0105 | 0.0061 |
| single_error_lut | 3 | 3 | 0.0020 | 10000 | 0.0245 | 0.0122 |
| single_error_lut | 3 | 3 | 0.0030 | 10000 | 0.0371 | 0.0205 |
| single_error_lut | 3 | 3 | 0.0050 | 10000 | 0.0596 | 0.0352 |
| single_error_lut | 3 | 3 | 0.0070 | 10000 | 0.0807 | 0.0488 |
| single_error_lut | 3 | 3 | 0.0100 | 10000 | 0.1133 | 0.0758 |
| single_error_lut | 5 | 5 | 0.0005 | 10000 | 0.0182 | 0.0062 |
| single_error_lut | 5 | 5 | 0.0010 | 10000 | 0.0376 | 0.0155 |
| single_error_lut | 5 | 5 | 0.0020 | 10000 | 0.0784 | 0.0404 |
| single_error_lut | 5 | 5 | 0.0030 | 10000 | 0.1114 | 0.0696 |
| single_error_lut | 5 | 5 | 0.0050 | 10000 | 0.1656 | 0.1281 |
| single_error_lut | 5 | 5 | 0.0070 | 10000 | 0.2093 | 0.1802 |
| single_error_lut | 5 | 5 | 0.0100 | 10000 | 0.2866 | 0.2646 |
| single_error_lut | 7 | 7 | 0.0005 | 10000 | 0.0423 | 0.0188 |
| single_error_lut | 7 | 7 | 0.0010 | 10000 | 0.0748 | 0.0456 |
| single_error_lut | 7 | 7 | 0.0020 | 10000 | 0.1424 | 0.1152 |
| single_error_lut | 7 | 7 | 0.0030 | 10000 | 0.1917 | 0.1765 |
| single_error_lut | 7 | 7 | 0.0050 | 10000 | 0.2861 | 0.2815 |
| single_error_lut | 7 | 7 | 0.0070 | 10000 | 0.3456 | 0.3446 |
| single_error_lut | 7 | 7 | 0.0100 | 10000 | 0.4069 | 0.4069 |

## CPU vs GPU Syndrome Benchmark

| backend | median ms | syndromes/s | speedup vs CPU | scope |
| --- | ---: | ---: | ---: | --- |
| cpu_numpy | 326.261 | 306,503 | 1.00x | compute_only |
| gpu_cupy | 2.853 | 35,052,753 | 114.36x | compute_only |

## Decoder Benchmark Results

| variant | decoder | distance | median ms | decoded errors | decoded rate | speed vs LUT | rate vs LUT |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| LUT | single_error_lut | 3 | 3.367 | 21/2000 | 0.0105 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 3 | 4.017 | 21/2000 | 0.0105 | 0.84x | 1.00x |
| LUT | single_error_lut | 5 | 10.575 | 35/2000 | 0.0175 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 5 | 17.709 | 23/2000 | 0.0115 | 0.60x | 0.66x |
| LUT | single_error_lut | 7 | 27.119 | 107/2000 | 0.0535 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 7 | 49.695 | 28/2000 | 0.014 | 0.55x | 0.26x |
| LUT | single_error_lut | 9 | 56.491 | 219/2000 | 0.1095 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 9 | 115.114 | 50/2000 | 0.025 | 0.49x | 0.23x |
| LUT | single_error_lut | 11 | 100.131 | 338/2000 | 0.169 | 1.00x | 1.00x |
| BP=0 | nv-qldpc-decoder | 11 | 242.138 | 43/2000 | 0.0215 | 0.41x | 0.13x |

## Decoder Comparison Takeaway

- d=3, BP=0: 0.84x LUT throughput and 1.00x LUT logical error rate.
- d=5, BP=0: 0.60x LUT throughput and 0.66x LUT logical error rate.
- d=7, BP=0: 0.55x LUT throughput and 0.26x LUT logical error rate.
- d=9, BP=0: 0.49x LUT throughput and 0.23x LUT logical error rate.
- d=11, BP=0: 0.41x LUT throughput and 0.13x LUT logical error rate.
