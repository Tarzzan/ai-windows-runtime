from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _message(cockpit_status: str, recommendation: str) -> str:
    if cockpit_status == "on_track":
        return "Readiness trend supports controlled pilot expansion."
    if recommendation == "limited_pilot":
        return "Pilot remains constrained pending blocker burn-down."
    return "Launch remains blocked until critical remediation is completed."


def build_stakeholder_update_report(
    *, delivery_cockpit_report: dict, release_brief_report: dict, risk_watchlist_report: dict
) -> dict:
    cockpit_summary = delivery_cockpit_report.get("summary", {})
    brief_summary = release_brief_report.get("summary", {})
    watchlist_summary = risk_watchlist_report.get("summary", {})

    status = str(cockpit_summary.get("cockpit_status", "at_risk"))
    recommendation = str(brief_summary.get("pilot_recommendation", "not_ready"))

    summary = {
        "audience": "stakeholders",
        "delivery_status": status,
        "pilot_recommendation": recommendation,
        "readiness_score": int(brief_summary.get("readiness_score", 0)),
        "trajectory": str(brief_summary.get("trajectory", "stable")),
        "p0_risks": int(watchlist_summary.get("p0_entries", 0)),
        "release_policy_status": str(cockpit_summary.get("release_policy_status", "missing")),
        "release_policy_failures": int(cockpit_summary.get("release_policy_failures", 0)),
    }

    highlights = [
        _message(status, recommendation),
        f"P0 watchlist entries: {summary['p0_risks']}",
        f"Readiness score: {summary['readiness_score']}",
    ]

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "highlights": highlights,
        "actions": ["Share this update in release governance sync."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build stakeholder update report")
    parser.add_argument("--delivery-cockpit-report", required=True, help="Delivery cockpit report path")
    parser.add_argument("--release-brief-report", required=True, help="Release brief report path")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_stakeholder_update_report(
        delivery_cockpit_report=read_json(args.delivery_cockpit_report),
        release_brief_report=read_json(args.release_brief_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
