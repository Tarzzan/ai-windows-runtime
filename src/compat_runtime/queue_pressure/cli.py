from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def build_queue_pressure_report(
    *, owner_load_report: dict, execution_throttle_report: dict, priority_corridor_report: dict
) -> dict:
    owner_summary = owner_load_report.get("summary", {})
    throttle_summary = execution_throttle_report.get("summary", {})
    corridor_summary = priority_corridor_report.get("summary", {})

    overloaded = int(owner_summary.get("overloaded_owners", 0))
    throttle = str(throttle_summary.get("throttle_mode", "tight"))
    corridor = str(corridor_summary.get("priority_corridor", "p0_only"))

    throttle_penalty = {"tight": 35, "balanced": 20, "open": 5}.get(throttle, 20)
    corridor_penalty = {"p0_only": 30, "p0_p1": 18, "full": 4}.get(corridor, 18)
    overload_penalty = min(30, overloaded * 12)

    score = max(0, min(100, throttle_penalty + corridor_penalty + overload_penalty))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "queue_pressure_score": score,
            "queue_pressure_band": band,
            "overloaded_owners": overloaded,
            "throttle_mode": throttle,
            "priority_corridor": corridor,
        },
        "actions": [
            "Reduce queue pressure before expanding intake when score remains high."
            if band == "high"
            else "Maintain queue pressure controls with periodic review."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build queue pressure report")
    p.add_argument("--owner-load-report", required=True)
    p.add_argument("--execution-throttle-report", required=True)
    p.add_argument("--priority-corridor-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_queue_pressure_report(
        owner_load_report=read_json(a.owner_load_report),
        execution_throttle_report=read_json(a.execution_throttle_report),
        priority_corridor_report=read_json(a.priority_corridor_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
