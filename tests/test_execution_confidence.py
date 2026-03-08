from compat_runtime.execution_confidence.cli import build_execution_confidence_report


def test_execution_confidence_stabilize_with_policy_or_risk_pressure():
    report = build_execution_confidence_report(
        readiness_scorecard_report={"score": 72},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 4}},
        risk_watchlist_report={"summary": {"p0_entries": 3, "p1_entries": 5}},
        policy_health_report={"policy_compliance_level": "non_compliant"},
    )

    assert report["summary"]["confidence_band"] in {"low", "medium"}
    assert report["summary"]["execution_mode"] == "stabilize"
    assert report["penalties"]["policy_penalty"] > 0
    assert report["actions"]


def test_execution_confidence_accelerate_when_clean_and_ready():
    report = build_execution_confidence_report(
        readiness_scorecard_report={"score": 95},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 1}},
        risk_watchlist_report={"summary": {"p0_entries": 0, "p1_entries": 0}},
        policy_health_report={"policy_compliance_level": "compliant"},
    )

    assert report["summary"]["confidence_band"] == "high"
    assert report["summary"]["execution_mode"] == "accelerate"
    assert report["penalties"]["policy_penalty"] == 0
