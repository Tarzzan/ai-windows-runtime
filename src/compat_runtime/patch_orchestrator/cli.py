from __future__ import annotations

import argparse

from compat_runtime.common.io import read_json, write_json


CATEGORY_PLAYBOOK = {
    "loader": ("P0", "Implement missing loader/import pathway", "high"),
    "com": ("P0", "Implement or stub required COM activation path", "high"),
    "installer": ("P0", "Instrument installer bootstrap handshake and add targeted shim", "high"),
    "network": ("P1", "Improve winhttp/protocol compatibility layer", "medium"),
    "sync": ("P1", "Harden synchronization object semantics and wait behavior", "medium"),
    "file": ("P1", "Expand file adapter semantics and handle/path behavior", "medium"),
    "registry": ("P1", "Expand registry adapter semantics and key/value behavior", "medium"),
    "unimplemented": ("P1", "Implement missing API stub with behavior tests", "medium"),
}


def proposal_from_gap(gap: dict) -> dict:
    category = gap.get("category", "runtime")
    priority, title, risk = CATEGORY_PLAYBOOK.get(
        category,
        ("P2", "Investigate runtime limitation and define fix", "medium"),
    )
    return {
        "gap_id": gap["id"],
        "priority": priority,
        "title": title,
        "risk": risk,
        "validation": "Add targeted reproduction test + regression scenario run",
    }


def build_patch_plan(gaps: dict) -> dict:
    proposals = [proposal_from_gap(g) for g in gaps.get("gaps", [])]
    return {"artifact_version": "1.0", "proposals": proposals}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build patch proposal plan from detected gaps")
    parser.add_argument("--gaps", required=True, help="Gaps JSON input")
    parser.add_argument("--output", required=True, help="Patch plan JSON output")
    args = parser.parse_args()

    gaps = read_json(args.gaps)
    plan = build_patch_plan(gaps)
    write_json(args.output, plan)


if __name__ == "__main__":
    main()
