from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_readiness_delta_report(
    *, launch_readiness_report: dict, delivery_cockpit_report: dict, release_gate_history_report: dict
) -> dict:
    launch_summary = launch_readiness_report.get("summary", {})
    cockpit_summary = delivery_cockpit_report.get("summary", {})
    history_summary = release_gate_history_report.get("summary", {})

    delta = int(cockpit_summary.get("readiness_score", 0)) - int(
        history_summary.get("latest_readiness_score", 0)
    )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "launch_status": str(launch_readiness_report.get("status", "blocked")),
            "cockpit_status": str(cockpit_summary.get("cockpit_status", "at_risk")),
            "trajectory": str(history_summary.get("trajectory", "stable")),
            "readiness_score_delta": delta,
            "release_decision": str(launch_summary.get("release_decision", "no-go")),
        },
        "actions": ["Escalate when readiness_score_delta is negative and trajectory is degrading."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build readiness delta report")
    parser.add_argument("--launch-readiness-report", required=True, help="Launch readiness report")
    parser.add_argument("--delivery-cockpit-report", required=True, help="Delivery cockpit report")
    parser.add_argument("--release-gate-history-report", required=True, help="Release gate history report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_readiness_delta_report(
        launch_readiness_report=read_json(args.launch_readiness_report),
        delivery_cockpit_report=read_json(args.delivery_cockpit_report),
        release_gate_history_report=read_json(args.release_gate_history_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
