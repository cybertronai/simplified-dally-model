# Models

Machine-model specifications, each in its own directory. A model defines the
machine layout, communication costs, input/output interface, and applicable
resource limits. An [instruction-set version](../instruction-sets/) defines
the available operations. Choose both when describing or evaluating a program.

| Model | Specification | Status |
|-------|---------------|--------|
| 1. Simplified Bill Dally model | [Single processor with caller-placed inputs and outputs](simplified-bill-dally/); distance-priced reads, free writes and arithmetic. | Existing model; supports v0–v3 and the non-tape operations in v4. |
| 2. Bill Dally's single core with tape | [Single processor on a grid of 32-bit words with read-only input and write-only output tapes](single-core-with-tape/); physical communication energy and latency, with area and time limits. | Supports v4 streaming through `recv` and `send`. |
| 3. Spatial computer (processor at every interval) | [Placeholder](spatial-computer/). | Unspecified; cannot be run or scored. |

Tape instructions require model 2. Model 1 retains its original function-call
semantics and unitless distance costs; selecting a newer instruction set does
not change those costs or add a tape interface.
