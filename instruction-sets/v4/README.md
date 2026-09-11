# v4 — v3 plus tape I/O: `recv, send`

Extends [v3](../v3/) with sequential input and output operations for
[Bill Dally's single core with tape](../../models/single-core-with-tape/).
All v3 operations and their effects are retained below. The selected
[model](../../models/) determines scratch layout and access costs;
this instruction-set version does not change the costs of earlier models.

## Notation

Three-address code with LLVM-flavored notation. `%N` denotes the memory
cell at linear address `N`, with the address-to-coordinate mapping supplied
by the selected model. `K` denotes an integer literal. For `cmp`, the
predicate is one of `eq, ne, lt, le, gt, ge`.

The short forms `recv d` and `send s` use destination and source cell
addresses, respectively. They are equivalent to `%d = recv` and `send %s`.
`recv` takes no scratch source operand; `send` has no scratch destination.

| Mnemonic | LLVM form | Effect |
|----------|-----------|--------|
| `add` | `%d = add %a, %b` | `mem[d] = mem[a] + mem[b]` |
| `sub` | `%d = sub %a, %b` | `mem[d] = mem[a] - mem[b]` |
| `mul` | `%d = mul %a, %b` | `mem[d] = mem[a] * mem[b]` |
| `div` | `%d = div %a, %b` | `mem[d] = mem[a] / mem[b]` |
| `copy` | `%d = copy %a` | `mem[d] = mem[a]` |
| `and` | `%d = and %a, %b` | `mem[d] = mem[a] & mem[b]` |
| `or` | `%d = or %a, %b` | `mem[d] = mem[a] \| mem[b]` |
| `xor` | `%d = xor %a, %b` | `mem[d] = mem[a] ^ mem[b]` |
| `not` | `%d = not %a` | `mem[d] = ~mem[a]` |
| `set` | `%d = set K` | `mem[d] = K` |
| `abs` | `%d = abs %a` | `mem[d] = \|mem[a]\|` |
| `cmp` | `%d = cmp %a, %b, <pred>` | `mem[d] = (mem[a] <pred> mem[b]) ? 1 : 0` |
| `select` | `%d = select %c, %t, %f` | `mem[d] = mem[c] ? mem[t] : mem[f]` |
| `recv` | `%d = recv` | Consume the next 32-bit input word and store it in `mem[d]`. |
| `send` | `send %s` | Append the 32-bit word from `mem[s]` to the output stream. |

## Tape semantics

The input tape is read-only and supplies a sequence of 32-bit words. Each
`recv d` consumes exactly one word, advances the input position once, and
writes that word to scratch cell `d`. Receiving past the supplied input is
invalid. Input words enter scratch through `recv` before other instructions
can use them.

The output tape is write-only and receives a sequence of 32-bit words. Each
`send s` reads scratch cell `s`, appends one word, and advances the output
position once. It leaves `mem[s]` unchanged. There are no tape seek,
rewind, input-write, or output-read operations.

## Costs under the single-core-with-tape model

The workload fixes the complete caller-supplied input stream and the
required output word stream. Every compared solution consumes the whole
input and produces the required output. Their tape I/O is therefore fixed
across solutions, so the model excludes `recv` and `send` from both the
energy and time score.

| Instruction | Physical scratch effect | Scored energy | Scored time |
|-------------|-------------------------|---------------|-------------|
| `recv d` | Write the next 32-bit input word to `d` | `0 fJ` | `0 ps` |
| `send s` | Read the full 32-bit word from `s` and append it to output | `0 fJ` | `0 ps` |

This accounting exclusion includes the scratch write performed by `recv`
and the scratch read performed by `send`. Both instructions are exempt
from the model's 50 fJ and 50 ps floors. Other instructions retain their
charged scratch reads and writes; see the
[model's cost rules](../../models/single-core-with-tape/).

The tapes do not provide scratch-to-scratch copying: the input is a fixed,
read-only stream, and output words cannot be read back. Their positions
advance sequentially according to the tape semantics above.

## Example

Suppose the next input word is `0x12345641`.

```text
recv 1       # mem[1] = 0x12345641; one scratch write
send 1       # append word 0x12345641; one full-word scratch read
```

The equivalent LLVM-flavored form is:

```text
%1 = recv
send %1
```

Together they consume one input word, produce the same word on the output
tape, and score `0 fJ` and `0 ps` under the single-core-with-tape model.
