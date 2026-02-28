from compat_runtime.backlog_refresh.cli import build_backlog_refresh_report


def test_backlog_refresh_promotes_blocking_tasks():
    report = build_backlog_refresh_report(
        incident_feedback_report={"summary": {"feedback_priority": "P0"}},
        iteration_plan_report={
            "tasks": [
                {"id": "t1", "priority": "P2", "blocking": True, "objective": "A"},
                {"id": "t2", "priority": "P2", "blocking": False, "objective": "B"},
            ]
        },
        remediation_sprint_report={"summary": {"sprint_now_tasks": 1, "sprint_next_tasks": 2}},
    )
    assert report["items"][0]["priority"] == "P0"
