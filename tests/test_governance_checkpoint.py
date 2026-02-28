from compat_runtime.governance_checkpoint.cli import build_governance_checkpoint_report


def test_governance_checkpoint_pass():
    report = build_governance_checkpoint_report(
        stability_window_report={"summary": {"window_status": "stable"}},
        hotfix_planner_report={"summary": {"plan_mode": "routine"}},
        verification_snapshot_report={"summary": {"missing_reports": 0}},
        evidence_catalog_report={"summary": {"catalog_items": 10}},
    )
    assert report["status"] == "pass"
