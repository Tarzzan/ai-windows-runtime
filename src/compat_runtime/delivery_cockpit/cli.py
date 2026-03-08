from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _status(score: int, pilot_recommendation: str, missing_reports: int) -> str:
    if pilot_recommendation == "ready" and score >= 75 and missing_reports == 0:
        return "on_track"
    if pilot_recommendation == "limited_pilot" and score >= 55:
        return "watch"
    return "at_risk"


def build_delivery_cockpit_report(
    *, release_brief_report: dict, remediation_sprint_report: dict, artifact_health_report: dict
) -> dict:
    brief_summary = release_brief_report.get("summary", {})
    sprint_summary = remediation_sprint_report.get("summary", {})
    health_summary = artifact_health_report.get("summary", {})

    readiness_score = int(brief_summary.get("readiness_score", 0))
    pilot_recommendation = str(brief_summary.get("pilot_recommendation", "not_ready"))
    missing_reports = int(health_summary.get("missing_reports", 0))

    summary = {
        "cockpit_status": _status(readiness_score, pilot_recommendation, missing_reports),
        "readiness_score": readiness_score,
        "pilot_recommendation": pilot_recommendation,
        "blocking_tasks": int(brief_summary.get("blocking_tasks", 0)),
        "sprint_now_tasks": int(sprint_summary.get("sprint_now_tasks", 0)),
        "missing_validation_reports": missing_reports,
        "health_ratio": float(health_summary.get("health_ratio", 0.0)),
        "release_policy_status": str(brief_summary.get("release_policy_status", "missing")),
        "release_policy_failures": int(brief_summary.get("release_policy_failures", 0)),
    }

    actions = []
    if summary["cockpit_status"] == "at_risk":
        actions.append("Keep launch on hold and burn down blocking sprint_now tasks first.")
    elif summary["cockpit_status"] == "watch":
        actions.append("Proceed with limited pilot and review missing risks each day.")
    else:
        actions.append("Proceed according to pilot plan and keep guardrails active.")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "actions": actions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build delivery cockpit report")
    parser.add_argument("--release-brief-report", required=True, help="Release brief report path")
    parser.add_argument(
        "--remediation-sprint-report", required=True, help="Remediation sprint report path"
    )
    parser.add_argument("--artifact-health-report", required=True, help="Artifact health report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_delivery_cockpit_report(
        release_brief_report=read_json(args.release_brief_report),
        remediation_sprint_report=read_json(args.remediation_sprint_report),
        artifact_health_report=read_json(args.artifact_health_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
