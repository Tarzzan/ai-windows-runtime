from compat_runtime.intake_resumption_policy.cli import build_intake_resumption_policy_report


def test_intake_resumption_policy_hold_when_reentry_blocked():
    report = build_intake_resumption_policy_report(
        scope_reentry_readiness_report={"summary": {"scope_reentry_readiness_band": "blocked"}},
        intake_transition_policy_report={"summary": {"intake_transition_policy": "stage"}},
        delivery_temperature_report={"summary": {"temperature": "warm"}},
    )
    assert report["summary"]["intake_resumption_policy"] == "hold"


def test_intake_resumption_policy_resume_when_all_green():
    report = build_intake_resumption_policy_report(
        scope_reentry_readiness_report={"summary": {"scope_reentry_readiness_band": "ready"}},
        intake_transition_policy_report={"summary": {"intake_transition_policy": "advance"}},
        delivery_temperature_report={"summary": {"temperature": "cool"}},
    )
    assert report["summary"]["intake_resumption_policy"] == "resume"
