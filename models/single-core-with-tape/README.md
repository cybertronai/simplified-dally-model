# Bill Dally's single core with tape

**Model 2.** Bill Dally's parallel explicit-communication grid model,
specialized to a single processor attached to a **read-only input tape** and a
**write-only output tape**. Scratch memory occupies a two-dimensional grid.
The score measures solution-dependent scratch access energy and time;
the common tape input/output work is excluded.

Use [instruction set v4](../../instruction-sets/v4/) for explicit tape I/O.
Every other instruction is charged for its scratch reads and writes.

## Machine and geometry

- One processor at `(x, y) = (0, 0)`.
- Scratch cells at integer coordinates `x ∈ [-16,000, 16,000]` and
  `y ∈ [1, 16,000]`.
- Each cell holds one **32-bit word**, on a grid with **1 µm** spacing.
- Communication follows Manhattan paths. A cell at `(x, y)` is
  `h = |x| + y` hops from the processor.
- Moving a 32-bit word one hop costs **1 fJ**. Average propagation speed is
  **c/120**, approximated as **0.4 ps per hop**; use 0.4 ps in accounting.

The coordinate bounds define the available scratch locations. There is no
separate area limit or total execution-time limit.

A run specifies a fixed, one-to-one placement of its allocated scratch
addresses at grid coordinates. Instruction operands such as `%d` refer to
these addresses; the address carried by a scratch request is 32 bits.
Moving data between scratch cells requires explicit instructions.
Use the declared coordinates to compute distance: `ceil(sqrt(address))`
from model 1 applies only if the run adopts that model's spiral placement.

## Scratch access costs

A scratch read sends a 32-bit address request and receives a 32-bit data
response: its distance terms are `2h` fJ and `0.8h` ps. A scratch write
sends the 32-bit address and 32-bit data together, with no acknowledgement
round trip: its distance terms are `2h` fJ and `0.4h` ps. The two words
double write energy but use the specified one-way propagation time.

Apply a **minimum of 50 fJ and 50 ps to each charged scratch access**:

| Access | Energy | Time |
|--------|--------|------|
| Read at distance `h` | `max(50, 2h)` fJ | `max(50, 0.8h)` ps |
| Write at distance `h` | `max(50, 2h)` fJ | `max(50, 0.4h)` ps |

The floors apply independently to energy and time, before accesses are
summed. A quantity below 50 becomes 50; a quantity at or above 50 is
unchanged. These are lower bounds, not rounding to multiples of 50 or
adding 50 to every distance term. `recv` and `send` are excluded from
scoring, including their scratch accesses, so neither floor applies to them.

The [Fable discussion](https://claude.ai/share/3783ff59-2510-4e4c-a63f-46ddaf783727)
motivates a register-file-scale baseline: even nearby word accesses require
address decoding, local data movement, and readout or capture. The shared
50 fJ / 50 ps floor is this model's simple approximation for those local
costs; distance determines the charge once its contribution exceeds the
floor.

## Instruction and solution costs

Every non-tape instruction touches scratch data and therefore has a
positive cost. For example, `add d,a,b` charges reads of `a` and `b` and a
write to `d`; `copy d,s` charges one read and one write; `set d,K` charges
only a write. With all accesses below the floors, these cost respectively
150 fJ / 150 ps, 100 fJ / 100 ps, and 50 fJ / 50 ps.

Source operands are read before the destination is overwritten, including
when their addresses coincide. Each listed source operand is charged;
`select` reads its condition and both value operands. Arithmetic instructions
are priced through these data accesses, with no additional arithmetic or
instruction-fetch charge.

For source-read distances `r₁, …, rₖ` and destination-write distances
`w₁, …, wₘ` in a non-tape instruction:

```text
energy_fJ = sum(max(50, 2r) for r in reads)
          + sum(max(50, 2w) for w in writes)
time_ps   = sum(max(50, 0.8r) for r in reads)
          + sum(max(50, 0.4w) for w in writes)
```

The single processor executes blocking accesses in instruction order,
without overlap. Sum the instruction charges to obtain the solution's
energy and time scores. These totals exclude tape I/O and therefore do
not represent full physical end-to-end energy or wall-clock time.

## Tape I/O

The input and output tapes attach to the processor. They advance
sequentially and cannot be sought or used as random-access scratch memory.
Scratch starts uninitialized; every source read must follow a write to that
cell. Input enters scratch through `recv`; output is produced by `send`.

```text
recv d    # next 32-bit input word appears in cell d; uncharged
send s    # append the 32-bit word in cell s to output; uncharged
```

Receiving advances the input tape by one word. Sending appends the full
32-bit source word and advances the output tape by one word. It leaves the
source cell unchanged. Neither instruction accesses a second scratch cell.
The input tape is never written and the output tape is never read.

Each workload fixes the input stream and required output stream. Every
compared solution consumes the entire input and produces the required
output. To focus the score on the solution's computation, **`recv` and
`send` each contribute 0 fJ and 0 ps**, including their associated scratch
write or read, regardless of the cell's distance. This is an accounting
exclusion of input/output work, not a claim that physical tape transfers
consume no energy or time.

There is no implicit final output read or additional tape-transport charge.
See [v4](../../instruction-sets/v4/) for the instruction semantics.

## Example

Place scratch addresses `1`, `2`, and `3` at `(3, 4)`, `(0, 1)`, and
`(0, 100)`, respectively: their distances are 7, 1, and 100 hops. With
input word `0x123456AB`:

```text
recv 1
set 2,1
add 1,1,2
copy 3,1
send 3
```

| Instruction | Result | Energy | Time |
|-------------|--------|--------|------|
| `recv 1` | Cell 1 contains `0x123456AB`; tape input excluded | 0 fJ | 0 ps |
| `set 2,1` | Cell 2 contains 1; one write at the floor | 50 fJ | 50 ps |
| `add 1,1,2` | Cell 1 contains `0x123456AC`; two reads and one write at the floors | 150 fJ | 150 ps |
| `copy 3,1` | Read cell 1, then write cell 3 | 250 fJ | 100 ps |
| `send 3` | Output contains word `0x123456AC`; tape output excluded | 0 fJ | 0 ps |
| **Total** | One input word consumed; one output word produced | **450 fJ** | **300 ps** |

For the copy, the read costs 50 fJ / 50 ps. The write at 100 hops costs
`max(50, 200) = 200` fJ and `max(50, 40) = 50` ps, illustrating that
energy can exceed its floor while time stays at its floor. At 1,000 hops,
a scratch read costs 2,000 fJ / 800 ps and a write costs 2,000 fJ / 400 ps.

[All models](../) · [Instruction sets](../../instruction-sets/)
