# instruction-sets

Versioned instruction-set specs for IR programs. Each version is a
self-contained spec in its own directory. Instruction sets define what
operations do; the separately selected [model](../models/) defines their
layout and costs. A program or result should identify both its model and
instruction-set version.

Versions v0–v3 retain their existing operation semantics. Version v4 adds
the tape operations used by [Bill Dally's single core with tape](../models/single-core-with-tape/)
and the [spatial computer](../models/spatial-computer/).
The [simplified Bill Dally model](../models/simplified-bill-dally/) retains
its original function-call interface and read-distance costs;
adding v4 does not give it tape semantics or change its costs.

| Version | Ops                       | Covers                                                   |
|---------|---------------------------|----------------------------------------------------------|
| [`v0`](v0/) | `add`, `sub`, `mul`, `copy` | Straight-line dense linear algebra (matmul, convolution, stencil, FFT, basic Strassen). |
| [`v1`](v1/) | v0 + `and`, `or`, `not`, `xor` | Adds bitwise logic kernels (popcount, parity, bit-reverse, masking, XOR-based hashing). |
| [`v2`](v2/) | v1 + `set`                | Adds integer-immediate store; constants no longer require a caller-supplied cell. |
| [`v3`](v3/) | v2 + `div`, `cmp`, `select`, `abs` | Adds the primitives needed for Gaussian elimination with partial pivoting (LU). |
| [`v4`](v4/) | v3 + `recv`, `send` | Adds sequential 32-bit input/output tape operations. Model 2 excludes tape I/O from its scores; model 3 charges on-chip tape transport and scratch access. |
