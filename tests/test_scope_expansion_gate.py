from compat_runtime.scope_expansion_gate.cli import build_scope_expansion_gate_report


def test_scope_expansion_gate_closed_when_expansion_hold():
    report = build_scope_expansion_gate_report(
        intake_expansion_policy_report={"summary": {"intake_expansion_policy": "hold"}},
        scope_unlock_gate_report={"summary": {"scope_unlock_gate": "guarded"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_expansion_gate"] == "closed"


def test_scope_expansion_gate_open_when_all_open():
    report = build_scope_expansion_gate_report(
        intake_expansion_policy_report={"summary": {"intake_expansion_policy": "expand"}},
        scope_unlock_gate_report={"summary": {"scope_unlock_gate": "unlocked"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_expansion_gate"] == "open"
