from compat_runtime.launch_readiness.cli import build_launch_readiness_report


def test_launch_readiness_ready_status():
    report = build_launch_readiness_report(
        handoff_checklist_report={"summary": {"checks_fail": 0}},
        validation_coverage_report={"summary": {"missing_reports": 0}},
        quality_gate_report={"gate": "pass"},
        release_decision_report={"decision": "go"},
        pilot_readiness_report={"recommendation": "ready"},
    )
    assert report["status"] == "ready"
