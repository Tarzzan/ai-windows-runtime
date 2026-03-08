from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _mode(score: int) -> str:
    if score >= 70:
        return "flexible"
    if score >= 40:
        return "balanced"
    return "tight"


def build_scope_budget_report(
    *, commitment_pacing_report: dict, readiness_scorecard_report: dict, release_forecast_report: dict
) -> dict:
    pacing = commitment_pacing_report.get("summary", {})
    scorecard = readiness_scorecard_report
    forecast = release_forecast_report.get("summary", {})

    commitment_mode = str(pacing.get("commitment_mode", "stabilize"))
    readiness_score = int(scorecard.get("score", 0))
    iterations_to_go = int(forecast.get("estimated_iterations_to_go", 6))

    mode_base = {"stabilize": 28, "paced": 55, "expand": 78}.get(commitment_mode, 28)
    readiness_bonus = max(-20, min(20, (readiness_score - 60) // 2))
    iteration_penalty = min(24, iterations_to_go * 4)

    score = max(0, min(100, mode_base + readiness_bonus - iteration_penalty))
    budget_mode = _mode(score)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_budget_score": score,
            "scope_budget_mode": budget_mode,
            "commitment_mode": commitment_mode,
            "readiness_score": readiness_score,
            "estimated_iterations_to_go": iterations_to_go,
        },
        "actions": [
            "Keep scope budget tight until forecast horizon shrinks."
            if budget_mode == "tight"
            else "Track scope budget drift each cycle before opening new commitments."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope budget report")
    p.add_argument("--commitment-pacing-report", required=True)
    p.add_argument("--readiness-scorecard-report", required=True)
    p.add_argument("--release-forecast-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_budget_report(
        commitment_pacing_report=read_json(a.commitment_pacing_report),
        readiness_scorecard_report=read_json(a.readiness_scorecard_report),
        release_forecast_report=read_json(a.release_forecast_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
