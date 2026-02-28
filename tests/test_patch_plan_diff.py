from compat_runtime.patch_plan_diff.cli import build_patch_plan_diff


def _plan(proposals: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": proposals}


def test_patch_plan_diff_detects_added_removed_changed():
    baseline = _plan(
        [
            {
                "gap_id": "gap-a",
                "priority": "P1",
                "title": "Title A",
                "risk": "medium",
                "validation": "tests",
            },
            {
                "gap_id": "gap-b",
                "priority": "P2",
                "title": "Title B",
                "risk": "low",
                "validation": "tests",
            },
        ]
    )
    current = _plan(
        [
            {
                "gap_id": "gap-a",
                "priority": "P0",
                "title": "Title A",
                "risk": "high",
                "validation": "tests",
            },
            {
                "gap_id": "gap-c",
                "priority": "P1",
                "title": "Title C",
                "risk": "medium",
                "validation": "tests",
            },
        ]
    )

    diff = build_patch_plan_diff(current_plan=current, baseline_plan=baseline)
    assert diff["summary"]["added"] == 1
    assert diff["summary"]["removed"] == 1
    assert diff["summary"]["changed"] == 1
    assert diff["summary"]["unchanged"] == 0
    assert diff["added"][0]["gap_id"] == "gap-c"
    assert diff["removed"][0]["gap_id"] == "gap-b"
    assert diff["changed"][0]["gap_id"] == "gap-a"
    assert "priority" in diff["changed"][0]["changed_fields"]


def test_patch_plan_diff_without_baseline_reports_all_added():
    current = _plan(
        [
            {
                "gap_id": "gap-a",
                "priority": "P1",
                "title": "Title A",
                "risk": "medium",
                "validation": "tests",
            }
        ]
    )

    diff = build_patch_plan_diff(current_plan=current)
    assert diff["summary"]["baseline_count"] == 0
    assert diff["summary"]["added"] == 1
    assert diff["summary"]["removed"] == 0
    assert diff["summary"]["changed"] == 0
    assert diff["reviewer_focus"]

