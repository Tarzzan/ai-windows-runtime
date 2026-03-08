from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_incident_feedback_report(
    *, post_release_monitor_report: dict, risk_watchlist_report: dict, hook_backlog_report: dict
) -> dict:
    monitor_summary = post_release_monitor_report.get("summary", {})
    risk_summary = risk_watchlist_report.get("summary", {})
    backlog_summary = hook_backlog_report.get("summary", {})

    priority = "P2"
    if str(monitor_summary.get("monitor_status", "stable")) == "critical":
        priority = "P0"
    elif str(monitor_summary.get("monitor_status", "stable")) == "watch":
        priority = "P1"

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "feedback_priority": priority,
            "monitor_status": str(monitor_summary.get("monitor_status", "stable")),
            "p0_risks": int(risk_summary.get("p0_entries", 0)),
            "high_urgency_hooks": int(backlog_summary.get("high_urgency", 0)),
            "release_policy_status": str(monitor_summary.get("release_policy_status", "missing")),
            "release_policy_failures": int(monitor_summary.get("release_policy_failures", 0)),
        },
        "feedback": [
            {
                "id": "post_release_signal",
                "priority": priority,
                "detail": "Consolidated post-release monitor and governance risk signal.",
            }
        ],
        "actions": ["Route incident feedback into backlog refresh before next cycle start."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build incident feedback report")
    parser.add_argument(
        "--post-release-monitor-report", required=True, help="Post-release monitor report path"
    )
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--hook-backlog-report", required=True, help="Hook backlog report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_incident_feedback_report(
        post_release_monitor_report=read_json(args.post_release_monitor_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        hook_backlog_report=read_json(args.hook_backlog_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
