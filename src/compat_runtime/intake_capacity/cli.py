from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(score: int) -> str:
    if score >= 70:
        return "expandable"
    if score >= 40:
        return "balanced"
    return "constrained"


def build_intake_capacity_report(
    *, intake_guard_report: dict, delivery_bandwidth_report: dict, queue_pressure_report: dict
) -> dict:
    guard = intake_guard_report.get("summary", {})
    bandwidth = delivery_bandwidth_report.get("summary", {})
    queue = queue_pressure_report.get("summary", {})

    intake_guard = str(guard.get("intake_guard", "strict"))
    bandwidth_mode = str(bandwidth.get("bandwidth_mode", "narrow"))
    queue_band = str(queue.get("queue_pressure_band", "high"))

    guard_base = {"strict": 28, "moderate": 58, "open": 84}.get(intake_guard, 28)
    bandwidth_penalty = {"narrow": 20, "controlled": 10, "wide": 0}.get(bandwidth_mode, 10)
    queue_penalty = {"high": 24, "medium": 12, "low": 0}.get(queue_band, 12)

    score = max(0, min(100, guard_base - bandwidth_penalty - queue_penalty + 16))
    mode = _mode(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "intake_capacity_score": score,
            "intake_capacity_mode": mode,
            "intake_guard": intake_guard,
            "bandwidth_mode": bandwidth_mode,
            "queue_pressure_band": queue_band,
        },
        "actions": [
            "Keep intake constrained until pressure and bandwidth improve."
            if mode == "constrained"
            else "Maintain intake capacity mode and review pressure drift each cycle."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build intake capacity report")
    p.add_argument("--intake-guard-report", required=True)
    p.add_argument("--delivery-bandwidth-report", required=True)
    p.add_argument("--queue-pressure-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_intake_capacity_report(
        intake_guard_report=read_json(a.intake_guard_report),
        delivery_bandwidth_report=read_json(a.delivery_bandwidth_report),
        queue_pressure_report=read_json(a.queue_pressure_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
