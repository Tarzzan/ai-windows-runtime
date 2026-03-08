from compat_runtime.portfolio_risk_budget.cli import build_portfolio_risk_budget_report


def test_portfolio_risk_budget_conservative_with_strict_guard_and_p0_pressure():
    report = build_portfolio_risk_budget_report(
        commitment_guard_report={"summary": {"commitment_guard": "strict"}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
        readiness_scorecard_report={"score": 62},
    )
    assert report["summary"]["risk_budget_mode"] == "conservative"


def test_portfolio_risk_budget_aggressive_on_adaptive_and_low_risk():
    report = build_portfolio_risk_budget_report(
        commitment_guard_report={"summary": {"commitment_guard": "adaptive"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
        readiness_scorecard_report={"score": 90},
    )
    assert report["summary"]["risk_budget_mode"] == "aggressive"
