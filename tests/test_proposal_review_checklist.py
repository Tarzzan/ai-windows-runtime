from compat_runtime.proposal_review_checklist.cli import build_proposal_review_checklist


def _patch_plan(proposals: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": proposals}


def test_review_checklist_flags_required_failures():
    patch_plan = _patch_plan([{"gap_id": "gap-1", "priority": "P0", "risk": "high"}])
    provenance = {
        "proposals": [
            {
                "gap_id": "gap-1",
                "gap": {"found": True},
                "provenance": {"provenance_score": 0.9},
            }
        ]
    }
    diff = {"added": [{"gap_id": "gap-1"}], "changed": []}
    test_impact = {"summary": {"suggested_suites": 2}}
    rollback = {"summary": {"total_hints": 1}, "hints": [{"gap_id": "gap-1", "rollback_level": "full"}]}

    report = build_proposal_review_checklist(
        patch_plan=patch_plan,
        proposal_provenance=provenance,
        patch_plan_diff=diff,
        test_impact=test_impact,
        rollback_hints=rollback,
    )

    assert report["summary"]["proposal_count"] == 1
    assert report["summary"]["required_failures"] == 0
    assert report["ready_for_approval"] is True
    assert any(item["status"] == "todo" for item in report["items"])


def test_review_checklist_detects_missing_coverage():
    patch_plan = _patch_plan([{"gap_id": "gap-x", "priority": "P1", "risk": "medium"}])

    report = build_proposal_review_checklist(patch_plan=patch_plan)
    assert report["ready_for_approval"] is False
    assert report["summary"]["required_failures"] >= 1
    assert report["actions"]

