from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _cadence(friction_band: str, temperature: str, control_mode: str) -> str:
    if control_mode == "strict" or friction_band == "high" or temperature == "hot":
        return "slow"
    if friction_band == "medium" or temperature == "warm":
        return "moderate"
    return "fast"


def _actions(cadence: str) -> list[str]:
    if cadence == "slow":
        return ["Adopt slow cadence with blocker-first sequencing and strict gate checks."]
    if cadence == "moderate":
        return ["Keep moderate cadence and reassess friction each iteration."]
    return ["Use fast cadence while preserving mandatory validation checkpoints."]


def build_cadence_recommendation_report(
    *,
    governance_friction_report: dict,
    delivery_temperature_report: dict,
    control_recommendation_report: dict,
) -> dict:
    friction = governance_friction_report.get("summary", {})
    temp = delivery_temperature_report.get("summary", {})
    control = control_recommendation_report.get("summary", {})

    friction_band = str(friction.get("friction_band", "high"))
    friction_score = int(friction.get("friction_score", 100))
    temperature = str(temp.get("temperature", "hot"))
    control_mode = str(control.get("control_mode", "strict"))

    cadence = _cadence(friction_band, temperature, control_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "cadence": cadence,
            "friction_band": friction_band,
            "friction_score": friction_score,
            "temperature": temperature,
            "control_mode": control_mode,
        },
        "actions": _actions(cadence),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build cadence recommendation report")
    parser.add_argument("--governance-friction-report", required=True)
    parser.add_argument("--delivery-temperature-report", required=True)
    parser.add_argument("--control-recommendation-report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    artifact = build_cadence_recommendation_report(
        governance_friction_report=read_json(args.governance_friction_report),
        delivery_temperature_report=read_json(args.delivery_temperature_report),
        control_recommendation_report=read_json(args.control_recommendation_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
