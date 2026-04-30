# v0 — minimal instruction set: `add, sub, mul, copy`

The smallest instruction set able to express straight-line arithmetic.

Sufficient for dense linear algebra (matmul, convolution, stencil, FFT, basic Strassen).

Not sufficient for divide/sqrt-bearing kernels (LU, Cholesky, QR, layernorm), softmax (`exp`), or sorts (comparisons + branching).

## Notation

Three-address code, LLVM-flavored SSA. `%N` denotes the memory cell
at linear address `N`


| Mnemonic | LLVM form              | Effect                       | Reads | Writes |
|----------|------------------------|------------------------------|------:|-------:|
| `add`    | `%d = add %a, %b`      | `mem[d] = mem[a] + mem[b]`   |   2   |   1    |
| `sub`    | `%d = sub %a, %b`      | `mem[d] = mem[a] - mem[b]`   |   2   |   1    |
| `mul`    | `%d = mul %a, %b`      | `mem[d] = mem[a] * mem[b]`   |   2   |   1    |
| `copy`   | `%d = copy %a`         | `mem[d] = mem[a]`            |   1   |   1    |
