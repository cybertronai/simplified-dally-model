# v3 — v2 plus GE primitives: `div, cmp, select, abs`

Extends [`v2`](../v2/) with the operations needed to express
**Gaussian elimination with partial pivoting** as straight-line code:
a true division, a magnitude comparison, a branchless ternary, and
absolute value. The "Justification" column ties each op to its
Gaussian-elimination role.

Sufficient for LU / Gaussian elimination, Cholesky (`div` + `sqrt`
still missing), and any kernel that needs branchless conditional
data movement.

## Notation

Three-address code, LLVM-flavored SSA. `%N` denotes the memory cell
at linear address `N`. `K` denotes an integer literal. For `cmp`,
the predicate is one of `eq, ne, lt, le, gt, ge`.

| Mnemonic | LLVM form                  | Effect                                       | Justification                                                            |
|----------|----------------------------|----------------------------------------------|--------------------------------------------------------------------------|
| `add`    | `%d = add %a, %b`          | `mem[d] = mem[a] + mem[b]`                   | inherited from v0                                                        |
| `sub`    | `%d = sub %a, %b`          | `mem[d] = mem[a] - mem[b]`                   | row update: `row[i][j] -= factor * row[k][j]`                            |
| `mul`    | `%d = mul %a, %b`          | `mem[d] = mem[a] * mem[b]`                   | row update (multiply step of `factor * row[k][j]`)                       |
| `div`    | `%d = div %a, %b`          | `mem[d] = mem[a] / mem[b]`                   | elimination factor: `factor = row[i][k] / row[k][k]`                     |
| `copy`   | `%d = copy %a`             | `mem[d] = mem[a]`                            | explicit row swap (when not done by index remapping)                     |
| `and`    | `%d = and %a, %b`          | `mem[d] = mem[a] & mem[b]`                   | inherited from v1; not used in GE                                        |
| `or`     | `%d = or %a, %b`           | `mem[d] = mem[a] \| mem[b]`                  | inherited from v1; not used in GE                                        |
| `xor`    | `%d = xor %a, %b`          | `mem[d] = mem[a] ^ mem[b]`                   | inherited from v1; not used in GE                                        |
| `not`    | `%d = not %a`              | `mem[d] = ~mem[a]`                           | inherited from v1; not used in GE                                        |
| `set`    | `%d = set K`               | `mem[d] = K`                                 | inherited from v2; materializes loop-bound / sentinel constants          |
| `abs`    | `%d = abs %a`              | `mem[d] = \|mem[a]\|`                        | partial pivoting compares magnitudes                                     |
| `cmp`    | `%d = cmp %a, %b, <pred>`  | `mem[d] = (mem[a] <pred> mem[b]) ? 1 : 0`    | pivot selection: e.g. `cmp %d, %a, %b, gt` answers `\|a\| > \|b\|?`      |
| `select` | `%d = select %c, %t, %f`   | `mem[d] = mem[c] ? mem[t] : mem[f]`          | branchless pivot swap and conditional row update                         |
