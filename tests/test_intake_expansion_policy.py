from compat_runtime.intake_expansion_policy.cli import build_intake_expansion_policy_report


def test_intake_expansion_policy_hold_when_expansion_blocked():
    report = build_intake_expansion_policy_report(
        scope_expansion_readiness_report={"summary": {"scope_expansion_readiness_band": "blocked"}},
        intake_resumption_policy_report={"summary": {"intake_resumption_policy": "stage"}},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "balanced"}},
    )
    assert report["summary"]["intake_expansion_policy"] == "hold"


def test_intake_expansion_policy_expand_when_all_open():
    report = build_intake_expansion_policy_report(
        scope_expansion_readiness_report={"summary": {"scope_expansion_readiness_band": "ready"}},
        intake_resumption_policy_report={"summary": {"intake_resumption_policy": "resume"}},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "abundant"}},
    )
    assert report["summary"]["intake_expansion_policy"] == "expand"
