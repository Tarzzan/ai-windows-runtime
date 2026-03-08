from compat_runtime.intake_transition_policy.cli import build_intake_transition_policy_report


def test_intake_transition_policy_hold_when_readiness_blocked():
    report = build_intake_transition_policy_report(
        transition_readiness_index_report={"summary": {"transition_readiness_band": "blocked"}},
        intake_pacing_window_report={"summary": {"intake_pacing_window": "moderate"}},
        intake_slot_policy_report={"summary": {"intake_slot_policy": "moderate"}},
    )
    assert report["summary"]["intake_transition_policy"] == "hold"


def test_intake_transition_policy_advance_when_all_open():
    report = build_intake_transition_policy_report(
        transition_readiness_index_report={"summary": {"transition_readiness_band": "ready"}},
        intake_pacing_window_report={"summary": {"intake_pacing_window": "fast"}},
        intake_slot_policy_report={"summary": {"intake_slot_policy": "expanded"}},
    )
    assert report["summary"]["intake_transition_policy"] == "advance"
