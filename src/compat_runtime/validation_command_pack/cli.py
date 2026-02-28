from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _priority_rank(priority: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(priority, 0)


def _suite_commands(test_impact_report: dict) -> dict[str, str]:
    commands: dict[str, str] = {}
    for suite in test_impact_report.get("suites", []):
        command = suite.get("suggested_command")
        if not isinstance(command, str) or not command:
            continue
        for gap_id in suite.get("trigger_proposals", []):
            if isinstance(gap_id, str):
                commands[gap_id] = command
        for category in suite.get("trigger_categories", []):
            if isinstance(category, str):
                commands[f"cat:{category}"] = command
    return commands


def build_validation_command_pack_report(
    *,
    iteration_plan_report: dict,
    test_impact_report: dict,
) -> dict:
    command_index = _suite_commands(test_impact_report)

    tasks = list(iteration_plan_report.get("tasks", []))
    tasks.sort(
        key=lambda row: (
            -_priority_rank(str(row.get("priority", "P2"))),
            0 if bool(row.get("blocking", False)) else 1,
            str(row.get("id", "")),
        )
    )

    command_rows = []
    seen_commands: set[str] = set()
    for task in tasks:
        objective = str(task.get("objective", ""))
        task_id = str(task.get("id", "task"))
        suggested = str(task.get("suggested_command", "scripts/run-full-pipeline.sh out"))

        # Prefer a command from test-impact mapping if discoverable from objective/category tokens.
        mapped = ""
        for key, command in command_index.items():
            if key.startswith("cat:") and key[4:] in objective.lower():
                mapped = command
                break
            if key in objective:
                mapped = command
                break
        command = mapped or suggested

        if command in seen_commands:
            continue
        seen_commands.add(command)
        command_rows.append(
            {
                "id": f"cmd-{len(command_rows) + 1}",
                "task_id": task_id,
                "priority": str(task.get("priority", "P2")),
                "blocking": bool(task.get("blocking", False)),
                "command": command,
                "reason": objective,
            }
        )

    blocking_ids = [row["id"] for row in command_rows if row["blocking"]]
    quick_ids = [row["id"] for row in command_rows[:3]]
    full_ids = [row["id"] for row in command_rows]

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "commands_total": len(command_rows),
            "blocking_commands": len(blocking_ids),
            "quick_pack_commands": len(quick_ids),
            "full_pack_commands": len(full_ids),
        },
        "commands": command_rows,
        "packs": {
            "quick": quick_ids,
            "blocking": blocking_ids,
            "full": full_ids,
        },
        "actions": [
            "Run blocking pack first, then quick pack for validation feedback loop.",
            "Use full pack before changing release decision status.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build validation command pack report")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--test-impact-report", required=True, help="Test impact report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_validation_command_pack_report(
        iteration_plan_report=read_json(args.iteration_plan_report),
        test_impact_report=read_json(args.test_impact_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
