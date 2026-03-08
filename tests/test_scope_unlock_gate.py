from compat_runtime.scope_unlock_gate.cli import build_scope_unlock_gate_report


def test_scope_unlock_gate_locked_when_resumption_hold():
    report = build_scope_unlock_gate_report(
        intake_resumption_policy_report={"summary": {"intake_resumption_policy": "hold"}},
        scope_admission_gate_report={"summary": {"scope_admission_gate": "guarded"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_unlock_gate"] == "locked"


def test_scope_unlock_gate_unlocked_when_all_open():
    report = build_scope_unlock_gate_report(
        intake_resumption_policy_report={"summary": {"intake_resumption_policy": "resume"}},
        scope_admission_gate_report={"summary": {"scope_admission_gate": "open"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_unlock_gate"] == "unlocked"
