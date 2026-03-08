from compat_runtime.scope_admission_gate.cli import build_scope_admission_gate_report


def test_scope_admission_gate_closed_when_transition_hold():
    report = build_scope_admission_gate_report(
        intake_transition_policy_report={"summary": {"intake_transition_policy": "hold"}},
        scope_freeze_guard_report={"summary": {"scope_freeze_guard": "guarded"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_admission_gate"] == "closed"


def test_scope_admission_gate_open_when_transition_advance_and_policy_pass():
    report = build_scope_admission_gate_report(
        intake_transition_policy_report={"summary": {"intake_transition_policy": "advance"}},
        scope_freeze_guard_report={"summary": {"scope_freeze_guard": "open"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_admission_gate"] == "open"
