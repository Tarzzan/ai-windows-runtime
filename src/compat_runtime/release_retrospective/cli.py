from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_release_retrospective_report(
    *, delivery_signoff_report: dict, readiness_delta_report: dict, release_gate_history_report: dict
) -> dict:
    signoff_summary = delivery_signoff_report.get("summary", {})
    signoff_status = str(delivery_signoff_report.get("status", "blocked"))
    release_policy_status = str(signoff_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(signoff_summary.get("release_policy_failures", 0))
    delta_summary = readiness_delta_report.get("summary", {})
    history_summary = release_gate_history_report.get("summary", {})

    lessons = []
    if signoff_status != "approved":
        lessons.append("Strengthen pre-signoff closure on blockers and dependencies.")
    if int(delta_summary.get("readiness_score_delta", 0)) < 0:
        lessons.append("Investigate readiness regressions between cycle checkpoints.")
    if str(history_summary.get("trajectory", "stable")) == "degrading":
        lessons.append("Tighten scope to stabilize gate trajectory before expansion.")
    if release_policy_status == "fail":
        lessons.append("Resolve release policy failures before opening the next release window.")
    if not lessons:
        lessons.append("Keep current governance cadence and preserve release discipline.")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "signoff_status": signoff_status,
            "trajectory": str(history_summary.get("trajectory", "stable")),
            "readiness_score_delta": int(delta_summary.get("readiness_score_delta", 0)),
            "dependency_blockers": int(signoff_summary.get("dependency_blockers", 0)),
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "lessons": lessons,
        "actions": ["Feed lessons into next cycle bootstrap planning."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release retrospective report")
    parser.add_argument("--delivery-signoff-report", required=True, help="Delivery signoff report")
    parser.add_argument("--readiness-delta-report", required=True, help="Readiness delta report")
    parser.add_argument("--release-gate-history-report", required=True, help="Release gate history report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_release_retrospective_report(
        delivery_signoff_report=read_json(args.delivery_signoff_report),
        readiness_delta_report=read_json(args.readiness_delta_report),
        release_gate_history_report=read_json(args.release_gate_history_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
