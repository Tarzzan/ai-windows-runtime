from compat_runtime.scope_transition_gate.cli import build_scope_transition_gate_report


def test_scope_transition_gate_blocked_when_pacing_slow():
    report = build_scope_transition_gate_report(
        intake_pacing_window_report={"summary": {"intake_pacing_window": "slow"}},
        scope_freeze_guard_report={"summary": {"scope_freeze_guard": "guarded"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_transition_gate"] == "blocked"


def test_scope_transition_gate_open_when_fast_and_open_and_policy_pass():
    report = build_scope_transition_gate_report(
        intake_pacing_window_report={"summary": {"intake_pacing_window": "fast"}},
        scope_freeze_guard_report={"summary": {"scope_freeze_guard": "open"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["scope_transition_gate"] == "open"
