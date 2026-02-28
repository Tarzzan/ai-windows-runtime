from compat_runtime.readiness_scorecard.cli import build_readiness_scorecard_report


def _quality(gate: str) -> dict:
    return {"gate": gate}


def _decision(decision: str) -> dict:
    return {"decision": decision}


def _iteration(blocking: int) -> dict:
    return {"summary": {"blocking_tasks": blocking}}


def _forecast(iterations: int) -> dict:
    return {"summary": {"estimated_iterations_to_go": iterations}}


def _kpi(level: str) -> dict:
    return {"summary": {"risk_level": level}}


def test_readiness_scorecard_red_for_no_go_context():
    report = build_readiness_scorecard_report(
        quality_gate_report=_quality("fail"),
        release_decision_report=_decision("no-go"),
        iteration_plan_report=_iteration(7),
        release_forecast_report=_forecast(6),
        kpi_report=_kpi("high"),
    )

    assert report["score"] < 50
    assert report["band"] == "red"
    assert report["release_candidate"] is False
    assert report["factors"]
    assert report["actions"]


def test_readiness_scorecard_green_for_go_context():
    report = build_readiness_scorecard_report(
        quality_gate_report=_quality("pass"),
        release_decision_report=_decision("go"),
        iteration_plan_report=_iteration(0),
        release_forecast_report=_forecast(1),
        kpi_report=_kpi("low"),
    )

    assert report["score"] >= 80
    assert report["band"] == "green"
    assert report["release_candidate"] is True
