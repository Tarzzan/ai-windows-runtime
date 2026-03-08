from compat_runtime.governance_checkpoint.cli import build_governance_checkpoint_report


def test_governance_checkpoint_pass():
    report = build_governance_checkpoint_report(
        stability_window_report={"summary": {"window_status": "stable"}},
        hotfix_planner_report={"summary": {"plan_mode": "routine"}},
        verification_snapshot_report={"summary": {"missing_reports": 0}},
        evidence_catalog_report={
            "summary": {
                "catalog_items": 10,
                "policy_config_valid": True,
                "policy_lockfile_sync": True,
                "policy_compliance_level": "compliant",
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
    )
    assert report["status"] == "pass"
    assert report["summary"]["policy_config_valid"] is True
    assert report["summary"]["policy_lockfile_sync"] is True
    assert report["summary"]["policy_compliance_level"] == "compliant"
    assert report["summary"]["release_policy_status"] == "pass"
    assert report["summary"]["release_policy_failures"] == 0


def test_governance_checkpoint_blocks_when_policy_is_not_synced():
    report = build_governance_checkpoint_report(
        stability_window_report={"summary": {"window_status": "stable"}},
        hotfix_planner_report={"summary": {"plan_mode": "routine"}},
        verification_snapshot_report={"summary": {"missing_reports": 0}},
        evidence_catalog_report={
            "summary": {
                "catalog_items": 10,
                "policy_config_valid": True,
                "policy_lockfile_sync": False,
                "policy_compliance_level": "degraded",
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
    )
    assert report["status"] == "block"


def test_governance_checkpoint_blocks_when_release_policy_fails():
    report = build_governance_checkpoint_report(
        stability_window_report={"summary": {"window_status": "stable"}},
        hotfix_planner_report={"summary": {"plan_mode": "routine"}},
        verification_snapshot_report={"summary": {"missing_reports": 0}},
        evidence_catalog_report={
            "summary": {
                "catalog_items": 10,
                "policy_config_valid": True,
                "policy_lockfile_sync": True,
                "policy_compliance_level": "compliant",
                "release_policy_status": "fail",
                "release_policy_failures": 2,
            }
        },
    )
    assert report["status"] == "block"
