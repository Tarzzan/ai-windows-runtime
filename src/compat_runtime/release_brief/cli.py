from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _headline(summary: dict) -> str:
    recommendation = str(summary.get("pilot_recommendation", "not_ready"))
    score = int(summary.get("readiness_score", 0))
    decision = str(summary.get("release_decision", "no-go"))
    return f"Pilot={recommendation} | Readiness={score} | Decision={decision}"


def _actions(recommendation: str) -> list[str]:
    if recommendation == "ready":
        return ["Publish release brief to stakeholders and start pilot communications."]
    if recommendation == "limited_pilot":
        return ["Publish constrained pilot brief with risk caveats and rollback criteria."]
    return ["Publish blocker-focused brief and keep pilot launch on hold."]


def build_release_brief_report(
    *,
    pilot_readiness_report: dict,
    readiness_scorecard_report: dict,
    release_forecast_report: dict,
    release_gate_history_report: dict,
    risk_watchlist_report: dict,
    release_policy_report: dict | None = None,
) -> dict:
    pilot_summary = pilot_readiness_report.get("summary", {})
    forecast_summary = release_forecast_report.get("summary", {})
    history_summary = release_gate_history_report.get("summary", {})
    watchlist_summary = risk_watchlist_report.get("summary", {})
    release_policy_summary = release_policy_report or {}

    recommendation = str(pilot_readiness_report.get("recommendation", "not_ready"))
    summary = {
        "pilot_recommendation": recommendation,
        "readiness_score": int(readiness_scorecard_report.get("score", 0)),
        "readiness_band": str(readiness_scorecard_report.get("band", "red")),
        "release_decision": str(pilot_summary.get("release_decision", "no-go")),
        "quality_gate": str(pilot_summary.get("quality_gate", "fail")),
        "estimated_iterations_to_go": int(forecast_summary.get("estimated_iterations_to_go", 1)),
        "trajectory": str(history_summary.get("trajectory", "stable")),
        "p0_watchlist_entries": int(watchlist_summary.get("p0_entries", 0)),
        "blocking_tasks": int(pilot_summary.get("blocking_tasks", 0)),
        "release_policy_status": str(release_policy_summary.get("status", "missing")),
        "release_policy_failures": len(release_policy_summary.get("failures", [])),
    }

    risks = []
    for entry in risk_watchlist_report.get("entries", [])[:5]:
        risks.append(
            {
                "id": str(entry.get("id", "risk")),
                "priority": str(entry.get("priority", "P2")),
                "detail": str(entry.get("detail", "")),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "headline": _headline(summary),
        "summary": summary,
        "top_risks": risks,
        "actions": _actions(recommendation),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release brief report")
    parser.add_argument("--pilot-readiness-report", required=True, help="Pilot readiness report path")
    parser.add_argument(
        "--readiness-scorecard-report", required=True, help="Readiness scorecard report path"
    )
    parser.add_argument("--release-forecast-report", required=True, help="Release forecast report path")
    parser.add_argument("--release-gate-history-report", required=True, help="Release gate history path")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--release-policy-report", required=False, help="Optional release policy report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_release_brief_report(
        pilot_readiness_report=read_json(args.pilot_readiness_report),
        readiness_scorecard_report=read_json(args.readiness_scorecard_report),
        release_forecast_report=read_json(args.release_forecast_report),
        release_gate_history_report=read_json(args.release_gate_history_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        release_policy_report=read_json(args.release_policy_report) if args.release_policy_report else None,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
