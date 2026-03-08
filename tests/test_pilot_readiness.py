from compat_runtime.pilot_readiness.cli import build_pilot_readiness_report


def test_pilot_readiness_not_ready_with_blockers():
    report = build_pilot_readiness_report(
        productization_readiness={"ready": True},
        quality_gate_report={"gate": "fail"},
        release_decision_report={
            "decision": "no-go",
            "checks": [{"id": "quality_gate", "required": True, "status": "fail"}],
        },
        readiness_scorecard_report={"score": 20, "band": "red"},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 6}},
        iteration_plan_report={"summary": {"blocking_tasks": 7}},
        risk_watchlist_report={"summary": {"p0_entries": 3}},
    )

    assert report["recommendation"] == "not_ready"
    assert report["blockers"] == ["quality_gate"]
    assert report["actions"]


def test_pilot_readiness_ready_when_signals_are_green():
    report = build_pilot_readiness_report(
        productization_readiness={"ready": True},
        quality_gate_report={"gate": "pass"},
        release_decision_report={"decision": "go", "checks": []},
        readiness_scorecard_report={"score": 90, "band": "green"},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 1}},
        iteration_plan_report={"summary": {"blocking_tasks": 0}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )

    assert report["recommendation"] == "ready"


def test_pilot_readiness_limited_pilot_for_alpha_window():
    report = build_pilot_readiness_report(
        productization_readiness={"ready": True},
        quality_gate_report={"gate": "warn"},
        release_decision_report={"decision": "go", "checks": []},
        readiness_scorecard_report={"score": 67, "band": "amber"},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 4}},
        iteration_plan_report={"summary": {"blocking_tasks": 4}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
    )

    assert report["recommendation"] == "limited_pilot"
