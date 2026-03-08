from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


OWNER_BY_SIGNAL = {
    "release_decision": "release-engineering",
    "hook_backlog": "runtime-instrumentation",
    "proposal_risk": "compatibility-engineering",
    "runtime_signal": "runtime-observability",
}


def _owner_for_source(source: str) -> str:
    return OWNER_BY_SIGNAL.get(source, "compatibility-engineering")


def _actions(unassigned: int, p0: int) -> list[str]:
    actions = []
    if p0 > 0:
        actions.append("Assign explicit owners for all P0 items before next standup.")
    if unassigned > 0:
        actions.append("Resolve unassigned entries and update ownership mapping rules.")
    if not actions:
        actions.append("Ownership coverage is complete. Track completion by owner.")
    return actions


def build_ownership_assignment_report(
    *,
    iteration_plan_report: dict,
    risk_watchlist_report: dict,
    validation_command_pack: dict,
) -> dict:
    task_rows = []
    for task in iteration_plan_report.get("tasks", []):
        source = str(task.get("source", "unknown"))
        task_rows.append(
            {
                "id": str(task.get("id", "task")),
                "priority": str(task.get("priority", "P2")),
                "blocking": bool(task.get("blocking", False)),
                "owner": _owner_for_source(source),
                "source": source,
                "objective": str(task.get("objective", "")),
                "suggested_command": str(task.get("suggested_command", "")),
            }
        )

    command_by_task = {
        str(command.get("task_id")): str(command.get("command"))
        for command in validation_command_pack.get("commands", [])
        if isinstance(command.get("task_id"), str)
    }
    for row in task_rows:
        if row["id"] in command_by_task:
            row["suggested_command"] = command_by_task[row["id"]]

    watchlist_rows = []
    for entry in risk_watchlist_report.get("entries", []):
        kind = str(entry.get("kind", "unknown"))
        watchlist_rows.append(
            {
                "id": str(entry.get("id", "entry")),
                "priority": str(entry.get("priority", "P2")),
                "owner": _owner_for_source(kind),
                "kind": kind,
                "detail": str(entry.get("detail", "")),
                "evidence": str(entry.get("evidence", "")),
            }
        )

    owners = sorted({row["owner"] for row in task_rows + watchlist_rows if row.get("owner")})
    p0 = sum(1 for row in task_rows if row["priority"] == "P0") + sum(
        1 for row in watchlist_rows if row["priority"] == "P0"
    )
    unassigned = sum(1 for row in task_rows if not row["owner"]) + sum(
        1 for row in watchlist_rows if not row["owner"]
    )
    watchlist_summary = risk_watchlist_report.get("summary", {})
    release_policy_status = str(watchlist_summary.get("release_policy_status", "missing"))
    release_policy_failures = int(watchlist_summary.get("release_policy_failures", 0))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "owners": len(owners),
            "tasks_assigned": len(task_rows),
            "watchlist_assigned": len(watchlist_rows),
            "p0_items": p0,
            "unassigned_items": unassigned,
            "release_policy_status": release_policy_status,
            "release_policy_failures": release_policy_failures,
        },
        "owners": owners,
        "tasks": task_rows,
        "watchlist": watchlist_rows,
        "actions": _actions(unassigned, p0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ownership assignment report")
    parser.add_argument("--iteration-plan-report", required=True, help="Iteration plan report path")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report path")
    parser.add_argument("--validation-command-pack", required=True, help="Validation command pack path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_ownership_assignment_report(
        iteration_plan_report=read_json(args.iteration_plan_report),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        validation_command_pack=read_json(args.validation_command_pack),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
