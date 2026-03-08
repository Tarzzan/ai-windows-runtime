from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _bootstrap_status(
    signoff_status: str, feedback_priority: str, lessons: int, release_policy_status: str
) -> str:
    if release_policy_status == "fail":
        return "blocked"
    if signoff_status == "approved" and feedback_priority in {"P1", "P2"}:
        return "ready"
    if lessons > 0:
        return "guarded"
    return "blocked"


def build_next_cycle_bootstrap_report(
    *,
    release_retrospective_report: dict,
    backlog_refresh_report: dict,
    validation_command_pack: dict,
    delivery_signoff_report: dict,
) -> dict:
    retro_summary = release_retrospective_report.get("summary", {})
    lessons = release_retrospective_report.get("lessons", [])
    backlog_summary = backlog_refresh_report.get("summary", {})

    signoff_status = str(delivery_signoff_report.get("status", "blocked"))
    feedback_priority = str(backlog_summary.get("feedback_priority", "P2"))
    release_policy_status = str(backlog_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(backlog_summary.get("release_policy_failures", 0))
    status = _bootstrap_status(signoff_status, feedback_priority, len(lessons), release_policy_status)

    commands = validation_command_pack.get("commands", [])

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "signoff_status": signoff_status,
            "feedback_priority": feedback_priority,
            "retrospective_trajectory": str(retro_summary.get("trajectory", "stable")),
            "refreshed_items": int(backlog_summary.get("refreshed_items", 0)),
            "bootstrap_commands": min(len(commands), 10),
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "commands": [str(row.get("command", "")) for row in commands[:10]],
        "actions": ["Initialize next iteration plan using refreshed backlog and retrospective lessons."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build next-cycle bootstrap report")
    parser.add_argument(
        "--release-retrospective-report", required=True, help="Release retrospective report"
    )
    parser.add_argument("--backlog-refresh-report", required=True, help="Backlog refresh report")
    parser.add_argument("--validation-command-pack", required=True, help="Validation command pack")
    parser.add_argument("--delivery-signoff-report", required=True, help="Delivery signoff report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_next_cycle_bootstrap_report(
        release_retrospective_report=read_json(args.release_retrospective_report),
        backlog_refresh_report=read_json(args.backlog_refresh_report),
        validation_command_pack=read_json(args.validation_command_pack),
        delivery_signoff_report=read_json(args.delivery_signoff_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
