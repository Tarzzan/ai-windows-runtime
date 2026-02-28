import json

from compat_runtime.repro_package.cli import build_repro_package


def _execution_report(status: str) -> dict:
    return {
        "artifact_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": status,
        "pipeline": {
            "base": {
                "trace_events": 5,
                "gaps": 2,
                "proposals": 2,
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


def _matrix(status: str) -> dict:
    return {
        "artifact_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "release_ready": status == "pass",
        "summary": {"execution_status": "ok"},
        "scenarios": [
            {
                "id": "runtime-telemetry-sample",
                "status": status,
                "gaps": 1,
                "proposals": 1,
                "evidence": "out/runtime-trace.json",
            }
        ],
    }


def _checklist(status: str) -> dict:
    return {
        "artifact_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "release_ready": status == "pass",
        "summary": {"required_failures": 0 if status == "pass" else 1},
        "items": [
            {
                "id": "pipeline_green",
                "title": "Pipeline complet vert",
                "required": True,
                "status": status,
                "evidence": "out/execution-report.json",
            }
        ],
    }


def test_repro_package_collects_failures_and_artifact_hashes(tmp_path):
    existing = tmp_path / "execution-report.json"
    existing.write_text(json.dumps({"ok": False}), encoding="utf-8")

    package = build_repro_package(
        _execution_report("failed"),
        _matrix("fail"),
        alpha_checklist=_checklist("fail"),
        artifacts=[str(existing), str(tmp_path / "missing.json")],
    )

    assert package["ready_for_repro"] is True
    assert package["summary"]["failure_count"] >= 2
    assert package["summary"]["existing_artifacts"] == 1
    assert package["summary"]["missing_artifacts"] == 1
    assert package["deterministic_id"]
    assert package["artifacts"][0]["sha256"]
    assert "scripts/run-full-pipeline.sh out" in package["reproduction_steps"][
        "recommended_commands"
    ]


def test_repro_package_stays_empty_when_all_green(tmp_path):
    existing = tmp_path / "execution-report.json"
    existing.write_text(json.dumps({"ok": True}), encoding="utf-8")

    package = build_repro_package(
        _execution_report("ok"),
        _matrix("pass"),
        alpha_checklist=_checklist("pass"),
        artifacts=[str(existing)],
    )

    assert package["ready_for_repro"] is False
    assert package["summary"]["failure_count"] == 0

