from compat_runtime.transition_readiness_index.cli import build_transition_readiness_index_report


def test_transition_readiness_blocked_with_blocked_gate_and_high_stress():
    report = build_transition_readiness_index_report(
        scope_transition_gate_report={"summary": {"scope_transition_gate": "blocked"}},
        delivery_stress_index_report={"summary": {"delivery_stress_score": 90}},
        policy_health_report={"policy_compliance_level": "partially_compliant"},
    )
    assert report["summary"]["transition_readiness_band"] == "blocked"


def test_transition_readiness_ready_when_gate_open_and_low_stress():
    report = build_transition_readiness_index_report(
        scope_transition_gate_report={"summary": {"scope_transition_gate": "open"}},
        delivery_stress_index_report={"summary": {"delivery_stress_score": 10}},
        policy_health_report={"policy_compliance_level": "compliant"},
    )
    assert report["summary"]["transition_readiness_band"] == "ready"
