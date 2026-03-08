from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(score: int) -> str:
    if score >= 70:
        return "narrow"
    if score >= 40:
        return "controlled"
    return "wide"


def build_delivery_bandwidth_report(
    *, queue_pressure_report: dict, cadence_recommendation_report: dict, owner_load_report: dict
) -> dict:
    pressure = queue_pressure_report.get("summary", {})
    cadence = cadence_recommendation_report.get("summary", {})
    owners = owner_load_report.get("summary", {})

    pressure_score = int(pressure.get("queue_pressure_score", 100))
    cadence_value = str(cadence.get("cadence", "slow"))
    overloaded = int(owners.get("overloaded_owners", 0))

    cadence_bias = {"slow": 20, "moderate": 8, "fast": -8}.get(cadence_value, 8)
    overload_bias = min(20, overloaded * 8)
    score = max(0, min(100, pressure_score + cadence_bias + overload_bias))
    mode = _mode(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "bandwidth_score": score,
            "bandwidth_mode": mode,
            "queue_pressure_score": pressure_score,
            "cadence": cadence_value,
            "overloaded_owners": overloaded,
        },
        "actions": [
            "Constrain delivery bandwidth until pressure decreases."
            if mode == "narrow"
            else "Keep current bandwidth mode and monitor owner throughput."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build delivery bandwidth report")
    p.add_argument("--queue-pressure-report", required=True)
    p.add_argument("--cadence-recommendation-report", required=True)
    p.add_argument("--owner-load-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_delivery_bandwidth_report(
        queue_pressure_report=read_json(a.queue_pressure_report),
        cadence_recommendation_report=read_json(a.cadence_recommendation_report),
        owner_load_report=read_json(a.owner_load_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
