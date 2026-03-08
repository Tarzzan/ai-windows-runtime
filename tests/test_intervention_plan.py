from compat_runtime.intervention_plan.cli import build_intervention_plan_report


def test_intervention_plan_urgent_when_p0_or_blockers_present():
    report = build_intervention_plan_report(
        control_efficiency_report={"summary": {"efficiency_band": "low", "efficiency_score": 20}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
        dependency_watch_report={"summary": {"dependencies_blocking": 1}},
    )
    assert report["summary"]["intervention_mode"] == "urgent"


def test_intervention_plan_routine_when_healthy():
    report = build_intervention_plan_report(
        control_efficiency_report={"summary": {"efficiency_band": "high", "efficiency_score": 85}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
        dependency_watch_report={"summary": {"dependencies_blocking": 0}},
    )
    assert report["summary"]["intervention_mode"] == "routine"
