from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_hotfix_planner_report(
    *, stability_window_report: dict, incident_feedback_report: dict, rollback_hints_report: dict
) -> dict:
    window_status = str(stability_window_report.get("summary", {}).get("window_status", "unstable"))
    feedback_summary = incident_feedback_report.get("summary", {})
    hints = rollback_hints_report.get("hints", [])

    priority = str(feedback_summary.get("feedback_priority", "P2"))
    plan_mode = "routine"
    if window_status == "unstable" or priority == "P0":
        plan_mode = "urgent"
    elif window_status == "watch" or priority == "P1":
        plan_mode = "accelerated"

    hotfix_items = []
    for hint in hints[:6]:
        hotfix_items.append(
            {
                "proposal_id": str(hint.get("proposal_id", "proposal")),
                "priority": priority,
                "rollback_level": str(hint.get("rollback_level", "minimal")),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "plan_mode": plan_mode,
            "window_status": window_status,
            "feedback_priority": priority,
            "hotfix_items": len(hotfix_items),
        },
        "items": hotfix_items,
        "actions": ["Execute hotfix plan according to plan_mode and rollback readiness."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build hotfix planner report")
    parser.add_argument("--stability-window-report", required=True, help="Stability window report")
    parser.add_argument("--incident-feedback-report", required=True, help="Incident feedback report")
    parser.add_argument("--rollback-hints-report", required=True, help="Rollback hints report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_hotfix_planner_report(
        stability_window_report=read_json(args.stability_window_report),
        incident_feedback_report=read_json(args.incident_feedback_report),
        rollback_hints_report=read_json(args.rollback_hints_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
