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
    assert report["summary"]["office_readiness"] == "not_provided"


def test_launch_readiness_blocked_when_office_is_blocked():
    report = build_launch_readiness_report(
        handoff_checklist_report={"summary": {"checks_fail": 0}},
        validation_coverage_report={"summary": {"missing_reports": 0}},
        quality_gate_report={"gate": "pass"},
        release_decision_report={"decision": "go"},
        pilot_readiness_report={"recommendation": "ready"},
        office_readiness_report={"status": "blocked"},
    )

    assert report["status"] == "blocked"
    assert report["summary"]["office_readiness"] == "blocked"


def test_launch_readiness_limited_when_office_is_limited():
    report = build_launch_readiness_report(
        handoff_checklist_report={"summary": {"checks_fail": 0}},
        validation_coverage_report={"summary": {"missing_reports": 0}},
        quality_gate_report={"gate": "pass"},
        release_decision_report={"decision": "go"},
        pilot_readiness_report={"recommendation": "not_ready"},
        office_readiness_report={"status": "limited"},
    )

    assert report["status"] == "limited"
    assert report["summary"]["office_readiness"] == "limited"


def test_launch_readiness_ready_with_limited_office_and_pilot():
    report = build_launch_readiness_report(
        handoff_checklist_report={"summary": {"checks_fail": 0}},
        validation_coverage_report={"summary": {"missing_reports": 0}},
        quality_gate_report={"gate": "warn"},
        release_decision_report={"decision": "go"},
        pilot_readiness_report={"recommendation": "limited_pilot"},
        office_readiness_report={"status": "limited"},
    )

    assert report["status"] == "ready"
