from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_stability_window_report(
    *, post_release_monitor_report: dict, release_gate_history_report: dict, readiness_delta_report: dict
) -> dict:
    monitor_summary = post_release_monitor_report.get("summary", {})
    history_summary = release_gate_history_report.get("summary", {})
    delta_summary = readiness_delta_report.get("summary", {})

    monitor_status = str(monitor_summary.get("monitor_status", "critical"))
    trajectory = str(history_summary.get("trajectory", "degrading"))
    delta = int(delta_summary.get("readiness_score_delta", 0))

    status = "unstable"
    if monitor_status == "stable" and trajectory in {"stable", "improving"} and delta >= 0:
        status = "stable"
    elif monitor_status == "watch" or trajectory == "stable":
        status = "watch"

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "window_status": status,
            "monitor_status": monitor_status,
            "trajectory": trajectory,
            "readiness_score_delta": delta,
        },
        "actions": ["Use this window status to decide hotfix urgency and cadence."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stability window report")
    parser.add_argument("--post-release-monitor-report", required=True, help="Post-release monitor report")
    parser.add_argument("--release-gate-history-report", required=True, help="Release gate history report")
    parser.add_argument("--readiness-delta-report", required=True, help="Readiness delta report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_stability_window_report(
        post_release_monitor_report=read_json(args.post_release_monitor_report),
        release_gate_history_report=read_json(args.release_gate_history_report),
        readiness_delta_report=read_json(args.readiness_delta_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
