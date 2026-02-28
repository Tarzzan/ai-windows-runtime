from compat_runtime.remediation_sprint.cli import build_remediation_sprint_report


def test_remediation_sprint_groups_tasks_by_priority():
    report = build_remediation_sprint_report(
        ownership_assignment_report={
            "tasks": [
                {"id": "a", "priority": "P0", "blocking": True, "owner": "o1", "objective": "A"},
                {"id": "b", "priority": "P1", "blocking": False, "owner": "o2", "objective": "B"},
                {"id": "c", "priority": "P2", "blocking": False, "owner": "o3", "objective": "C"},
            ]
        },
        execution_burndown_report={"summary": {"iterations_to_clear_blockers": 2}},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 4}},
    )

    assert report["summary"]["sprint_now_tasks"] == 1
    assert report["summary"]["sprint_next_tasks"] == 1
    assert report["summary"]["backlog_tasks"] == 1
    assert report["actions"]
