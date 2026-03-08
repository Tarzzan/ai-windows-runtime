from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _corridor(throttle_mode: str, p0_count: int) -> str:
    if throttle_mode == "tight" or p0_count >= 3:
        return "p0_only"
    if throttle_mode == "balanced" or p0_count > 0:
        return "p0_p1"
    return "full"


def _actions(corridor: str) -> list[str]:
    if corridor == "p0_only":
        return ["Keep execution corridor to P0 only until stability improves."]
    if corridor == "p0_p1":
        return ["Run P0/P1 corridor and defer opportunistic backlog items."]
    return ["Full corridor enabled; include P2 backlog opportunistically."]


def build_priority_corridor_report(
    *, execution_throttle_report: dict, execution_focus_report: dict, risk_watchlist_report: dict
) -> dict:
    throttle_mode = str(execution_throttle_report.get("summary", {}).get("throttle_mode", "tight"))
    p0_focus = int(execution_focus_report.get("summary", {}).get("p0_focus_items", 0))
    p0_risks = int(risk_watchlist_report.get("summary", {}).get("p0_entries", 0))
    p0_count = max(p0_focus, p0_risks)

    corridor = _corridor(throttle_mode, p0_count)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "priority_corridor": corridor,
            "throttle_mode": throttle_mode,
            "p0_focus_items": p0_focus,
            "p0_risks": p0_risks,
        },
        "actions": _actions(corridor),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build priority corridor report")
    p.add_argument("--execution-throttle-report", required=True)
    p.add_argument("--execution-focus-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_priority_corridor_report(
        execution_throttle_report=read_json(a.execution_throttle_report),
        execution_focus_report=read_json(a.execution_focus_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
