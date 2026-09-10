# instruction-sets

Versioned instruction-set specs for IR programs run under the
simplified Dally cost model. Each version is a self-contained spec
in its own directory

| Version | Ops                       | Covers                                                   |
|---------|---------------------------|----------------------------------------------------------|
| [`v0`](v0/) | `add`, `sub`, `mul`, `copy` | Straight-line dense linear algebra (matmul, convolution, stencil, FFT, basic Strassen). |
| [`v1`](v1/) | v0 + `and`, `or`, `not`, `xor` | Adds bitwise logic kernels (popcount, parity, bit-reverse, masking, XOR-based hashing). |
| [`v2`](v2/) | v1 + `set`                | Adds integer-immediate store; constants no longer require a caller-supplied cell. |
| [`v3`](v3/) | v2 + `div`, `cmp`, `select`, `abs` | Adds the primitives needed for Gaussian elimination with partial pivoting (LU). |

Profiles layered on top of an instruction-set version:

| Profile | Base | Adds | Status |
|---------|------|------|--------|
| [`tape-v0`](tape-v0/) | v3 | `external_tape_read` / `external_tape_write` tape I/O contract | **Proposal, pending discussion in [#2](https://github.com/cybertronai/simplified-dally-model/issues/2).** Reference submission: [`reference-submissions/matmul-tape/`](../reference-submissions/matmul-tape/). |

