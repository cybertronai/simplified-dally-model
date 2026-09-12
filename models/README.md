# Models

Machine-model specifications, each in its own directory. A model defines the
machine layout, access costs, input/output interface, and coordinate bounds.
An [instruction-set version](../instruction-sets/) defines
the available operations. Choose both when describing or evaluating a program.

| Model | Specification | Status |
|-------|---------------|--------|
| 1. Simplified Bill Dally model | [Single processor with caller-placed inputs and outputs](simplified-bill-dally/); distance-priced reads, free writes, and no additional arithmetic charge. | Existing model; supports v0–v3 and the non-tape operations in v4. |
| 2. Bill Dally's single core with tape | [Single processor on a grid of 32-bit words with read-only input and write-only output tapes](single-core-with-tape/); scratch energy and time scores, with a 50 fJ and 50 ps minimum per charged scratch access; tape I/O is uncharged. | Supports v4 streaming through `recv` and `send`; fixed coordinate bounds, with no area or total-time cap. |
| 3. Spatial computer (pitch 128) | [Processor mesh with 48 KiB of local 32-bit scratch per processor and bottom-edge tapes](spatial-computer/). | Specified with v4, concurrent execution, distance-priced energy, and one-word-per-cycle links; on-chip tape I/O is charged. |

Tape instructions require model 2 or 3. Model 1 retains its original function-call
semantics and unitless distance costs; selecting a newer instruction set does
not change those costs or add a tape interface.
