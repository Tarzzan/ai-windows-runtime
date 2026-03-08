from compat_runtime.flow_control_budget.cli import build_flow_control_budget_report


def test_flow_control_budget_tight_for_reduce_and_low_buffer():
    report = build_flow_control_budget_report(
        scope_rebalance_report={"summary": {"scope_rebalance": "reduce"}},
        capacity_buffer_report={"summary": {"capacity_buffer_score": 10}},
        execution_reserve_report={"summary": {"execution_reserve": "protected"}},
    )
    assert report["summary"]["flow_control_mode"] == "tight"


def test_flow_control_budget_open_for_expand_and_surplus():
    report = build_flow_control_budget_report(
        scope_rebalance_report={"summary": {"scope_rebalance": "expand"}},
        capacity_buffer_report={"summary": {"capacity_buffer_score": 90}},
        execution_reserve_report={"summary": {"execution_reserve": "surplus"}},
    )
    assert report["summary"]["flow_control_mode"] == "open"
