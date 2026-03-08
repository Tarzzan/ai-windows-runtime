from __future__ import annotations

import argparse
import math
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _band(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


def _actions(blocking_tasks: int, projected_score: int) -> list[str]:
    actions = []
    if blocking_tasks > 0:
        actions.append("Focus next iteration on blocking tasks to improve burndown slope.")
    if projected_score >= 75:
        actions.append("Projected readiness can reach green band in two iterations if pace holds.")
    else:
        actions.append("Increase iteration throughput or reduce scope to improve forecast confidence.")
    return actions


def build_execution_burndown_report(
    *,
    iteration_plan_report: dict,
    release_forecast_report: dict,
    readiness_scorecard_report: dict,
) -> dict:
    plan_summary = iteration_plan_report.get("summary", {})
    forecast_assumptions = release_forecast_report.get("assumptions", {})

    total_tasks = int(plan_summary.get("total_tasks", 0))
    blocking_tasks = int(plan_summary.get("blocking_tasks", 0))
    estimated_hours = int(plan_summary.get("estimated_total_hours", 0))
    current_score = int(readiness_scorecard_report.get("score", 0))
    scorecard_summary = readiness_scorecard_report.get("summary", {})
    release_policy_status = str(scorecard_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(scorecard_summary.get("release_policy_failures", 0))

    burn_target = int(forecast_assumptions.get("blocking_tasks_per_iteration_target", 3))
    burn_target = max(1, burn_target)
    iterations_to_clear = math.ceil(blocking_tasks / burn_target) if blocking_tasks > 0 else 0

    projected_score_iter1 = min(100, current_score + (15 if blocking_tasks > 0 else 5))
    projected_score_iter2 = min(100, current_score + (30 if blocking_tasks > 0 else 10))

    milestones = []
    for iteration in [1, 2, 3]:
        remaining = max(0, blocking_tasks - (burn_target * iteration))
        milestones.append(
            {
                "iteration": iteration,
                "target_blocking_remaining": remaining,
                "target_score": min(100, current_score + (15 * iteration)),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_tasks": total_tasks,
            "blocking_tasks": blocking_tasks,
            "estimated_total_hours": estimated_hours,
            "blocking_burn_target_per_iteration": burn_target,
            "iterations_to_clear_blockers": iterations_to_clear,
            "current_score": current_score,
            "projected_score_iteration_1": projected_score_iter1,
            "projected_score_iteration_2": projected_score_iter2,
            "projected_band_iteration_2": _band(projected_score_iter2),
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "milestones": milestones,
        "actions": _actions(blocking_tasks, projected_score_iter2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build execution burndown forecast report")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--release-forecast-report", required=True, help="Release forecast report path")
    parser.add_argument(
        "--readiness-scorecard-report", required=True, help="Readiness scorecard report path"
    )
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_execution_burndown_report(
        iteration_plan_report=read_json(args.iteration_plan_report),
        release_forecast_report=read_json(args.release_forecast_report),
        readiness_scorecard_report=read_json(args.readiness_scorecard_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
