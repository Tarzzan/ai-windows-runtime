from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 75:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def _actions(band: str) -> list[str]:
    if band == "high":
        return ["Control efficiency is high: keep current governance cadence."]
    if band == "medium":
        return ["Control efficiency is medium: tighten blocking command turnaround."]
    return ["Control efficiency is low: reduce scope and increase validation discipline."]


def build_control_efficiency_report(
    *,
    execution_confidence_report: dict,
    execution_momentum_report: dict,
    validation_command_pack: dict,
) -> dict:
    conf_summary = execution_confidence_report.get("summary", {})
    momentum_summary = execution_momentum_report.get("summary", {})
    pack_summary = validation_command_pack.get("summary", {})

    confidence_score = int(conf_summary.get("confidence_score", 0))
    momentum_index = int(momentum_summary.get("momentum_index", 0))
    commands_total = int(pack_summary.get("commands_total", 0))
    blocking_commands = int(pack_summary.get("blocking_commands", 0))

    command_penalty = min(20, max(0, commands_total - 6) * 2)
    blocking_penalty = min(30, blocking_commands * 4)

    efficiency_score = max(0, min(100, int((confidence_score + momentum_index) / 2) - command_penalty - blocking_penalty))
    efficiency_band = _band(efficiency_score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "efficiency_score": efficiency_score,
            "efficiency_band": efficiency_band,
            "confidence_score": confidence_score,
            "momentum_index": momentum_index,
            "commands_total": commands_total,
            "blocking_commands": blocking_commands,
        },
        "factors": {
            "command_penalty": command_penalty,
            "blocking_penalty": blocking_penalty,
        },
        "actions": _actions(efficiency_band),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build control efficiency report")
    parser.add_argument("--execution-confidence-report", required=True, help="Execution confidence report path")
    parser.add_argument("--execution-momentum-report", required=True, help="Execution momentum report path")
    parser.add_argument("--validation-command-pack", required=True, help="Validation command pack path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_control_efficiency_report(
        execution_confidence_report=read_json(args.execution_confidence_report),
        execution_momentum_report=read_json(args.execution_momentum_report),
        validation_command_pack=read_json(args.validation_command_pack),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
