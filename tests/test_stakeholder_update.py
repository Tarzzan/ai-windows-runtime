from compat_runtime.stakeholder_update.cli import build_stakeholder_update_report


def test_stakeholder_update_highlights():
    report = build_stakeholder_update_report(
        delivery_cockpit_report={
            "summary": {
                "cockpit_status": "watch",
                "release_policy_status": "fail",
                "release_policy_failures": 2,
            }
        },
        release_brief_report={
            "summary": {"pilot_recommendation": "limited_pilot", "readiness_score": 63, "trajectory": "stable"}
        },
        risk_watchlist_report={"summary": {"p0_entries": 1}},
    )
    assert report["summary"]["delivery_status"] == "watch"
    assert report["summary"]["release_policy_status"] == "fail"
    assert report["summary"]["release_policy_failures"] == 2
    assert len(report["highlights"]) >= 2
