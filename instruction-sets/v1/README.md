# v1 — v0 plus bitwise logic: `and, or, not, xor`

Extends [`v0`](../v0/) with bitwise logical operations.

Sufficient for bitwise kernels (popcount, parity, bit-reverse, masking),
XOR-based hashing/mixing, and boolean-mask predicates over packed words.

Not sufficient for divide/sqrt-bearing kernels (LU, Cholesky, QR, layernorm),
softmax (`exp`), or sorts (comparisons + branching).

## Notation

Three-address code, LLVM-flavored SSA. `%N` denotes the memory cell
at linear address `N`.

| Mnemonic | LLVM form              | Effect                       |
|----------|------------------------|------------------------------|
| `add`    | `%d = add %a, %b`      | `mem[d] = mem[a] + mem[b]`   |
| `sub`    | `%d = sub %a, %b`      | `mem[d] = mem[a] - mem[b]`   |
| `mul`    | `%d = mul %a, %b`      | `mem[d] = mem[a] * mem[b]`   |
| `copy`   | `%d = copy %a`         | `mem[d] = mem[a]`            |
| `and`    | `%d = and %a, %b`      | `mem[d] = mem[a] & mem[b]`   |
| `or`     | `%d = or %a, %b`       | `mem[d] = mem[a] \| mem[b]`  |
| `xor`    | `%d = xor %a, %b`      | `mem[d] = mem[a] ^ mem[b]`   |
| `not`    | `%d = not %a`          | `mem[d] = ~mem[a]`           |
