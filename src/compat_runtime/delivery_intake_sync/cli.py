from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _state(risk_budget_mode: str, admission_window: str, cadence: str) -> str:
    if risk_budget_mode == "conservative" or admission_window == "restricted" or cadence == "slow":
        return "blocked"
    if risk_budget_mode == "balanced" or admission_window == "controlled" or cadence == "moderate":
        return "aligned"
    return "expanding"


def build_delivery_intake_sync_report(
    *, portfolio_risk_budget_report: dict, admission_window_report: dict, cadence_recommendation_report: dict
) -> dict:
    budget = portfolio_risk_budget_report.get("summary", {})
    window = admission_window_report.get("summary", {})
    cadence = cadence_recommendation_report.get("summary", {})

    budget_mode = str(budget.get("risk_budget_mode", "conservative"))
    window_state = str(window.get("admission_window", "restricted"))
    cadence_value = str(cadence.get("cadence", "slow"))

    sync_state = _state(budget_mode, window_state, cadence_value)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "delivery_intake_sync": sync_state,
            "risk_budget_mode": budget_mode,
            "admission_window": window_state,
            "cadence": cadence_value,
        },
        "actions": [
            "Hold intake expansion until delivery/intake sync leaves blocked state."
            if sync_state == "blocked"
            else "Review delivery-intake sync posture before each intake decision."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build delivery intake sync report")
    p.add_argument("--portfolio-risk-budget-report", required=True)
    p.add_argument("--admission-window-report", required=True)
    p.add_argument("--cadence-recommendation-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_delivery_intake_sync_report(
        portfolio_risk_budget_report=read_json(a.portfolio_risk_budget_report),
        admission_window_report=read_json(a.admission_window_report),
        cadence_recommendation_report=read_json(a.cadence_recommendation_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
