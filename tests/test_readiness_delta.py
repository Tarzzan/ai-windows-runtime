from compat_runtime.readiness_delta.cli import build_readiness_delta_report


def test_readiness_delta_computed():
    report = build_readiness_delta_report(
        launch_readiness_report={"status": "limited", "summary": {"release_decision": "hold"}},
        delivery_cockpit_report={"summary": {"cockpit_status": "watch", "readiness_score": 70}},
        release_gate_history_report={"summary": {"trajectory": "stable", "latest_readiness_score": 60}},
    )
    assert report["summary"]["readiness_score_delta"] == 10
