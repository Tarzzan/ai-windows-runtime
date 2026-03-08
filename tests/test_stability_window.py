from compat_runtime.stability_window.cli import build_stability_window_report


def test_stability_window_watch():
    report = build_stability_window_report(
        post_release_monitor_report={
            "summary": {
                "monitor_status": "watch",
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
        release_gate_history_report={"summary": {"trajectory": "stable"}},
        readiness_delta_report={"summary": {"readiness_score_delta": 0}},
    )
    assert report["summary"]["window_status"] == "watch"


def test_stability_window_unstable_when_release_policy_failed():
    report = build_stability_window_report(
        post_release_monitor_report={
            "summary": {
                "monitor_status": "stable",
                "release_policy_status": "fail",
                "release_policy_failures": 1,
            }
        },
        release_gate_history_report={"summary": {"trajectory": "improving"}},
        readiness_delta_report={"summary": {"readiness_score_delta": 1}},
    )
    assert report["summary"]["window_status"] == "unstable"
