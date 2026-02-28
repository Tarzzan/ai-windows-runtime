from compat_runtime.patch_template_library.cli import build_patch_template_catalog


def _gaps(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "gaps": items}


def _patch_plan(items: list[dict]) -> dict:
    return {"artifact_version": "1.0", "proposals": items}


def test_patch_template_catalog_tracks_usage_and_priorities():
    gaps = _gaps(
        [
            {"id": "gap-loader", "category": "loader"},
            {"id": "gap-network", "category": "network"},
            {"id": "gap-custom", "category": "custom"},
        ]
    )
    patch_plan = _patch_plan(
        [
            {"gap_id": "gap-loader", "priority": "P0"},
            {"gap_id": "gap-network", "priority": "P1"},
            {"gap_id": "gap-custom", "priority": "P2"},
        ]
    )

    report = build_patch_template_catalog(gaps=gaps, patch_plan=patch_plan)
    assert report["summary"]["templates_total"] >= 1
    assert report["summary"]["used_templates"] >= 1
    assert report["summary"]["mapped_gaps"] == 3
    assert report["summary"]["proposals_linked"] == 3
    assert "custom" in report["unmapped_categories"]
    assert report["actions"]


def test_patch_template_catalog_empty_input():
    report = build_patch_template_catalog(gaps=_gaps([]), patch_plan=_patch_plan([]))
    assert report["summary"]["mapped_gaps"] == 0
    assert report["summary"]["used_templates"] == 0
    assert report["templates"]

