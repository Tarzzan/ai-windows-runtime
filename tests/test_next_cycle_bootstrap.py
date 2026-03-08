from compat_runtime.next_cycle_bootstrap.cli import build_next_cycle_bootstrap_report


def test_next_cycle_bootstrap_ready():
    report = build_next_cycle_bootstrap_report(
        release_retrospective_report={"summary": {"trajectory": "stable"}, "lessons": ["x"]},
        backlog_refresh_report={
            "summary": {
                "feedback_priority": "P1",
                "refreshed_items": 3,
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
        validation_command_pack={"commands": [{"command": "pytest -q"}]},
        delivery_signoff_report={"status": "approved"},
    )
    assert report["status"] == "ready"


def test_next_cycle_bootstrap_blocked_when_release_policy_failed():
    report = build_next_cycle_bootstrap_report(
        release_retrospective_report={"summary": {"trajectory": "stable"}, "lessons": []},
        backlog_refresh_report={
            "summary": {
                "feedback_priority": "P2",
                "refreshed_items": 1,
                "release_policy_status": "fail",
                "release_policy_failures": 2,
            }
        },
        validation_command_pack={"commands": [{"command": "pytest -q"}]},
        delivery_signoff_report={"status": "approved"},
    )
    assert report["status"] == "blocked"
