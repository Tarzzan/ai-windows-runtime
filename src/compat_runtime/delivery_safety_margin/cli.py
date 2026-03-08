from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 70:
        return "comfortable"
    if score >= 40:
        return "guarded"
    return "narrow"


def build_delivery_safety_margin_report(
    *, execution_stability_guard_report: dict, flow_control_budget_report: dict, capacity_buffer_report: dict
) -> dict:
    stability = execution_stability_guard_report.get("summary", {})
    flow = flow_control_budget_report.get("summary", {})
    buffer = capacity_buffer_report.get("summary", {})

    guard = str(stability.get("execution_stability_guard", "strict"))
    flow_score = int(flow.get("flow_control_score", 0))
    buffer_score = int(buffer.get("capacity_buffer_score", 0))

    guard_base = {"strict": 20, "elevated": 46, "normal": 72}.get(guard, 20)
    score = max(0, min(100, guard_base + (flow_score // 3) + (buffer_score // 4)))
    band = _band(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "safety_margin_score": score,
            "safety_margin_band": band,
            "execution_stability_guard": guard,
            "flow_control_score": flow_score,
            "capacity_buffer_score": buffer_score,
        },
        "actions": [
            "Protect delivery safety margin until stability guard relaxes."
            if band == "narrow"
            else "Track delivery safety margin before each intake decision."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build delivery safety margin report")
    p.add_argument("--execution-stability-guard-report", required=True)
    p.add_argument("--flow-control-budget-report", required=True)
    p.add_argument("--capacity-buffer-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_delivery_safety_margin_report(
        execution_stability_guard_report=read_json(a.execution_stability_guard_report),
        flow_control_budget_report=read_json(a.flow_control_budget_report),
        capacity_buffer_report=read_json(a.capacity_buffer_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
