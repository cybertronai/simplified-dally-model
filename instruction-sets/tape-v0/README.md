# tape-v0: external tape-and-core contract

**Status: PROPOSAL, pending discussion in [#2](https://github.com/cybertronai/simplified-dally-model/issues/2).**
Nothing here is agreed yet. The reference submission in
[`reference-submissions/matmul-tape/`](../../reference-submissions/matmul-tape/)
exercises this contract exactly as proposed, so every open question below shows
up as a line item in its cost breakdown rather than being silently resolved.

- **Base instruction set:** [`v3`](../v3/) (the maximal current spec). The
  contract is defined against v3; a program that also avoids v1-v3 extensions
  is a plain v0 program under the tape profile (the reference matmul is).
- **Scope:** single core. One processor at the origin, one memory grid in the
  upper half-plane, one tape. Multi-core (point-to-point send/recv with
  positions) is a **different profile** and must be named and versioned
  separately; nothing in tape-v0 may assume it is the last word on I/O.

## New operations

| op | form | effect |
|----|------|--------|
| `external_tape_read` | `external_tape_read dst` | Consume the next unread input byte from the tape, write its value into cell `dst`. |
| `external_tape_write` | `external_tape_write src` | Append the current value of cell `src` to the tape's output stream. |

Spelling is deliberately distinct from the bare memory `read`/`copy` ops: a
tape fetch consumes an external item and has its own pricing and failure
rules; a cell read fetches a priced cell.

## Tape semantics (proposed)

- **Linear, byte-granular, no addresses, no geometry.** The tape is a pure I/O
  channel: two cursors (one input, one output) that advance one byte per
  operation. No seeking, no rewinding, no random access. Programs that want
  bit-packed formats pack bits themselves in cells.
- **Input-once.** Each input byte can be read exactly once, in order. There is
  no replay: a byte that has passed the input cursor is gone. Rationale: the
  cells inside the machine are the only reusable memory and they are priced by
  distance; a rereadable tape is unpriced external storage and bypasses the
  entire cost model.
- **Output-once.** Each output byte is appended once. There is no reading back
  what was written: the output cursor only moves forward, and it is not a
  source for `external_tape_read`.
- **Underflow** (input cursor past the end of the input stream): the
  submission is invalid. Rejected at validation time, not scored.
- **Overflow** (output side): the output stream is unbounded within a call, so
  there is no overflow condition; the charge per written byte is the limit.
  If a task wants an output cap, that is a task-level rule, not a tape rule.
- **Reset:** both cursors are positioned at the start of their streams at the
  beginning of a call and never reset within it. There is no mid-call reset.
- **Arity:** the number of `external_tape_read` operations in the (static,
  straight-line) program is exactly the input arity, and the order of the ops
  is the input order. This pins the input-arity ambiguity raised in
  [#3](https://github.com/cybertronai/simplified-dally-model/issues/3) for
  tape-profile programs: there is nothing to zip against, the program states
  its own arity.

## Event table and pricing (proposed)

Energy is the L1 (wire-length) model already used by the base cost model: a
transfer's charge is proportional to the L1 distance it travels.

| event | charge | notes |
|-------|-------:|-------|
| cell read (operand fetch) | `ceil(sqrt(addr))` | unchanged from base model: the L1 wire energy from cell to core. |
| cell write | 0 | unchanged. |
| arithmetic | 0 | unchanged. |
| legacy output extraction (read of a declared output cell) | `ceil(sqrt(addr))` | base-model rule; see open question below. |
| `external_tape_read` (per byte) | `T_read` | **proposed: 1** — a flat unit charge, the tape modeled as adjacent to the core (distance 1). |
| `external_tape_write` (per byte) | `T_write` | **proposed: 1** — same reasoning. |

`T_read`/`T_write` are proposal-pending constants, not decisions. The
reference submission reports its cost as a function of them.

### OPEN QUESTION (called out, not resolved): tape-write vs legacy output-read billing

The base model already charges one read of each declared output cell at exit
("the location of every output byte is specified by the caller, these incur
standard read cost"). Under the tape profile the final transfer out is an
`external_tape_write` with its own per-byte charge. Three readings exist:

- **(a) replace:** the tape-write charge *replaces* the legacy output-cell
  read (one charge per byte transferred, whichever rule covers it);
- **(b) stack:** both apply (output-cell read + tape-write byte charge);
- **(c) double-billing bug:** (b) is wrong and (a) is the only consistent
  reading, because it is the same physical transfer billed twice.

This contract does **not** pick one. The reference submission's cost breakdown
reports both (a) and (b) side by side so the numbers are on the table for the
#2 discussion. Whichever is chosen becomes a line in tape-v1.

## Executor delta (what tape-v0 requires that no executor has today)

Neither existing executor (the Python reference in
`sutro-problems/sparse-parity/mask_sparse_parity.py`, nor the Rust
`cybertronai/dally-eval`) implements the tape operations. That is the delta
this contract requires of them; it is deliberately a small one:

1. two new opcodes (`external_tape_read`, `external_tape_write`) with the
   cursor semantics above;
2. the flat per-byte charges `T_read`/`T_write` added to the static cost;
3. resolution of the billing open question above.

Until they land, a tape-profile submission is verified by running its
**lowered form** under the existing executors: `external_tape_read dst`
lowers to "the input byte lands in cell `dst`" (exactly the base model's
input-placement rule, same order), and `external_tape_write src` lowers to
"cell `src` is a declared output" (the output-read rule). The lowered form is
byte-exact under both executors today; the tape charges are then accounted
per the event table on top of the executor-reported cost. The reference
submission does exactly this and shows both ledgers.
