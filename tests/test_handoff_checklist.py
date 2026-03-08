from compat_runtime.handoff_checklist.cli import build_handoff_checklist_report


def test_handoff_checklist_counts():
    report = build_handoff_checklist_report(
        stakeholder_update_report={
            "summary": {
                "delivery_status": "watch",
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
        ownership_assignment_report={"summary": {"unassigned_items": 0}},
        rollout_guardrails_report={"summary": {"stop_conditions": 2}},
        validation_command_pack={"commands": [{"command": "pytest -q"}]},
    )
    assert report["summary"]["checks_total"] == 5
    assert report["summary"]["checks_fail"] == 0
    assert report["summary"]["release_policy_status"] == "pass"
