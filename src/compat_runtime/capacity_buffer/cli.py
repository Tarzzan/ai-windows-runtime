from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _buffer(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def build_capacity_buffer_report(
    *, execution_reserve_report: dict, owner_load_report: dict, backlog_refresh_report: dict
) -> dict:
    reserve = execution_reserve_report.get("summary", {})
    owners = owner_load_report.get("summary", {})
    backlog = backlog_refresh_report.get("summary", {})

    reserve_mode = str(reserve.get("execution_reserve", "protected"))
    overloaded = int(owners.get("overloaded_owners", 0))
    refreshed_items = int(backlog.get("refreshed_items", 0))

    reserve_base = {"protected": 25, "managed": 55, "surplus": 82}.get(reserve_mode, 25)
    overload_penalty = min(30, overloaded * 12)
    backlog_penalty = min(20, max(0, refreshed_items - 4) * 3)

    score = max(0, min(100, reserve_base - overload_penalty - backlog_penalty + 18))
    buffer_band = _buffer(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "capacity_buffer_score": score,
            "capacity_buffer_band": buffer_band,
            "execution_reserve": reserve_mode,
            "overloaded_owners": overloaded,
            "refreshed_items": refreshed_items,
        },
        "actions": [
            "Protect capacity buffer until overload pressure decreases."
            if buffer_band == "low"
            else "Track capacity buffer trend at each planning cycle."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build capacity buffer report")
    p.add_argument("--execution-reserve-report", required=True)
    p.add_argument("--owner-load-report", required=True)
    p.add_argument("--backlog-refresh-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_capacity_buffer_report(
        execution_reserve_report=read_json(a.execution_reserve_report),
        owner_load_report=read_json(a.owner_load_report),
        backlog_refresh_report=read_json(a.backlog_refresh_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
