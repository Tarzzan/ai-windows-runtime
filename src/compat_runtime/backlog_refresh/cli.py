from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_backlog_refresh_report(
    *, incident_feedback_report: dict, iteration_plan_report: dict, remediation_sprint_report: dict
) -> dict:
    feedback_summary = incident_feedback_report.get("summary", {})
    tasks = iteration_plan_report.get("tasks", [])
    sprint_summary = remediation_sprint_report.get("summary", {})

    priority = str(feedback_summary.get("feedback_priority", "P2"))
    release_policy_status = str(feedback_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(feedback_summary.get("release_policy_failures", 0))
    refreshed = []
    for task in tasks[:8]:
        refreshed.append(
            {
                "id": str(task.get("id", "task")),
                "priority": priority if bool(task.get("blocking", False)) else str(task.get("priority", "P2")),
                "objective": str(task.get("objective", "")),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "refreshed_items": len(refreshed),
            "feedback_priority": priority,
            "sprint_now_tasks": int(sprint_summary.get("sprint_now_tasks", 0)),
            "sprint_next_tasks": int(sprint_summary.get("sprint_next_tasks", 0)),
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "items": refreshed,
        "actions": ["Apply refreshed priorities when drafting next iteration plan."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build backlog refresh report")
    parser.add_argument("--incident-feedback-report", required=True, help="Incident feedback report path")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--remediation-sprint-report", required=True, help="Remediation sprint report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_backlog_refresh_report(
        incident_feedback_report=read_json(args.incident_feedback_report),
        iteration_plan_report=read_json(args.iteration_plan_report),
        remediation_sprint_report=read_json(args.remediation_sprint_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
