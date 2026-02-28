from compat_runtime.stability_window.cli import build_stability_window_report


def test_stability_window_watch():
    report = build_stability_window_report(
        post_release_monitor_report={"summary": {"monitor_status": "watch"}},
        release_gate_history_report={"summary": {"trajectory": "stable"}},
        readiness_delta_report={"summary": {"readiness_score_delta": 0}},
    )
    assert report["summary"]["window_status"] == "watch"
