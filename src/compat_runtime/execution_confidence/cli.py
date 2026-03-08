from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


def _confidence_band(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def _execution_mode(score: int, p0_entries: int, policy_failures: int) -> str:
    if policy_failures > 0 or p0_entries >= 3:
        return "stabilize"
    if score >= 80 and p0_entries == 0:
        return "accelerate"
    return "controlled"


def _actions(mode: str, policy_failures: int) -> list[str]:
    actions: list[str] = []
    if policy_failures > 0:
        actions.append("Resolve policy compliance failures before confidence escalation.")
    if mode == "accelerate":
        actions.append("Increase execution throughput while preserving validation cadence.")
    elif mode == "controlled":
        actions.append("Continue controlled execution and reduce high-priority risks incrementally.")
    else:
        actions.append("Prioritize risk stabilization and blocker burn-down before new scope intake.")
    return actions


def build_execution_confidence_report(
    *,
    readiness_scorecard_report: dict,
    release_forecast_report: dict,
    risk_watchlist_report: dict,
    policy_health_report: dict | None = None,
) -> dict:
    score = int(readiness_scorecard_report.get("score", 0))
    forecast_summary = release_forecast_report.get("summary", {})
    watchlist_summary = risk_watchlist_report.get("summary", {})
    policy = policy_health_report or {}

    iterations_to_go = int(forecast_summary.get("estimated_iterations_to_go", 1))
    p0_entries = int(watchlist_summary.get("p0_entries", 0))
    p1_entries = int(watchlist_summary.get("p1_entries", 0))
    policy_failures = 0 if bool(policy.get("policy_compliance_level") == "compliant") else 1

    penalties = {
        "forecast_penalty": min(20, iterations_to_go * 3),
        "p0_penalty": min(30, p0_entries * 10),
        "p1_penalty": min(12, p1_entries * 2),
        "policy_penalty": 15 if policy_failures > 0 else 0,
    }

    confidence_score = _clamp(score - sum(penalties.values()))
    confidence_band = _confidence_band(confidence_score)
    execution_mode = _execution_mode(confidence_score, p0_entries, policy_failures)

    summary = {
        "readiness_score": score,
        "confidence_score": confidence_score,
        "confidence_band": confidence_band,
        "execution_mode": execution_mode,
        "estimated_iterations_to_go": iterations_to_go,
        "p0_entries": p0_entries,
        "p1_entries": p1_entries,
        "policy_compliance_level": str(policy.get("policy_compliance_level", "missing")),
    }

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "penalties": penalties,
        "actions": _actions(execution_mode, policy_failures),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build execution confidence report")
    parser.add_argument("--readiness-scorecard-report", required=True, help="Readiness scorecard report path")
    parser.add_argument("--release-forecast-report", required=True, help="Release forecast report path")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--policy-health-report", required=False, help="Optional policy health report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_execution_confidence_report(
        readiness_scorecard_report=read_json(args.readiness_scorecard_report),
        release_forecast_report=read_json(args.release_forecast_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        policy_health_report=read_json(args.policy_health_report) if args.policy_health_report else None,
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
