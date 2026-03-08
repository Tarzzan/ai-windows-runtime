from compat_runtime.scope_rebalance.cli import build_scope_rebalance_report


def test_scope_rebalance_reduce_when_policy_restrictive():
    report = build_scope_rebalance_report(
        intake_queue_policy_report={"summary": {"intake_queue_policy": "restrictive"}},
        portfolio_risk_budget_report={"summary": {"risk_budget_mode": "balanced"}},
        scope_budget_report={"summary": {"scope_budget_mode": "balanced"}},
    )
    assert report["summary"]["scope_rebalance"] == "reduce"


def test_scope_rebalance_expand_when_all_conditions_open():
    report = build_scope_rebalance_report(
        intake_queue_policy_report={"summary": {"intake_queue_policy": "permissive"}},
        portfolio_risk_budget_report={"summary": {"risk_budget_mode": "aggressive"}},
        scope_budget_report={"summary": {"scope_budget_mode": "flexible"}},
    )
    assert report["summary"]["scope_rebalance"] == "expand"
