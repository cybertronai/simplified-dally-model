# v2 — v1 plus immediate store: `set`

Extends [`v1`](../v1/) with a single op that writes an integer
immediate into a memory cell. No read is performed, so the op
incurs no cost under the model.

Sufficient for kernels that need constants materialized in memory
(loop bounds, masks, accumulator init, lookup-table seeding) without
relying on a caller-supplied cell.

## Notation

Three-address code, LLVM-flavored SSA. `%N` denotes the memory cell
at linear address `N`. `K` denotes an integer literal.

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
| `set`    | `%d = set K`           | `mem[d] = K`                 |
