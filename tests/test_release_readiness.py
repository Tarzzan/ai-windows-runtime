import json

from compat_runtime.release_readiness.cli import (
    build_alpha_release_checklist,
    build_compatibility_matrix,
    build_release_bundle_manifest,
)


def _execution_report() -> dict:
    return {
        "artifact_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": "ok",
        "pipeline": {
            "base": {
                "trace_events": 4,
                "gaps": 1,
                "proposals": 1,
                "validation": {"trace": True, "gaps": True, "patch_plan": True},
            },
            "runtime": {
                "trace_events": 3,
                "gaps": 1,
                "proposals": 1,
                "validation": {"trace": True},
            },
        },
    }


def _trend_report() -> dict:
    return {"summary": {"regressed_metrics": [], "improved_metrics": ["base_gaps"]}}


def _kpi_report() -> dict:
    return {"summary": {"risk_level": "low"}}


def test_release_readiness_generates_matrix_and_checklist():
    matrix = build_compatibility_matrix(
        _execution_report(),
        trend_report=_trend_report(),
        kpi_report=_kpi_report(),
    )
    checklist = build_alpha_release_checklist(
        matrix,
        trend_report=_trend_report(),
        kpi_report=_kpi_report(),
    )

    assert matrix["release_ready"] is True
    assert all(item["status"] == "pass" for item in matrix["scenarios"])
    assert checklist["release_ready"] is True
    assert checklist["summary"]["required_failures"] == 0


def test_release_bundle_manifest_hashes_existing_files(tmp_path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"ok": True}), encoding="utf-8")
    b.write_text(json.dumps({"ok": False}), encoding="utf-8")

    manifest = build_release_bundle_manifest([str(a), str(b), str(tmp_path / "missing.json")])
    assert len(manifest["files"]) == 2
    assert len(manifest["missing"]) == 1
    assert manifest["files"][0]["sha256"]
