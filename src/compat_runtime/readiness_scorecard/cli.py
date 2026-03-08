from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


def _actions(band: str) -> list[str]:
    if band == "red":
        return [
            "Keep release blocked and focus on blocking P0 tasks.",
            "Re-run full pipeline and regenerate scorecard after each remediation batch.",
        ]
    if band == "amber":
        return [
            "Address highest-impact remaining blockers before release decision review.",
            "Track warning and forecast drift on each iteration.",
        ]
    return ["Readiness posture is strong. Proceed with controlled release validation steps."]


def build_readiness_scorecard_report(
    *,
    quality_gate_report: dict,
    release_decision_report: dict,
    iteration_plan_report: dict,
    release_forecast_report: dict,
    kpi_report: dict,
) -> dict:
    score = 100
    factors = []

    gate = str(quality_gate_report.get("gate", "fail"))
    if gate == "fail":
        score -= 25
        factors.append({"factor": "quality_gate_fail", "delta": -25, "detail": "gate=fail"})
    elif gate == "warn":
        score -= 10
        factors.append({"factor": "quality_gate_warn", "delta": -10, "detail": "gate=warn"})
    else:
        factors.append({"factor": "quality_gate_pass", "delta": 0, "detail": "gate=pass"})

    decision = str(release_decision_report.get("decision", "no-go"))
    if decision == "no-go":
        score -= 25
        factors.append({"factor": "release_decision_no_go", "delta": -25, "detail": "decision=no-go"})
    elif decision == "hold":
        score -= 12
        factors.append({"factor": "release_decision_hold", "delta": -12, "detail": "decision=hold"})
    else:
        factors.append({"factor": "release_decision_go", "delta": 0, "detail": "decision=go"})

    risk_level = str(kpi_report.get("summary", {}).get("risk_level", "high"))
    if risk_level == "high":
        score -= 15
        factors.append({"factor": "kpi_risk_high", "delta": -15, "detail": "risk_level=high"})
    elif risk_level == "medium":
        score -= 8
        factors.append({"factor": "kpi_risk_medium", "delta": -8, "detail": "risk_level=medium"})
    else:
        factors.append({"factor": "kpi_risk_low", "delta": 0, "detail": "risk_level=low"})

    plan_summary = iteration_plan_report.get("summary", {})
    blocking = int(plan_summary.get("blocking_tasks", 0))
    blocking_penalty = min(24, blocking * 3)
    if blocking_penalty > 0:
        score -= blocking_penalty
    factors.append(
        {
            "factor": "blocking_tasks_penalty",
            "delta": -blocking_penalty,
            "detail": f"blocking_tasks={blocking}",
        }
    )

    forecast_summary = release_forecast_report.get("summary", {})
    iterations = int(forecast_summary.get("estimated_iterations_to_go", 1))
    release_policy_status = str(forecast_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(forecast_summary.get("release_policy_failures", 0))
    forecast_penalty = 0
    if iterations > 4:
        forecast_penalty = 12
    elif iterations > 2:
        forecast_penalty = 6
    if forecast_penalty > 0:
        score -= forecast_penalty
    factors.append(
        {
            "factor": "forecast_penalty",
            "delta": -forecast_penalty,
            "detail": f"estimated_iterations_to_go={iterations}",
        }
    )

    score = max(0, min(100, score))
    band = _band(score)

    release_candidate = (
        score >= 80
        and decision == "go"
        and gate == "pass"
        and blocking == 0
        and risk_level in {"low", "medium"}
    )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "band": band,
        "release_candidate": release_candidate,
        "summary": {
            "decision_context": decision,
            "quality_gate": gate,
            "risk_level": risk_level,
            "blocking_tasks": blocking,
            "estimated_iterations_to_go": iterations,
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "factors": factors,
        "actions": _actions(band),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release readiness scorecard report")
    parser.add_argument("--quality-gate-report", required=True, help="Quality gate report path")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report path")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--release-forecast-report", required=True, help="Release forecast report path")
    parser.add_argument("--kpi-report", required=True, help="KPI report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_readiness_scorecard_report(
        quality_gate_report=read_json(args.quality_gate_report),
        release_decision_report=read_json(args.release_decision_report),
        iteration_plan_report=read_json(args.iteration_plan_report),
        release_forecast_report=read_json(args.release_forecast_report),
        kpi_report=read_json(args.kpi_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
