from compat_runtime.delivery_signoff.cli import build_delivery_signoff_report


def test_delivery_signoff_approved():
    report = build_delivery_signoff_report(
        release_packet_report={
            "summary": {
                "packet_ready": True,
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
        ops_runbook_report={"summary": {"runbook_readiness": "operational"}},
        dependency_watch_report={"summary": {"dependencies_blocking": 0}},
        readiness_delta_report={"summary": {"readiness_score_delta": 1}},
        launch_readiness_report={"status": "ready"},
    )
    assert report["status"] == "approved"
    assert report["summary"]["release_policy_status"] == "pass"
    assert report["summary"]["release_policy_failures"] == 0


def test_delivery_signoff_blocked_when_release_policy_failed():
    report = build_delivery_signoff_report(
        release_packet_report={
            "summary": {
                "packet_ready": True,
                "release_policy_status": "fail",
                "release_policy_failures": 2,
            }
        },
        ops_runbook_report={"summary": {"runbook_readiness": "operational"}},
        dependency_watch_report={"summary": {"dependencies_blocking": 0}},
        readiness_delta_report={"summary": {"readiness_score_delta": 1}},
        launch_readiness_report={"status": "ready"},
    )
    assert report["status"] == "blocked"
