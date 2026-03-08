from compat_runtime.delivery_intake_sync.cli import build_delivery_intake_sync_report


def test_delivery_intake_sync_blocked_with_restricted_window():
    report = build_delivery_intake_sync_report(
        portfolio_risk_budget_report={"summary": {"risk_budget_mode": "balanced"}},
        admission_window_report={"summary": {"admission_window": "restricted"}},
        cadence_recommendation_report={"summary": {"cadence": "moderate"}},
    )
    assert report["summary"]["delivery_intake_sync"] == "blocked"


def test_delivery_intake_sync_expanding_on_aggressive_open_fast():
    report = build_delivery_intake_sync_report(
        portfolio_risk_budget_report={"summary": {"risk_budget_mode": "aggressive"}},
        admission_window_report={"summary": {"admission_window": "open"}},
        cadence_recommendation_report={"summary": {"cadence": "fast"}},
    )
    assert report["summary"]["delivery_intake_sync"] == "expanding"
