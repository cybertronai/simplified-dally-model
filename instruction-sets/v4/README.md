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
| `send` | `send %s` | Append the byte from `mem[s]` to the output stream. |

## Tape semantics

The input tape is read-only and supplies a sequence of 32-bit words. Each
`recv d` consumes exactly one word, advances the input position once, and
writes that word to scratch cell `d`. Receiving past the supplied input is
invalid. Input words enter scratch through `recv` before other instructions
can use them.

The output tape is write-only and receives a sequence of bytes. Each
`send s` reads scratch cell `s`, appends one byte, and advances the output
position once. It leaves `mem[s]` unchanged. There are no tape seek,
rewind, input-write, or output-read operations.

**Byte-selection convention:** `send` emits the low eight bits of the
32-bit source word, `mem[s] & 0xff`.

## Costs under the single-core-with-tape model

For a scratch cell at `(x, y)`, let `r = |x| + y` be its Manhattan distance
from the processor in 1 μm hops.

| Instruction | Charged scratch access | Energy | Time |
|-------------|------------------------|--------|------|
| `recv d` | One write to `d`: 32-bit address + 32-bit data | `2r_d` fJ | `0.4r_d` ps |
| `send s` | One read from `s`: 32-bit address request + 32-bit data response | `2r_s` fJ | `0.8r_s` ps |

`send` pays for a full 32-bit scratch read even though it emits one byte.
`recv` pays for the destination write, without a scratch source read.
No independent tape-transport energy or latency is specified; the above
charges account for their scratch accesses. These costs belong to the
single-core-with-tape model, whose serialized timing adds the access times.

## Example

Suppose scratch cell `1` is at `(2, 1)`, so its distance is three hops,
and the next input word is `0x12345641`.

```text
recv 1       # mem[1] = 0x12345641; one scratch write
send 1       # append byte 0x41; one full-word scratch read
```

The equivalent LLVM-flavored form is:

```text
%1 = recv
send %1
```

The receive costs `6 fJ` and `1.2 ps`; the send costs `6 fJ` and `2.4 ps`.
Together they consume one input word, produce one output byte, and charge
`12 fJ` and `3.6 ps` under the single-core-with-tape model.
