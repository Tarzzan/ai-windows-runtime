from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _control_mode(temperature: str, confidence_band: str, policy_status: str) -> str:
    if policy_status != "pass":
        return "strict"
    if temperature == "hot" or confidence_band == "low":
        return "stabilize"
    if temperature == "cool" and confidence_band == "high":
        return "accelerate"
    return "controlled"


def _actions(mode: str) -> list[str]:
    if mode == "strict":
        return ["Enforce strict controls: freeze non-essential changes until policy gate is green."]
    if mode == "stabilize":
        return ["Prioritize stabilization controls on blockers and high-risk execution paths."]
    if mode == "accelerate":
        return ["Apply acceleration controls with unchanged validation bar."]
    return ["Maintain controlled delivery with explicit daily gate checks."]


def build_control_recommendation_report(
    *,
    delivery_temperature_report: dict,
    execution_confidence_report: dict,
    execution_pressure_report: dict,
    release_policy_report: dict,
) -> dict:
    temp_summary = delivery_temperature_report.get("summary", {})
    conf_summary = execution_confidence_report.get("summary", {})
    pressure_summary = execution_pressure_report.get("summary", {})

    temperature = str(temp_summary.get("temperature", "warm"))
    confidence_band = str(conf_summary.get("confidence_band", "low"))
    pressure_level = str(pressure_summary.get("pressure_level", "high"))
    policy_status = str(release_policy_report.get("status", "missing"))

    mode = _control_mode(temperature, confidence_band, policy_status)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "control_mode": mode,
            "temperature": temperature,
            "confidence_band": confidence_band,
            "pressure_level": pressure_level,
            "policy_status": policy_status,
        },
        "actions": _actions(mode),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build control recommendation report")
    parser.add_argument("--delivery-temperature-report", required=True, help="Delivery temperature report path")
    parser.add_argument("--execution-confidence-report", required=True, help="Execution confidence report path")
    parser.add_argument("--execution-pressure-report", required=True, help="Execution pressure report path")
    parser.add_argument("--release-policy-report", required=True, help="Release policy report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_control_recommendation_report(
        delivery_temperature_report=read_json(args.delivery_temperature_report),
        execution_confidence_report=read_json(args.execution_confidence_report),
        execution_pressure_report=read_json(args.execution_pressure_report),
        release_policy_report=read_json(args.release_policy_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
