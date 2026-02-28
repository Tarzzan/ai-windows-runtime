from compat_runtime.release_brief.cli import build_release_brief_report


def test_release_brief_builds_headline_and_risks():
    report = build_release_brief_report(
        pilot_readiness_report={
            "recommendation": "limited_pilot",
            "summary": {"release_decision": "hold", "quality_gate": "warn", "blocking_tasks": 2},
        },
        readiness_scorecard_report={"score": 58, "band": "amber"},
        release_forecast_report={"summary": {"estimated_iterations_to_go": 3}},
        release_gate_history_report={"summary": {"trajectory": "stable"}},
        risk_watchlist_report={"summary": {"p0_entries": 1}, "entries": [{"id": "r1", "priority": "P0"}]},
    )

    assert "Pilot=limited_pilot" in report["headline"]
    assert report["summary"]["readiness_score"] == 58
    assert report["top_risks"]
    assert report["actions"]
