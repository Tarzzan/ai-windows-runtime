from compat_runtime.rollback_hints.cli import build_rollback_hints


def _patch_plan(proposals: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": proposals}


def _gaps(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "gaps": items}


def test_rollback_hints_assigns_levels_and_actions():
    patch_plan = _patch_plan(
        [
            {"gap_id": "gap-loader", "priority": "P0", "risk": "high"},
            {"gap_id": "gap-file", "priority": "P2", "risk": "low"},
        ]
    )
    gaps = _gaps(
        [
            {"id": "gap-loader", "category": "loader"},
            {"id": "gap-file", "category": "file"},
        ]
    )
    test_impact = {"summary": {"suggested_suites": 4}}

    report = build_rollback_hints(
        patch_plan=patch_plan,
        gaps=gaps,
        test_impact=test_impact,
    )

    assert report["summary"]["total_hints"] == 2
    assert report["summary"]["full_rollbacks"] == 1
    assert report["summary"]["minimal_rollbacks"] == 1
    assert report["summary"]["highest_priority"] == "P0"
    assert report["summary"]["suggested_suites"] == 4
    assert report["hints"][0]["validation_commands"]
    assert report["actions"]


def test_rollback_hints_handles_empty_plan():
    report = build_rollback_hints(
        patch_plan=_patch_plan([]),
        gaps=_gaps([]),
    )
    assert report["summary"]["total_hints"] == 0
    assert report["hints"] == []
    assert report["actions"]

