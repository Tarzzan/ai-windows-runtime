from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_ops_runbook_report(
    *, rollout_guardrails_report: dict, validation_command_pack: dict, handoff_checklist_report: dict
) -> dict:
    stop_conditions = rollout_guardrails_report.get("stop_conditions", [])
    safeguards = rollout_guardrails_report.get("safeguards", [])
    commands = validation_command_pack.get("commands", [])
    failed_checks = int(handoff_checklist_report.get("summary", {}).get("checks_fail", 0))

    readiness = "operational" if len(commands) > 0 and failed_checks == 0 else "needs_attention"

    curated_commands = []
    for entry in commands[:6]:
        curated_commands.append(
            {
                "id": str(entry.get("id", entry.get("task_id", "command"))),
                "command": str(entry.get("command", "")),
                "priority": str(entry.get("priority", "P2")),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "runbook_readiness": readiness,
            "stop_conditions": len(stop_conditions),
            "safeguards": len(safeguards),
            "commands": len(curated_commands),
            "handoff_failed_checks": failed_checks,
        },
        "runbook": {
            "stop_conditions": stop_conditions,
            "safeguards": safeguards,
            "commands": curated_commands,
        },
        "actions": ["Validate runbook commands before each rollout wave."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ops runbook report")
    parser.add_argument("--rollout-guardrails-report", required=True, help="Rollout guardrails report")
    parser.add_argument("--validation-command-pack", required=True, help="Validation command pack")
    parser.add_argument("--handoff-checklist-report", required=True, help="Handoff checklist report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_ops_runbook_report(
        rollout_guardrails_report=read_json(args.rollout_guardrails_report),
        validation_command_pack=read_json(args.validation_command_pack),
        handoff_checklist_report=read_json(args.handoff_checklist_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
