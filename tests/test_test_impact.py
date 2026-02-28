from compat_runtime.test_impact.cli import build_test_impact_report


def _patch_plan(proposals: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": proposals}


def _gaps(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "gaps": items}


def test_test_impact_builds_priority_suites():
    patch_plan = _patch_plan(
        [
            {"gap_id": "gap-loader", "priority": "P0", "title": "Loader fix"},
            {"gap_id": "gap-network", "priority": "P1", "title": "Network fix"},
        ]
    )
    gaps = _gaps(
        [
            {"id": "gap-loader", "category": "loader", "severity": "high"},
            {"id": "gap-network", "category": "network", "severity": "medium"},
        ]
    )
    provenance = {"summary": {"weak_provenance_entries": 1}}
    root_cause = {
        "root_cause_clusters": [
            {"category": "loader", "count": 2},
            {"category": "network", "count": 1},
        ]
    }

    report = build_test_impact_report(
        patch_plan=patch_plan,
        gaps=gaps,
        root_cause=root_cause,
        proposal_provenance=provenance,
    )

    assert report["summary"]["total_proposals"] == 2
    assert report["summary"]["high_priority_suites"] >= 1
    assert report["summary"]["weak_provenance_entries"] == 1
    assert any(suite["id"] == "pe-loader-regression" for suite in report["suites"])
    assert report["coverage"]["root_cause_alignment"]
    assert report["actions"]


def test_test_impact_keeps_smoke_when_no_proposals():
    report = build_test_impact_report(
        patch_plan=_patch_plan([]),
        gaps=_gaps([]),
    )

    assert report["summary"]["total_proposals"] == 0
    assert any(suite["id"] == "runtime-smoke-suite" for suite in report["suites"])

