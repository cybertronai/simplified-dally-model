#!/usr/bin/env python3
"""Reference tape-driven matmul submission generator (tape-v0 proposal).

C = A x B over wrapping 8-bit cells. Parameterized N; emits:

  - a bounded, checkable SCHEDULE (JSON): named operands, static sizes,
    explicit tape events, straight-line ops. No runtime recursion, no
    search -- this is a hand-written reference, unrolled by construction.
  - the LOWERED IR text (executor form): tape reads lower to input
    placement, tape writes to declared outputs, per tape-v0.

Layout (row-major): A at cells [1, N^2], B at [N^2+1, 2N^2],
C at [2N^2+1, 3N^2], one shared product scratch cell at 3N^2+1.
Uses only v0 ops (mul, add): the k=0 product initializes C[i][j]
directly, so no `set`/constant cell is needed.

Usage: generate.py N [--out-dir DIR]
"""
import argparse
import json
import math
import os
import sys


def cell_cost(addr: int) -> int:
    return math.isqrt(addr - 1) + 1


def generate(n: int) -> dict:
    def a_cell(i, k):
        return 1 + i * n + k

    def b_cell(k, j):
        return n * n + 1 + k * n + j

    def c_cell(i, j):
        return 2 * n * n + 1 + i * n + j

    prod = 3 * n * n + 1

    tape_reads = []  # (dst_cell, name)
    for i in range(n):
        for k in range(n):
            tape_reads.append((a_cell(i, k), f"A[{i}][{k}]"))
    for k in range(n):
        for j in range(n):
            tape_reads.append((b_cell(k, j), f"B[{k}][{j}]"))

    ops = []  # dicts: {op, dst, srcs:[names]}
    for i in range(n):
        for j in range(n):
            for k in range(n):
                srcs = [f"A[{i}][{k}]", f"B[{k}][{j}]"]
                if k == 0:
                    ops.append({"op": "mul", "dst": f"C[{i}][{j}]", "srcs": srcs})
                else:
                    ops.append({"op": "mul", "dst": "PROD", "srcs": srcs})
                    ops.append(
                        {"op": "add", "dst": f"C[{i}][{j}]", "srcs": [f"C[{i}][{j}]", "PROD"]}
                    )

    name_to_cell = {}
    for cell, name in tape_reads:
        name_to_cell[name] = cell
    for i in range(n):
        for j in range(n):
            name_to_cell[f"C[{i}][{j}]"] = c_cell(i, j)
    name_to_cell["PROD"] = prod

    schedule = {
        "name": f"tape-matmul-{n}x{n}",
        "profile": "tape-v0 (proposal, pending #2)",
        "instruction_set": "v0 (mul, add only)",
        "semantics": "C = A x B over wrapping 8-bit cells; byte-exact vs signed 8-bit reference",
        "sizes": {"N": n, "inputs": 2 * n * n, "outputs": n * n, "ops": len(ops)},
        "operands": {name: name_to_cell[name] for name in sorted(name_to_cell)},
        "tape": {
            "read_events": [
                {"order": idx, "operand": name, "dst_cell": cell}
                for idx, (cell, name) in enumerate(tape_reads)
            ],
            "write_events": [
                {"order": i * n + j, "operand": f"C[{i}][{j}]", "src_cell": c_cell(i, j)}
                for i in range(n)
                for j in range(n)
            ],
        },
        "ops": ops,
    }
    return schedule


def lower_to_ir(schedule: dict) -> str:
    ops_by_name = {}
    for cell, name in [(e["dst_cell"], e["operand"]) for e in schedule["tape"]["read_events"]]:
        ops_by_name[name] = cell
    ops_by_name.update(schedule["operands"])
    lines = [",".join(str(e["dst_cell"]) for e in schedule["tape"]["read_events"])]
    for op in schedule["ops"]:
        lines.append(
            "{} {},{}".format(
                op["op"],
                ops_by_name[op["dst"]],
                ",".join(str(ops_by_name[s]) for s in op["srcs"]),
            )
        )
    lines.append(",".join(str(e["src_cell"]) for e in schedule["tape"]["write_events"]))
    return "\n".join(lines) + "\n"


def tape_cost_report(schedule: dict, t_read: int, t_write: int) -> dict:
    n = schedule["sizes"]["N"]
    opname = schedule["operands"]
    operand_reads = 0
    for op in schedule["ops"]:
        for s in op["srcs"]:
            operand_reads += cell_cost(opname[s])
    output_reads = sum(
        cell_cost(e["src_cell"]) for e in schedule["tape"]["write_events"]
    )
    n_in, n_out = schedule["sizes"]["inputs"], schedule["sizes"]["outputs"]
    return {
        "N": n,
        "events": {
            "operand_cell_reads": operand_reads,
            "legacy_output_reads": output_reads,
            "tape_read_bytes": n_in,
            "tape_write_bytes": n_out,
        },
        "charges": {
            "operand_reads (wire L1, in executor cost)": operand_reads,
            f"tape_in = {n_in} x T_read={t_read}": n_in * t_read,
            f"tape_out = {n_out} x T_write={t_write}": n_out * t_write,
            "variant_a_replace_total": operand_reads + n_in * t_read + n_out * t_write,
            "variant_b_stack_total": operand_reads
            + output_reads
            + n_in * t_read
            + n_out * t_write,
            "legacy_executor_static_cost (lowered form)": operand_reads + output_reads,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("n", type=int)
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args()
    n = args.n
    if n < 2 or n > 64:
        sys.exit("N must be in [2, 64] (reference range)")
    schedule = generate(n)
    tag = f"matmul_{n}x{n}"
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, f"{tag}.schedule.json"), "w") as f:
        json.dump(schedule, f, indent=1)
        f.write("\n")
    with open(os.path.join(args.out_dir, f"{tag}.ir"), "w") as f:
        f.write(lower_to_ir(schedule))
    print(json.dumps(tape_cost_report(schedule, 1, 1), indent=1))


if __name__ == "__main__":
    main()
