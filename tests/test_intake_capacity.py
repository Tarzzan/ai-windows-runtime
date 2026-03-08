from compat_runtime.intake_capacity.cli import build_intake_capacity_report


def test_intake_capacity_constrained_with_strict_guard_and_pressure():
    report = build_intake_capacity_report(
        intake_guard_report={"summary": {"intake_guard": "strict"}},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "narrow"}},
        queue_pressure_report={"summary": {"queue_pressure_band": "high"}},
    )
    assert report["summary"]["intake_capacity_mode"] == "constrained"


def test_intake_capacity_expandable_on_open_posture():
    report = build_intake_capacity_report(
        intake_guard_report={"summary": {"intake_guard": "open"}},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "wide"}},
        queue_pressure_report={"summary": {"queue_pressure_band": "low"}},
    )
    assert report["summary"]["intake_capacity_mode"] == "expandable"
