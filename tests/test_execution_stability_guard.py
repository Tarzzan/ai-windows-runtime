from compat_runtime.execution_stability_guard.cli import build_execution_stability_guard_report


def test_execution_stability_guard_strict_with_closed_window():
    report = build_execution_stability_guard_report(
        intake_release_window_report={"summary": {"intake_release_window": "closed"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
        post_release_monitor_report={"summary": {"monitor_status": "stable"}},
    )
    assert report["summary"]["execution_stability_guard"] == "strict"


def test_execution_stability_guard_normal_with_open_and_low_risk():
    report = build_execution_stability_guard_report(
        intake_release_window_report={"summary": {"intake_release_window": "open"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
        post_release_monitor_report={"summary": {"monitor_status": "stable"}},
    )
    assert report["summary"]["execution_stability_guard"] == "normal"
