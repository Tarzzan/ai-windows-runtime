from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _state(queue_policy: str, risk_budget_mode: str, scope_budget_mode: str) -> str:
    if queue_policy == "restrictive" or risk_budget_mode == "conservative" or scope_budget_mode == "tight":
        return "reduce"
    if queue_policy == "managed" or risk_budget_mode == "balanced" or scope_budget_mode == "balanced":
        return "hold"
    return "expand"


def build_scope_rebalance_report(
    *, intake_queue_policy_report: dict, portfolio_risk_budget_report: dict, scope_budget_report: dict
) -> dict:
    queue = intake_queue_policy_report.get("summary", {})
    risk = portfolio_risk_budget_report.get("summary", {})
    scope = scope_budget_report.get("summary", {})

    queue_policy = str(queue.get("intake_queue_policy", "restrictive"))
    risk_mode = str(risk.get("risk_budget_mode", "conservative"))
    scope_mode = str(scope.get("scope_budget_mode", "tight"))

    rebalance = _state(queue_policy, risk_mode, scope_mode)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "scope_rebalance": rebalance,
            "intake_queue_policy": queue_policy,
            "risk_budget_mode": risk_mode,
            "scope_budget_mode": scope_mode,
        },
        "actions": [
            "Reduce active scope and protect delivery commitments before intake expansion."
            if rebalance == "reduce"
            else "Re-evaluate scope rebalance posture at each governance pass."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build scope rebalance report")
    p.add_argument("--intake-queue-policy-report", required=True)
    p.add_argument("--portfolio-risk-budget-report", required=True)
    p.add_argument("--scope-budget-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_scope_rebalance_report(
        intake_queue_policy_report=read_json(a.intake_queue_policy_report),
        portfolio_risk_budget_report=read_json(a.portfolio_risk_budget_report),
        scope_budget_report=read_json(a.scope_budget_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
