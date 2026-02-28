from compat_runtime.ownership_assignment.cli import build_ownership_assignment_report


def test_ownership_assignment_maps_tasks_and_watchlist():
    report = build_ownership_assignment_report(
        iteration_plan_report={
            "tasks": [
                {
                    "id": "t1",
                    "priority": "P0",
                    "blocking": True,
                    "source": "release_decision",
                    "objective": "Fix gate",
                    "suggested_command": "scripts/run-full-pipeline.sh out",
                }
            ]
        },
        risk_watchlist_report={
            "entries": [{"id": "w1", "priority": "P0", "kind": "proposal_risk", "detail": "high"}]
        },
        validation_command_pack={"commands": [{"task_id": "t1", "command": "pytest -q"}]},
    )

    assert report["summary"]["tasks_assigned"] == 1
    assert report["summary"]["watchlist_assigned"] == 1
    assert report["tasks"][0]["owner"]
    assert report["actions"]
