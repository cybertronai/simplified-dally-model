# Bill Dally's single core with tape

**Model 2.** Bill Dally's parallel explicit-communication grid model,
specialized to a single processor attached to a **read-only input tape** and a
**write-only output tape**. Scratch memory occupies a two-dimensional grid;
communication is priced in energy and propagation time.

Unlike the [simplified Bill Dally model](../simplified-bill-dally/), both
scratch reads and scratch writes are charged. Use
[instruction set v4](../../instruction-sets/v4/) for explicit tape I/O.

## Machine and geometry

- One processor at `(x, y) = (0, 0)`.
- Scratch cells at integer coordinates `x ∈ [-16,000, 16,000]` and
  `y ∈ [1, 16,000]`.
- Each cell holds one **32-bit word**, on a grid with **1 µm** spacing.
- Communication follows Manhattan paths. A cell at `(x, y)` is
  `h = |x| + y` hops from the processor.
- Moving a 32-bit word one hop costs **1 fJ**. Average propagation speed is
  **c/120**, approximated as **0.4 ps per hop**; use 0.4 ps in accounting.

A run specifies a fixed, one-to-one placement of its allocated scratch
addresses at grid coordinates. Instruction operands such as `%d` refer to
these addresses; the address carried by a scratch request is 32 bits.
Scratch cannot be relocated without explicitly reading and writing it.
Use the declared coordinates to compute distance: `ceil(sqrt(address))`
from model 1 applies only if the run adopts that model's spiral placement.

## Scratch access costs

For a cell `h` hops from the processor:

| Access | Traffic | Energy | Propagation time |
|--------|---------|--------|------------------|
| Read | 32-bit address request, then 32-bit data response | `2h` fJ | `0.8h` ps |
| Write | 32-bit address plus 32-bit data request | `2h` fJ | `0.4h` ps |

A read makes a round trip. A write sends its address and data together in
one direction, with no acknowledgement round trip. The two words double
write energy, but do not double the specified one-way propagation time.

Each instruction charges its scratch source reads and destination write.
For example, `add d,a,b` charges reads of `a` and `b` and a write to `d`;
`copy d,s` charges one read and one write; `set d,K` charges only a write.
Source operands are read before the destination is overwritten, including
when their addresses coincide. Each listed source operand is charged;
`select` reads its condition and both value operands.

Accounting conventions: arithmetic itself has no additional energy or time
charge. The single processor executes blocking accesses in instruction
order, summing their energy and propagation times without overlap. There is
no additional processor clock, instruction-fetch, or tape-transport charge
in this model. These conventions define the baseline rather than inferring
unspecified hardware costs.

For source-read hops `r₁, …, rₖ` and destination-write hops `w₁, …, wₘ`:

```text
energy_fJ = 2 × (sum(r) + sum(w))
time_ps   = 0.8 × sum(r) + 0.4 × sum(w)
```

## Tape I/O

The input and output tapes attach to the processor. They advance
sequentially and cannot be sought or used as random-access scratch memory.
Scratch starts uninitialized; every source read must follow a write to that
cell. Input enters scratch through `recv`; output is produced by `send`.

```text
recv d    # next 32-bit input word appears in cell d; charge scratch write
send s    # append the byte in cell s to output; charge scratch read
```

Receiving advances the input tape by one word. Sending appends one byte
and advances the output tape by one byte. The byte convention is the **low
eight bits** of the source word; sending still reads and charges the whole
32-bit scratch word. Neither instruction accesses a second scratch cell.
The input tape is never written and the output tape is never read.

There is no preloaded-input exemption or implicit final output read in this
model: each input transfer and output transfer is explicit. Tape storage is
external to the scratch-area budget; only the associated scratch access is
charged here. See [v4](../../instruction-sets/v4/) for instruction semantics.

## Limits

| Resource | Limit |
|----------|-------|
| Scratch area | **256 mm²** |
| Total modeled execution time | **24 hours** (`86,400 s`, or `8.64 × 10¹⁶ ps`) |

**Area convention:** one allocated scratch site occupies 1 µm². Therefore,
the area limit permits at most **256,000,000 allocated 32-bit cells**
(1,024,000,000 bytes). Count all allocated sites, including temporarily
unused cells; reusing a site does not allocate another one. Tapes are
external, and separate processor/wire area costs are not specified.

The full coordinate envelope is about 32 mm × 16 mm, or **512 mm²**. The
256 mm² limit applies to the allocated scratch sites within that envelope,
not to allocating the entire rectangle. Both the coordinate bounds and the
area cap must hold. For example, the first 256,000,000 cells of model 1's
upper-half-plane spiral fit in a triangular region within these bounds.

A run that exceeds either the area limit or the sum of modeled access times
is outside this model's limits. Energy is the accumulated communication
cost; no separate energy limit is specified.

## Example

Place scratch address `1` at `(3, 4)`, seven hops from the processor. With
input word `0x123456AB`:

```text
recv 1
send 1
```

| Instruction | Result | Energy | Time |
|-------------|--------|--------|------|
| `recv 1` | Cell 1 contains `0x123456AB` | 14 fJ | 2.8 ps |
| `send 1` | Output contains byte `0xAB` | 14 fJ | 5.6 ps |
| **Total** | One input word consumed; one output byte produced | **28 fJ** | **8.4 ps** |

One scratch cell is allocated, occupying 1 µm² under the area convention.

[All models](../) · [Instruction sets](../../instruction-sets/)
