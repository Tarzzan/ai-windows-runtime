from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(score: int) -> str:
    if score >= 70:
        return "aggressive"
    if score >= 40:
        return "balanced"
    return "conservative"


def build_portfolio_risk_budget_report(
    *, commitment_guard_report: dict, risk_watchlist_report: dict, readiness_scorecard_report: dict
) -> dict:
    guard = commitment_guard_report.get("summary", {})
    risks = risk_watchlist_report.get("summary", {})

    guard_mode = str(guard.get("commitment_guard", "strict"))
    p0_entries = int(risks.get("p0_entries", 0))
    readiness_score = int(readiness_scorecard_report.get("score", 0))

    guard_base = {"strict": 24, "moderate": 52, "adaptive": 80}.get(guard_mode, 24)
    readiness_adjust = max(-20, min(20, (readiness_score - 60) // 2))
    p0_penalty = min(32, p0_entries * 8)

    score = max(0, min(100, guard_base + readiness_adjust - p0_penalty))
    budget_mode = _mode(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "risk_budget_score": score,
            "risk_budget_mode": budget_mode,
            "commitment_guard": guard_mode,
            "p0_entries": p0_entries,
            "readiness_score": readiness_score,
        },
        "actions": [
            "Keep conservative portfolio budget until P0 risk pressure decreases."
            if budget_mode == "conservative"
            else "Recalibrate portfolio risk budget at each iteration checkpoint."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build portfolio risk budget report")
    p.add_argument("--commitment-guard-report", required=True)
    p.add_argument("--risk-watchlist-report", required=True)
    p.add_argument("--readiness-scorecard-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_portfolio_risk_budget_report(
        commitment_guard_report=read_json(a.commitment_guard_report),
        risk_watchlist_report=read_json(a.risk_watchlist_report),
        readiness_scorecard_report=read_json(a.readiness_scorecard_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
