import json

from compat_runtime.gap_detector.cli import detect_gaps
from compat_runtime.patch_orchestrator.cli import build_patch_plan
from compat_runtime.schema_validator.cli import validate_artifact
from compat_runtime.trace_collector.cli import build_trace


def test_validator_accepts_generated_pipeline_artifacts(tmp_path):
    log_file = tmp_path / "sample.log"
    log_file.write_text("err:module:import_dll failed\n", encoding="utf-8")

    trace = build_trace(str(log_file))
    gaps = detect_gaps(trace)
    plan = build_patch_plan(gaps)

    trace_path = tmp_path / "trace.json"
    gaps_path = tmp_path / "gaps.json"
    plan_path = tmp_path / "plan.json"

    trace_path.write_text(json.dumps(trace), encoding="utf-8")
    gaps_path.write_text(json.dumps(gaps), encoding="utf-8")
    plan_path.write_text(json.dumps(plan), encoding="utf-8")

    trace_report = validate_artifact(str(trace_path), "schemas/trace.schema.json")
    gaps_report = validate_artifact(str(gaps_path), "schemas/gaps.schema.json")
    plan_report = validate_artifact(str(plan_path), "schemas/patch-plan.schema.json")

    assert trace_report["valid"] is True
    assert gaps_report["valid"] is True
    assert plan_report["valid"] is True


def test_validator_rejects_missing_required_fields(tmp_path):
    invalid_trace = {"artifact_version": "1.0", "events": [{"category": "runtime"}]}
    invalid_path = tmp_path / "invalid-trace.json"
    invalid_path.write_text(json.dumps(invalid_trace), encoding="utf-8")

    report = validate_artifact(str(invalid_path), "schemas/trace.schema.json")
    assert report["valid"] is False
    assert any("missing required field" in error for error in report["errors"])


def test_validator_supports_union_types_for_nullable_detail(tmp_path):
    telemetry = {
        "artifact_version": "1.0",
        "events": [
            {
                "seq": 1,
                "component": "win32",
                "action": "CreateProcessW",
                "stage": "Start",
                "detail": None,
            }
        ],
    }
    telemetry_path = tmp_path / "telemetry.json"
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

    report = validate_artifact(
        str(telemetry_path),
        "schemas/runtime-telemetry.schema.json",
    )
    assert report["valid"] is True
