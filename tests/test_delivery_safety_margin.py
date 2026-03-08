from compat_runtime.delivery_safety_margin.cli import build_delivery_safety_margin_report


def test_delivery_safety_margin_narrow_with_strict_guard():
    report = build_delivery_safety_margin_report(
        execution_stability_guard_report={"summary": {"execution_stability_guard": "strict"}},
        flow_control_budget_report={"summary": {"flow_control_score": 10}},
        capacity_buffer_report={"summary": {"capacity_buffer_score": 10}},
    )
    assert report["summary"]["safety_margin_band"] == "narrow"


def test_delivery_safety_margin_comfortable_with_normal_guard():
    report = build_delivery_safety_margin_report(
        execution_stability_guard_report={"summary": {"execution_stability_guard": "normal"}},
        flow_control_budget_report={"summary": {"flow_control_score": 90}},
        capacity_buffer_report={"summary": {"capacity_buffer_score": 80}},
    )
    assert report["summary"]["safety_margin_band"] == "comfortable"
