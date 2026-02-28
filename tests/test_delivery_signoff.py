from compat_runtime.delivery_signoff.cli import build_delivery_signoff_report


def test_delivery_signoff_approved():
    report = build_delivery_signoff_report(
        release_packet_report={"summary": {"packet_ready": True}},
        ops_runbook_report={"summary": {"runbook_readiness": "operational"}},
        dependency_watch_report={"summary": {"dependencies_blocking": 0}},
        readiness_delta_report={"summary": {"readiness_score_delta": 1}},
        launch_readiness_report={"status": "ready"},
    )
    assert report["status"] == "approved"
