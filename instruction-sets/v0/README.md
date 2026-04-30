# v0 — minimal instruction set: `add, sub, mul, copy`

The smallest instruction set able to express straight-line arithmetic
schedules under the simplified Dally model. Sufficient for dense
linear algebra (matmul, convolution, stencil, FFT, basic Strassen).
Not sufficient for divide/sqrt-bearing kernels (LU, Cholesky, QR,
layernorm), softmax (`exp`), or sorts (comparisons + branching).

## Notation

Three-address code, LLVM-flavored SSA. `%N` denotes the memory cell
at linear address `N` (the cell that sits at Manhattan distance
`⌈√N⌉` from the core).

A program is:

1. An **input placement line** listing the addresses where the caller
   has placed each input. Placement is free.
2. A sequence of **instructions**, one per line.
3. An **output line** listing the addresses to read at exit. Each
   exit read pays the standard read cost.

## Instructions

| Mnemonic | LLVM form              | Effect                       | Reads | Writes |
|----------|------------------------|------------------------------|------:|-------:|
| `add`    | `%d = add %a, %b`      | `mem[d] = mem[a] + mem[b]`   |   2   |   1    |
| `sub`    | `%d = sub %a, %b`      | `mem[d] = mem[a] - mem[b]`   |   2   |   1    |
| `mul`    | `%d = mul %a, %b`      | `mem[d] = mem[a] * mem[b]`   |   2   |   1    |
| `copy`   | `%d = copy %a`         | `mem[d] = mem[a]`            |   1   |   1    |

The destination cell `%d` may alias a source — read happens first,
then the write — so `%1 = add %1, %2` is the in-place accumulate
`mem[1] += mem[2]`.

`copy` is the explicit data-movement primitive. The model has no
implicit cache, so re-using a far cell cheaply requires copying it
into a near cell once and re-reading the near cell. Without `copy`,
scratchpad-style tiling is not expressible.

## Cost

* Each operand read costs `⌈√addr⌉`, the Manhattan distance from the
  core to the cell at linear address `addr`.
* Writes are free.
* Arithmetic is free.
* At program exit, every output address pays one standard read cost.

The **total program cost** is the sum of all read costs (operand
reads during the body + one read per output address at exit).

## Worked example: `myfunc(a, b, c, d, e) = a*b + c*d + e`

```
inputs:  %1, %2, %3, %4, %5     ; a@1, b@2, c@3, d@4, e@5

%1 = mul %1, %2                 ; t1 = a * b      -> addr 1
%2 = mul %3, %4                 ; t2 = c * d      -> addr 2
%1 = add %1, %2                 ; s  = t1 + t2    -> addr 1
%1 = add %1, %5                 ; r  = s  + e     -> addr 1

outputs: %1                     ; exit read cost = ⌈√1⌉ = 1
```

| step  | reads            | cost  |
|------:|------------------|------:|
|  1    | `%1`, `%2`       | 1 + 2 |
|  2    | `%3`, `%4`       | 2 + 2 |
|  3    | `%1`, `%2`       | 1 + 2 |
|  4    | `%1`, `%5`       | 1 + 3 |
|  exit | `%1`             | 1     |

Total: **15**.

## Compact wire encoding

For tools that consume IR as text (parsers, scorers, simulators),
drop the `%` and SSA syntactic sugar: list the input addresses on
line 1, one instruction per line in the form `op dest,src1,src2`,
and the output addresses on the last line.

```
1,2,3,4,5
mul 1,1,2
mul 2,3,4
add 1,1,2
add 1,5
1
```

Two-operand short form: `add d,s` is sugar for `add d,d,s` (in-place
accumulate). Same applies to `sub` and `mul`. `copy d,s` is always
2-operand.

`;` is also accepted as a line separator, so the same program inline
is `1,2,3,4,5;mul 1,1,2;mul 2,3,4;add 1,1,2;add 1,5;1`.

This wire encoding is what
[`cybertronai/sutro-problems/matmul`](https://github.com/cybertronai/sutro-problems/tree/main/matmul)
parses for the matmul-energy benchmark; in that scorer `copy` is
spelled `mov`.

## Out of scope (deferred to later versions)

* **Constants and immediates** — no `const`, no immediate operands.
  Programs that need a literal value derive it from the inputs (e.g.,
  initialize an accumulator with the first product rather than with
  a literal zero).
* **Control flow** — no branches, loops, or calls. Loops in the
  source are unrolled at IR-emission time; the IR is a straight-line
  tape.
* **Compare and select** — no `cmp`, `select`, `min`, `max`. Sorts
  and pivot selection require comparison; out of scope here.
* **Division and transcendentals** — no `div`, `sqrt`, `exp`, `log`,
  `sin`, `cos`. LU/Cholesky/QR/layernorm/softmax are out of scope.

These are exactly the extensions a `v1` instruction set would need to
cover the rest of a typical numerical-kernel benchmark suite.
