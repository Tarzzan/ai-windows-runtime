from compat_runtime.execution_focus.cli import build_execution_focus_report


def test_execution_focus_tracks_p0_items():
    report = build_execution_focus_report(
        cadence_recommendation_report={"summary": {"cadence": "slow"}},
        risk_watchlist_report={"entries": [{"id": "a", "priority": "P0", "detail": "x"}]},
        ownership_assignment_report={"owners": ["runtime"]},
    )
    assert report["summary"]["p0_focus_items"] == 1


def test_execution_focus_allows_empty_watchlist():
    report = build_execution_focus_report(
        cadence_recommendation_report={"summary": {"cadence": "moderate"}},
        risk_watchlist_report={"entries": []},
        ownership_assignment_report={"owners": ["runtime", "release"]},
    )
    assert report["summary"]["p0_focus_items"] == 0
