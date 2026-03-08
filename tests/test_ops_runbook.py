from compat_runtime.ops_runbook.cli import build_ops_runbook_report


def test_ops_runbook_operational():
    report = build_ops_runbook_report(
        rollout_guardrails_report={"stop_conditions": ["x"], "safeguards": [{"id": "s1"}]},
        validation_command_pack={"commands": [{"id": "c1", "command": "pytest -q", "priority": "P0"}]},
        handoff_checklist_report={
            "summary": {"checks_fail": 0, "release_policy_status": "pass", "release_policy_failures": 0}
        },
    )
    assert report["summary"]["runbook_readiness"] == "operational"
    assert report["summary"]["release_policy_status"] == "pass"
    assert report["summary"]["release_policy_failures"] == 0


def test_ops_runbook_needs_attention_when_release_policy_failed():
    report = build_ops_runbook_report(
        rollout_guardrails_report={"stop_conditions": ["x"], "safeguards": [{"id": "s1"}]},
        validation_command_pack={"commands": [{"id": "c1", "command": "pytest -q", "priority": "P0"}]},
        handoff_checklist_report={
            "summary": {"checks_fail": 0, "release_policy_status": "fail", "release_policy_failures": 2}
        },
    )
    assert report["summary"]["runbook_readiness"] == "needs_attention"
