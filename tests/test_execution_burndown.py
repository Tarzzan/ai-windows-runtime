from compat_runtime.execution_burndown.cli import build_execution_burndown_report


def test_execution_burndown_projects_milestones():
    report = build_execution_burndown_report(
        iteration_plan_report={"summary": {"total_tasks": 10, "blocking_tasks": 6, "estimated_total_hours": 60}},
        release_forecast_report={"assumptions": {"blocking_tasks_per_iteration_target": 3}},
        readiness_scorecard_report={
            "score": 30,
            "summary": {"release_policy_status": "fail", "release_policy_failures": 1},
        },
    )

    assert report["summary"]["iterations_to_clear_blockers"] == 2
    assert report["summary"]["release_policy_status"] == "fail"
    assert report["summary"]["release_policy_failures"] == 1
    assert report["summary"]["projected_score_iteration_2"] >= 50
    assert len(report["milestones"]) == 3
    assert report["actions"]


def test_execution_burndown_handles_zero_blockers():
    report = build_execution_burndown_report(
        iteration_plan_report={"summary": {"total_tasks": 2, "blocking_tasks": 0, "estimated_total_hours": 8}},
        release_forecast_report={"assumptions": {"blocking_tasks_per_iteration_target": 3}},
        readiness_scorecard_report={
            "score": 85,
            "summary": {"release_policy_status": "pass", "release_policy_failures": 0},
        },
    )

    assert report["summary"]["iterations_to_clear_blockers"] == 0
    assert report["summary"]["release_policy_status"] == "pass"
    assert report["summary"]["projected_band_iteration_2"] == "green"
