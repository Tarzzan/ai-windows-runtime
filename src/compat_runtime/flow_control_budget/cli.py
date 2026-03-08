from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(score: int) -> str:
    if score >= 70:
        return "open"
    if score >= 40:
        return "managed"
    return "tight"


def build_flow_control_budget_report(
    *, scope_rebalance_report: dict, capacity_buffer_report: dict, execution_reserve_report: dict
) -> dict:
    rebalance = scope_rebalance_report.get("summary", {})
    buffer = capacity_buffer_report.get("summary", {})
    reserve = execution_reserve_report.get("summary", {})

    rebalance_mode = str(rebalance.get("scope_rebalance", "reduce"))
    buffer_score = int(buffer.get("capacity_buffer_score", 0))
    reserve_mode = str(reserve.get("execution_reserve", "protected"))

    rebalance_base = {"reduce": 20, "hold": 48, "expand": 76}.get(rebalance_mode, 20)
    reserve_bonus = {"protected": -12, "managed": 2, "surplus": 12}.get(reserve_mode, -12)
    score = max(0, min(100, rebalance_base + reserve_bonus + (buffer_score // 3)))
    mode = _mode(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "flow_control_score": score,
            "flow_control_mode": mode,
            "scope_rebalance": rebalance_mode,
            "capacity_buffer_score": buffer_score,
            "execution_reserve": reserve_mode,
        },
        "actions": [
            "Keep flow control budget tight until scope pressure eases."
            if mode == "tight"
            else "Review flow control budget each governance pass."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build flow control budget report")
    p.add_argument("--scope-rebalance-report", required=True)
    p.add_argument("--capacity-buffer-report", required=True)
    p.add_argument("--execution-reserve-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_flow_control_budget_report(
        scope_rebalance_report=read_json(a.scope_rebalance_report),
        capacity_buffer_report=read_json(a.capacity_buffer_report),
        execution_reserve_report=read_json(a.execution_reserve_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
