from compat_runtime.ops_runbook.cli import build_ops_runbook_report


def test_ops_runbook_operational():
    report = build_ops_runbook_report(
        rollout_guardrails_report={"stop_conditions": ["x"], "safeguards": [{"id": "s1"}]},
        validation_command_pack={"commands": [{"id": "c1", "command": "pytest -q", "priority": "P0"}]},
        handoff_checklist_report={"summary": {"checks_fail": 0}},
    )
    assert report["summary"]["runbook_readiness"] == "operational"
