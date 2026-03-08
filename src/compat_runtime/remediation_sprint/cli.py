from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _priority_rank(priority: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(priority, 0)


def _bucket(priority: str) -> str:
    if priority == "P0":
        return "sprint_now"
    if priority == "P1":
        return "sprint_next"
    return "backlog"


def _actions(now: int, next_count: int) -> list[str]:
    actions = []
    if now > 0:
        actions.append("Lock sprint_now scope and track daily burn on blocking items.")
    if next_count > 0:
        actions.append("Prepare sprint_next tasks with owner confirmation.")
    if not actions:
        actions.append("No remediation sprint task found. Validate input artifacts.")
    return actions


def build_remediation_sprint_report(
    *,
    ownership_assignment_report: dict,
    execution_burndown_report: dict,
    release_forecast_report: dict,
) -> dict:
    rows = []
    for task in ownership_assignment_report.get("tasks", []):
        priority = str(task.get("priority", "P2"))
        rows.append(
            {
                "id": str(task.get("id", "task")),
                "owner": str(task.get("owner", "unassigned")),
                "priority": priority,
                "bucket": _bucket(priority),
                "blocking": bool(task.get("blocking", False)),
                "objective": str(task.get("objective", "")),
                "suggested_command": str(task.get("suggested_command", "")),
            }
        )

    rows.sort(
        key=lambda row: (
            0 if row["bucket"] == "sprint_now" else (1 if row["bucket"] == "sprint_next" else 2),
            -_priority_rank(row["priority"]),
            row["id"],
        )
    )

    sprint_now = [row["id"] for row in rows if row["bucket"] == "sprint_now"]
    sprint_next = [row["id"] for row in rows if row["bucket"] == "sprint_next"]
    backlog = [row["id"] for row in rows if row["bucket"] == "backlog"]

    burndown_summary = execution_burndown_report.get("summary", {})
    forecast_summary = release_forecast_report.get("summary", {})
    ownership_summary = ownership_assignment_report.get("summary", {})
    release_policy_status = str(ownership_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(ownership_summary.get("release_policy_failures", 0))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "tasks_total": len(rows),
            "sprint_now_tasks": len(sprint_now),
            "sprint_next_tasks": len(sprint_next),
            "backlog_tasks": len(backlog),
            "iterations_to_clear_blockers": int(
                burndown_summary.get("iterations_to_clear_blockers", 0)
            ),
            "estimated_iterations_to_go": int(
                forecast_summary.get("estimated_iterations_to_go", 1)
            ),
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "tasks": rows,
        "buckets": {"sprint_now": sprint_now, "sprint_next": sprint_next, "backlog": backlog},
        "actions": _actions(len(sprint_now), len(sprint_next)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build remediation sprint report")
    parser.add_argument("--ownership-assignment-report", required=True, help="Ownership report path")
    parser.add_argument("--execution-burndown-report", required=True, help="Execution burndown report path")
    parser.add_argument("--release-forecast-report", required=True, help="Release forecast report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_remediation_sprint_report(
        ownership_assignment_report=read_json(args.ownership_assignment_report),
        execution_burndown_report=read_json(args.execution_burndown_report),
        release_forecast_report=read_json(args.release_forecast_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
