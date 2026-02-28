from compat_runtime.proposal_provenance.cli import build_proposal_provenance


def _patch_plan(proposals: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": proposals}


def _gaps(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "gaps": items}


def _trace(events: list[dict]) -> dict:
    return {"artifact_version": "1.0", "events": events}


def test_proposal_provenance_links_gap_and_trace_evidence():
    patch_plan = _patch_plan(
        [
            {
                "gap_id": "gap-1",
                "priority": "P0",
                "title": "Fix loader",
                "risk": "high",
                "validation": "tests",
            }
        ]
    )
    gaps = _gaps(
        [
            {
                "id": "gap-1",
                "category": "loader",
                "severity": "high",
                "confidence": 0.9,
                "summary": "Loader blocker",
            }
        ]
    )
    trace = _trace(
        [
            {"category": "loader", "severity": "high", "message": "import failed"},
            {"category": "loader", "severity": "high", "message": "dll missing"},
        ]
    )

    artifact = build_proposal_provenance(patch_plan=patch_plan, gaps=gaps, trace=trace)
    assert artifact["summary"]["total_proposals"] == 1
    assert artifact["summary"]["matched_gaps"] == 1
    assert artifact["summary"]["unmatched_gaps"] == 0
    proposal = artifact["proposals"][0]
    assert proposal["gap"]["found"] is True
    assert proposal["provenance"]["trace_event_count"] == 2
    assert proposal["provenance"]["evidence_messages"]
    assert proposal["provenance"]["provenance_score"] >= 0.9


def test_proposal_provenance_marks_unmatched_gap():
    patch_plan = _patch_plan(
        [
            {
                "gap_id": "gap-missing",
                "priority": "P1",
                "title": "Investigate",
                "risk": "medium",
                "validation": "tests",
            }
        ]
    )
    gaps = _gaps([])

    artifact = build_proposal_provenance(patch_plan=patch_plan, gaps=gaps)
    assert artifact["summary"]["matched_gaps"] == 0
    assert artifact["summary"]["unmatched_gaps"] == 1
    assert artifact["proposals"][0]["gap"]["found"] is False
    assert artifact["actions"]

