from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _priority_rank(priority: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(priority, 0)


def _suite_command_by_domain(test_impact_report: dict, domain: str) -> str:
    for suite in test_impact_report.get("suites", []):
        categories = suite.get("trigger_categories", [])
        if isinstance(categories, list) and domain in categories:
            cmd = suite.get("suggested_command")
            if isinstance(cmd, str) and cmd:
                return cmd
    return "scripts/run-full-pipeline.sh out"


def _suite_command_by_gap(test_impact_report: dict, gap_id: str) -> str:
    for suite in test_impact_report.get("suites", []):
        proposals = suite.get("trigger_proposals", [])
        if isinstance(proposals, list) and gap_id in proposals:
            cmd = suite.get("suggested_command")
            if isinstance(cmd, str) and cmd:
                return cmd
    return "scripts/run-full-pipeline.sh out"


def _task(
    *,
    task_id: str,
    priority: str,
    objective: str,
    source: str,
    suggested_command: str,
    estimated_hours: int,
    blocking: bool,
) -> dict:
    return {
        "id": task_id,
        "priority": priority,
        "objective": objective,
        "source": source,
        "suggested_command": suggested_command,
        "estimated_hours": estimated_hours,
        "blocking": blocking,
    }


def _actions(decision: str, blocking_tasks: int) -> list[str]:
    if decision == "no-go":
        return [
            "Execute blocking P0 tasks first and keep release frozen.",
            "Re-run scripts/run-full-pipeline.sh out after completing blocking tasks.",
        ]
    if blocking_tasks > 0:
        return ["Resolve all blocking tasks before moving into broader compatibility expansion."]
    return ["Current iteration plan is actionable. Execute in priority order and review deltas."]


def build_iteration_plan_report(
    *,
    release_decision_report: dict,
    hook_backlog_report: dict,
    proposal_risk_report: dict,
    test_impact_report: dict,
) -> dict:
    tasks: list[dict] = []
    seen_ids: set[str] = set()

    decision = str(release_decision_report.get("decision", "hold"))

    for check in release_decision_report.get("checks", []):
        check_id = str(check.get("id", "check"))
        if check.get("required") and check.get("status") == "fail":
            task_id = f"gate-{check_id}"
            if task_id in seen_ids:
                continue
            seen_ids.add(task_id)
            title = str(check.get("title", check_id))
            tasks.append(
                _task(
                    task_id=task_id,
                    priority="P0",
                    objective=f"Resolve release blocker: {title}",
                    source="release_decision",
                    suggested_command="scripts/run-full-pipeline.sh out",
                    estimated_hours=6,
                    blocking=True,
                )
            )

    for item in hook_backlog_report.get("items", []):
        if not item.get("missing_hook"):
            continue
        domain = str(item.get("domain", "runtime"))
        task_id = f"hook-{domain}"
        if task_id in seen_ids:
            continue
        seen_ids.add(task_id)
        priority = str(item.get("urgency", "P1"))
        errors = int(item.get("errors", 0))
        high_risk = int(item.get("related_high_risk", 0))
        effort = min(24, 6 + errors * 3 + high_risk * 2)
        recommendation = str(item.get("recommended_hook", "Add missing runtime hook"))
        tasks.append(
            _task(
                task_id=task_id,
                priority=priority,
                objective=f"Implement missing {domain} hook: {recommendation}",
                source="hook_backlog",
                suggested_command=_suite_command_by_domain(test_impact_report, domain),
                estimated_hours=effort,
                blocking=priority == "P0",
            )
        )

    for proposal in proposal_risk_report.get("proposals", []):
        gap_id = proposal.get("gap_id")
        if not isinstance(gap_id, str):
            continue
        risk_level = str(proposal.get("risk_level", "low"))
        if risk_level not in {"high", "medium"}:
            continue
        task_id = f"risk-{gap_id}"
        if task_id in seen_ids:
            continue
        seen_ids.add(task_id)
        priority = "P0" if risk_level == "high" else "P1"
        score = int(proposal.get("risk_score", 0))
        effort = min(20, 4 + (score // 20))
        tasks.append(
            _task(
                task_id=task_id,
                priority=priority,
                objective=f"Validate and harden {risk_level}-risk proposal {gap_id}",
                source="proposal_risk",
                suggested_command=_suite_command_by_gap(test_impact_report, gap_id),
                estimated_hours=effort,
                blocking=priority == "P0",
            )
        )

    tasks.sort(
        key=lambda row: (
            -_priority_rank(str(row["priority"])),
            0 if row["blocking"] else 1,
            row["id"],
        )
    )

    blocking_tasks = sum(1 for task in tasks if task["blocking"])
    p0_tasks = sum(1 for task in tasks if task["priority"] == "P0")
    p1_tasks = sum(1 for task in tasks if task["priority"] == "P1")
    p2_tasks = sum(1 for task in tasks if task["priority"] == "P2")
    estimated_hours = sum(int(task["estimated_hours"]) for task in tasks)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "decision_context": decision,
        "summary": {
            "total_tasks": len(tasks),
            "blocking_tasks": blocking_tasks,
            "p0_tasks": p0_tasks,
            "p1_tasks": p1_tasks,
            "p2_tasks": p2_tasks,
            "estimated_total_hours": estimated_hours,
        },
        "tasks": tasks,
        "actions": _actions(decision, blocking_tasks),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build compatibility iteration action plan report")
    parser.add_argument("--release-decision-report", required=True, help="Release decision report path")
    parser.add_argument("--hook-backlog-report", required=True, help="Hook backlog report path")
    parser.add_argument("--proposal-risk-report", required=True, help="Proposal risk report path")
    parser.add_argument("--test-impact-report", required=True, help="Test impact report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_iteration_plan_report(
        release_decision_report=read_json(args.release_decision_report),
        hook_backlog_report=read_json(args.hook_backlog_report),
        proposal_risk_report=read_json(args.proposal_risk_report),
        test_impact_report=read_json(args.test_impact_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
