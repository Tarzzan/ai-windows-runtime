from compat_runtime.proposal_risk.cli import build_proposal_risk_report


def _patch_plan(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": items}


def test_proposal_risk_scoring_and_levels():
    patch_plan = _patch_plan(
        [
            {"gap_id": "gap-a", "priority": "P0", "risk": "high"},
            {"gap_id": "gap-b", "priority": "P2", "risk": "low"},
        ]
    )
    provenance = {
        "proposals": [
            {"gap_id": "gap-a", "provenance": {"provenance_score": 0.9}},
            {"gap_id": "gap-b", "provenance": {"provenance_score": 0.4}},
        ]
    }
    diff = {"added": [{"gap_id": "gap-a"}], "changed": []}
    test_impact = {
        "suites": [
            {"priority": "P0", "trigger_proposals": ["gap-a"]},
            {"priority": "P2", "trigger_proposals": ["gap-b"]},
        ]
    }
    rollback = {"hints": [{"gap_id": "gap-a", "rollback_level": "full"}]}

    report = build_proposal_risk_report(
        patch_plan=patch_plan,
        proposal_provenance=provenance,
        patch_plan_diff=diff,
        test_impact=test_impact,
        rollback_hints=rollback,
    )

    assert report["summary"]["total_proposals"] == 2
    assert report["summary"]["high_risk"] >= 1
    assert report["summary"]["weak_provenance"] >= 1
    assert report["proposals"][0]["drivers"]
    assert report["actions"]


def test_proposal_risk_handles_empty_input():
    report = build_proposal_risk_report(patch_plan=_patch_plan([]))
    assert report["summary"]["total_proposals"] == 0
    assert report["proposals"] == []
    assert report["actions"]

