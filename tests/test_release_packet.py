from compat_runtime.release_packet.cli import build_release_packet_report


def test_release_packet_ready_when_manifest_complete():
    report = build_release_packet_report(
        launch_readiness_report={"status": "limited", "summary": {"release_decision": "hold"}},
        release_bundle_manifest={"files": [{"path": "a"}], "missing": []},
        stakeholder_update_report={"summary": {"delivery_status": "watch"}},
        policy_health_report={"config_valid": True, "lockfile_sync": True},
    )
    assert report["summary"]["packet_ready"] is True
    assert report["summary"]["policy_config_valid"] is True
    assert report["summary"]["policy_lockfile_sync"] is True
