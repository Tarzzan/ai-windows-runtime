from compat_runtime.incident_feedback.cli import build_incident_feedback_report


def test_incident_feedback_priority():
    report = build_incident_feedback_report(
        post_release_monitor_report={"summary": {"monitor_status": "critical"}},
        risk_watchlist_report={"summary": {"p0_entries": 2}},
        hook_backlog_report={"summary": {"high_urgency": 1}},
    )
    assert report["summary"]["feedback_priority"] == "P0"
