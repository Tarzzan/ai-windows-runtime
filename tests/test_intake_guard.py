from compat_runtime.intake_guard.cli import build_intake_guard_report


def test_intake_guard_strict_on_policy_or_narrow():
    report = build_intake_guard_report(
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "narrow"}},
        release_policy_report={"status": "pass"},
        priority_corridor_report={"summary": {"priority_corridor": "p0_only"}},
    )
    assert report["summary"]["intake_guard"] == "strict"


def test_intake_guard_open_when_wide_and_pass():
    report = build_intake_guard_report(
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "wide"}},
        release_policy_report={"status": "pass"},
        priority_corridor_report={"summary": {"priority_corridor": "full"}},
    )
    assert report["summary"]["intake_guard"] == "open"
