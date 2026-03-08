from compat_runtime.scope_acceleration_gate.cli import build_scope_acceleration_gate_report


def test_scope_acceleration_gate_closed_when_acceleration_hold():
    report = build_scope_acceleration_gate_report(
        intake_acceleration_policy_report={"summary": {"intake_acceleration_policy": "hold"}},
        scope_expansion_gate_report={"summary": {"scope_expansion_gate": "guarded"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_acceleration_gate"] == "closed"


def test_scope_acceleration_gate_open_when_all_open():
    report = build_scope_acceleration_gate_report(
        intake_acceleration_policy_report={"summary": {"intake_acceleration_policy": "accelerate"}},
        scope_expansion_gate_report={"summary": {"scope_expansion_gate": "open"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_acceleration_gate"] == "open"
