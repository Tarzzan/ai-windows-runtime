from compat_runtime.evidence_catalog.cli import build_evidence_catalog_report


def test_evidence_catalog_lists_artifacts():
    report = build_evidence_catalog_report(
        verification_snapshot_report={"summary": {"coverage_ratio": 1.0}},
        release_packet_report={"summary": {"packet_ready": True, "bundle_missing": 0}},
        repro_package={"artifacts": [{"path": "a", "exists": True, "sha256": "x"}]},
    )
    assert report["summary"]["catalog_items"] == 1
