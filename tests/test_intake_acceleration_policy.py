from compat_runtime.intake_acceleration_policy.cli import build_intake_acceleration_policy_report


def test_intake_acceleration_policy_hold_when_acceleration_blocked():
    report = build_intake_acceleration_policy_report(
        scope_acceleration_readiness_report={"summary": {"scope_acceleration_readiness_band": "blocked"}},
        intake_expansion_policy_report={"summary": {"intake_expansion_policy": "stage"}},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "balanced"}},
    )
    assert report["summary"]["intake_acceleration_policy"] == "hold"


def test_intake_acceleration_policy_accelerate_when_all_open():
    report = build_intake_acceleration_policy_report(
        scope_acceleration_readiness_report={"summary": {"scope_acceleration_readiness_band": "ready"}},
        intake_expansion_policy_report={"summary": {"intake_expansion_policy": "expand"}},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "abundant"}},
    )
    assert report["summary"]["intake_acceleration_policy"] == "accelerate"
