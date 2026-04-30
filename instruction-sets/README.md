# instruction-sets

Versioned instruction-set specs for IR programs run under the
simplified Dally cost model. Each version is a self-contained spec
in its own directory; later versions strictly extend earlier ones.

| Version | Ops                       | Covers                                                   |
|---------|---------------------------|----------------------------------------------------------|
| [`v0`](v0/) | `add`, `sub`, `mul`, `copy` | Straight-line dense linear algebra (matmul, convolution, stencil, FFT, basic Strassen). |
