from compat_runtime.hotfix_planner.cli import build_hotfix_planner_report


def test_hotfix_planner_urgent():
    report = build_hotfix_planner_report(
        stability_window_report={"summary": {"window_status": "unstable"}},
        incident_feedback_report={"summary": {"feedback_priority": "P0"}},
        rollback_hints_report={"hints": [{"proposal_id": "p1", "rollback_level": "full"}]},
    )
    assert report["summary"]["plan_mode"] == "urgent"
