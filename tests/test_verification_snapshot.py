from compat_runtime.verification_snapshot.cli import build_verification_snapshot_report


def test_verification_snapshot_contains_coverage():
    report = build_verification_snapshot_report(
        validation_coverage_report={"summary": {"coverage_ratio": 1.0, "missing_reports": 0}},
        next_cycle_bootstrap_report={"status": "ready", "summary": {"bootstrap_commands": 4}},
        delivery_signoff_report={"status": "approved", "summary": {"dependency_blockers": 0}},
    )
    assert report["summary"]["coverage_ratio"] == 1.0
