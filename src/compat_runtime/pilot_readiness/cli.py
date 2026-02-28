from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _recommendation(
    *,
    productization_ready: bool,
    score: int,
    decision: str,
    gate: str,
    blocking_tasks: int,
    iterations_to_go: int,
) -> str:
    if not productization_ready:
        return "not_ready"
    if (
        score >= 80
        and decision == "go"
        and gate == "pass"
        and blocking_tasks == 0
        and iterations_to_go <= 2
    ):
        return "ready"
    if score >= 50 and blocking_tasks <= 3 and iterations_to_go <= 4:
        return "limited_pilot"
    return "not_ready"


def _actions(recommendation: str) -> list[str]:
    if recommendation == "ready":
        return [
            "Prepare pilot rollout checklist and monitor runtime telemetry in real time.",
            "Publish pilot success criteria and rollback thresholds.",
        ]
    if recommendation == "limited_pilot":
        return [
            "Run a constrained pilot with explicit rollback guardrails.",
            "Limit pilot scope to scenarios covered by highest-confidence validation suites.",
        ]
    return [
        "Pilot is not ready. Resolve blocking tasks and improve readiness score first.",
        "Re-run forecast and scorecard after remediation milestones.",
    ]


def build_pilot_readiness_report(
    *,
    productization_readiness: dict,
    quality_gate_report: dict,
    release_decision_report: dict,
    readiness_scorecard_report: dict,
    release_forecast_report: dict,
    iteration_plan_report: dict,
    risk_watchlist_report: dict,
) -> dict:
    product_ready = bool(productization_readiness.get("ready", False))
    gate = str(quality_gate_report.get("gate", "fail"))
    decision = str(release_decision_report.get("decision", "no-go"))
    score = int(readiness_scorecard_report.get("score", 0))
    band = str(readiness_scorecard_report.get("band", "red"))
    plan_summary = iteration_plan_report.get("summary", {})
    forecast_summary = release_forecast_report.get("summary", {})
    watchlist_summary = risk_watchlist_report.get("summary", {})

    blocking_tasks = int(plan_summary.get("blocking_tasks", 0))
    iterations_to_go = int(forecast_summary.get("estimated_iterations_to_go", 1))
    p0_watchlist = int(watchlist_summary.get("p0_entries", 0))

    recommendation = _recommendation(
        productization_ready=product_ready,
        score=score,
        decision=decision,
        gate=gate,
        blocking_tasks=blocking_tasks,
        iterations_to_go=iterations_to_go,
    )

    blockers = []
    for check in release_decision_report.get("checks", []):
        if check.get("required") and check.get("status") != "pass":
            blockers.append(str(check.get("id")))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "recommendation": recommendation,
        "summary": {
            "productization_ready": product_ready,
            "quality_gate": gate,
            "release_decision": decision,
            "readiness_score": score,
            "readiness_band": band,
            "blocking_tasks": blocking_tasks,
            "estimated_iterations_to_go": iterations_to_go,
            "p0_watchlist_entries": p0_watchlist,
        },
        "blockers": blockers,
        "actions": _actions(recommendation),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pilot readiness recommendation report")
    parser.add_argument("--productization-readiness", required=True, help="Productization readiness path")
    parser.add_argument("--quality-gate-report", required=True, help="Quality gate report path")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report path")
    parser.add_argument(
        "--readiness-scorecard-report", required=True, help="Readiness scorecard report path"
    )
    parser.add_argument("--release-forecast-report", required=True, help="Release forecast report path")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_pilot_readiness_report(
        productization_readiness=read_json(args.productization_readiness),
        quality_gate_report=read_json(args.quality_gate_report),
        release_decision_report=read_json(args.release_decision_report),
        readiness_scorecard_report=read_json(args.readiness_scorecard_report),
        release_forecast_report=read_json(args.release_forecast_report),
        iteration_plan_report=read_json(args.iteration_plan_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
