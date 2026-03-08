from compat_runtime.scope_budget.cli import build_scope_budget_report


def test_scope_budget_tight_with_stabilize_and_long_forecast():
    report = build_scope_budget_report(
        commitment_pacing_report={"summary": {"commitment_mode": "stabilize"}},
        readiness_scorecard_report={"score": 55},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 6}},
    )
    assert report["summary"]["scope_budget_mode"] == "tight"


def test_scope_budget_flexible_with_expand_and_short_forecast():
    report = build_scope_budget_report(
        commitment_pacing_report={"summary": {"commitment_mode": "expand"}},
        readiness_scorecard_report={"score": 88},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 1}},
    )
    assert report["summary"]["scope_budget_mode"] == "flexible"
