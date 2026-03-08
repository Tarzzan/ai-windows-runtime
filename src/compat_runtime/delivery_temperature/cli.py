from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _temperature(index: int) -> str:
    if index >= 75:
        return "hot"
    if index >= 45:
        return "warm"
    return "cool"


def _actions(temperature: str) -> list[str]:
    if temperature == "hot":
        return ["Apply delivery cooling plan: reduce scope and shorten feedback loops."]
    if temperature == "warm":
        return ["Keep controlled cadence with daily blocker review."]
    return ["Sustain cadence and prepare selective acceleration candidates."]


def build_delivery_temperature_report(
    *,
    execution_pressure_report: dict,
    launch_readiness_report: dict,
    release_decision_report: dict,
) -> dict:
    pressure_summary = execution_pressure_report.get("summary", {})

    pressure_index = int(pressure_summary.get("pressure_index", 0))
    launch_status = str(launch_readiness_report.get("status", "blocked"))
    release_decision = str(release_decision_report.get("decision", "no-go"))

    launch_bonus = {"ready": -15, "limited": 5, "blocked": 15}.get(launch_status, 10)
    decision_bonus = {"go": -10, "hold": 8, "no-go": 18}.get(release_decision, 10)

    temperature_index = max(0, min(100, pressure_index + launch_bonus + decision_bonus))
    temperature = _temperature(temperature_index)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "temperature_index": temperature_index,
            "temperature": temperature,
            "pressure_index": pressure_index,
            "launch_status": launch_status,
            "release_decision": release_decision,
        },
        "factors": {
            "base_pressure_index": pressure_index,
            "launch_adjustment": launch_bonus,
            "decision_adjustment": decision_bonus,
        },
        "actions": _actions(temperature),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build delivery temperature report")
    parser.add_argument("--execution-pressure-report", required=True, help="Execution pressure report path")
    parser.add_argument("--launch-readiness-report", required=True, help="Launch readiness report path")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_delivery_temperature_report(
        execution_pressure_report=read_json(args.execution_pressure_report),
        launch_readiness_report=read_json(args.launch_readiness_report),
        release_decision_report=read_json(args.release_decision_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
