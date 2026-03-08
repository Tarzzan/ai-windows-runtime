from compat_runtime.post_release_monitor.cli import build_post_release_monitor_report


def test_post_release_monitor_watch_status():
    report = build_post_release_monitor_report(
        delivery_signoff_report={
            "status": "conditional",
            "summary": {"release_policy_status": "pass", "release_policy_failures": 0},
        },
        runtime_signal_report={"summary": {"missing_hooks": 2, "total_events": 12}},
        crash_signature_report={"summary": {"high_priority_signatures": 0}},
    )
    assert report["summary"]["monitor_status"] == "watch"
    assert report["summary"]["release_policy_status"] == "pass"


def test_post_release_monitor_critical_when_release_policy_failed():
    report = build_post_release_monitor_report(
        delivery_signoff_report={
            "status": "conditional",
            "summary": {"release_policy_status": "fail", "release_policy_failures": 1},
        },
        runtime_signal_report={"summary": {"missing_hooks": 0, "total_events": 12}},
        crash_signature_report={"summary": {"high_priority_signatures": 0}},
    )
    assert report["summary"]["monitor_status"] == "critical"
