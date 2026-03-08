from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _actions(overloaded: int) -> list[str]:
    if overloaded > 0:
        return ["Redistribute overloaded owner queues before next execution cycle."]
    return ["Owner load is balanced; maintain current ownership allocation."]


def build_owner_load_report(*, ownership_assignment_report: dict) -> dict:
    tasks = ownership_assignment_report.get("tasks", [])
    c = Counter(str(t.get("owner", "unassigned")) for t in tasks)

    owners = []
    overloaded = 0
    for owner, count in sorted(c.items()):
        load_band = "high" if count >= 4 else "medium" if count >= 2 else "low"
        if load_band == "high":
            overloaded += 1
        owners.append({"owner": owner, "tasks": count, "load_band": load_band})

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "owners_total": len(owners),
            "overloaded_owners": overloaded,
            "tasks_total": len(tasks),
        },
        "owners": owners,
        "actions": _actions(overloaded),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build owner load report")
    p.add_argument("--ownership-assignment-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_owner_load_report(ownership_assignment_report=read_json(a.ownership_assignment_report))
    write_json(a.output, out)


if __name__ == "__main__":
    main()
