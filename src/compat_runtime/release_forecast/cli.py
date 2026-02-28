from __future__ import annotations

import argparse
import math
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _pace_factor(*, improved: int, regressed: int, risk_level: str) -> float:
    factor = 1.0
    if regressed > improved:
        factor += 0.5
    elif improved > regressed:
        factor -= 0.2

    if risk_level == "high":
        factor += 0.5
    elif risk_level == "medium":
        factor += 0.2

    return max(0.6, factor)


def _wave_from_iterations(iterations: int) -> str:
    if iterations <= 1:
        return "immediate"
    if iterations <= 3:
        return "near_term"
    return "long_term"


def _actions(decision: str, iterations: int, blockers: int) -> list[str]:
    actions = []
    if decision == "no-go":
        actions.append("Keep release frozen until forecast blockers are reduced.")
    if blockers > 0:
        actions.append("Execute blocking tasks first and re-evaluate forecast after each run.")
    if iterations > 3:
        actions.append("Split iteration plan into smaller milestones to improve delivery pace.")
    if not actions:
        actions.append("Forecast is favorable. Continue normal release cadence.")
    return actions


def build_release_forecast_report(
    *,
    iteration_plan_report: dict,
    release_decision_report: dict,
    kpi_report: dict,
    trend_report: dict,
) -> dict:
    decision = str(release_decision_report.get("decision", "hold"))
    risk_level = str(kpi_report.get("summary", {}).get("risk_level", "high"))

    summary_plan = iteration_plan_report.get("summary", {})
    blocking_tasks = int(summary_plan.get("blocking_tasks", 0))
    total_tasks = int(summary_plan.get("total_tasks", 0))
    p0_tasks = int(summary_plan.get("p0_tasks", 0))
    estimated_hours = int(summary_plan.get("estimated_total_hours", 0))

    trend_summary = trend_report.get("summary", {})
    improved = len(trend_summary.get("improved_metrics", []))
    regressed = len(trend_summary.get("regressed_metrics", []))
    pace = _pace_factor(improved=improved, regressed=regressed, risk_level=risk_level)

    # Heuristic baseline: 3 blocking tasks can be closed per iteration in healthy pace.
    base_iterations = max(1, math.ceil(blocking_tasks / 3)) if blocking_tasks > 0 else 1
    estimated_iterations = max(1, math.ceil(base_iterations * pace))

    hours_per_iteration = 24
    estimated_days = max(3, estimated_iterations * 7)
    wave = _wave_from_iterations(estimated_iterations)

    # Suggest the first 5 execution tasks as near-term runbook.
    top_tasks = []
    for task in iteration_plan_report.get("tasks", [])[:5]:
        top_tasks.append(
            {
                "id": task.get("id"),
                "priority": task.get("priority"),
                "blocking": bool(task.get("blocking", False)),
                "objective": task.get("objective"),
                "suggested_command": task.get("suggested_command"),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "decision_context": decision,
            "risk_level": risk_level,
            "total_tasks": total_tasks,
            "blocking_tasks": blocking_tasks,
            "p0_tasks": p0_tasks,
            "estimated_total_hours": estimated_hours,
            "estimated_iterations_to_go": estimated_iterations,
            "estimated_days_to_go": estimated_days,
            "forecast_wave": wave,
            "pace_factor": round(pace, 3),
            "trend_improved_metrics": improved,
            "trend_regressed_metrics": regressed,
        },
        "top_tasks": top_tasks,
        "actions": _actions(decision, estimated_iterations, blocking_tasks),
        "assumptions": {
            "hours_per_iteration_capacity": hours_per_iteration,
            "blocking_tasks_per_iteration_target": 3,
            "forecast_model": "heuristic_v1",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release forecast report")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report path")
    parser.add_argument("--kpi-report", required=True, help="KPI report path")
    parser.add_argument("--trend-report", required=True, help="Trend report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_release_forecast_report(
        iteration_plan_report=read_json(args.iteration_plan_report),
        release_decision_report=read_json(args.release_decision_report),
        kpi_report=read_json(args.kpi_report),
        trend_report=read_json(args.trend_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
