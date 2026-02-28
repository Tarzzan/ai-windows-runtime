import json

from compat_runtime.reporting.cli import build_execution_report


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_execution_report_marks_ok_when_validations_pass(tmp_path):
    trace = tmp_path / "trace.json"
    gaps = tmp_path / "gaps.json"
    plan = tmp_path / "plan.json"
    trace_v = tmp_path / "trace-v.json"
    gaps_v = tmp_path / "gaps-v.json"
    plan_v = tmp_path / "plan-v.json"
    runtime_trace = tmp_path / "runtime-trace.json"
    runtime_gaps = tmp_path / "runtime-gaps.json"
    runtime_plan = tmp_path / "runtime-plan.json"
    runtime_v = tmp_path / "runtime-v.json"

    _write(trace, {"artifact_version": "1.0", "events": [{}, {}]})
    _write(gaps, {"artifact_version": "1.0", "gaps": [{}]})
    _write(plan, {"artifact_version": "1.0", "proposals": [{}]})
    _write(trace_v, {"valid": True})
    _write(gaps_v, {"valid": True})
    _write(plan_v, {"valid": True})
    _write(runtime_trace, {"artifact_version": "1.0", "events": [{}, {}, {}]})
    _write(runtime_gaps, {"artifact_version": "1.0", "gaps": [{}, {}]})
    _write(runtime_plan, {"artifact_version": "1.0", "proposals": [{}, {}]})
    _write(runtime_v, {"valid": True})

    report = build_execution_report(
        trace_path=str(trace),
        gaps_path=str(gaps),
        patch_plan_path=str(plan),
        trace_validation_path=str(trace_v),
        gaps_validation_path=str(gaps_v),
        patch_plan_validation_path=str(plan_v),
        runtime_trace_path=str(runtime_trace),
        runtime_gaps_path=str(runtime_gaps),
        runtime_patch_plan_path=str(runtime_plan),
        runtime_trace_validation_path=str(runtime_v),
    )

    assert report["pipeline"]["base"]["trace_events"] == 2
    assert report["pipeline"]["runtime"]["trace_events"] == 3
    assert report["status"] == "ok"


def test_execution_report_marks_failed_on_validation_errors(tmp_path):
    trace = tmp_path / "trace.json"
    gaps = tmp_path / "gaps.json"
    plan = tmp_path / "plan.json"
    trace_v = tmp_path / "trace-v.json"
    gaps_v = tmp_path / "gaps-v.json"
    plan_v = tmp_path / "plan-v.json"

    _write(trace, {"artifact_version": "1.0", "events": [{}]})
    _write(gaps, {"artifact_version": "1.0", "gaps": []})
    _write(plan, {"artifact_version": "1.0", "proposals": []})
    _write(trace_v, {"valid": True})
    _write(gaps_v, {"valid": False})
    _write(plan_v, {"valid": True})

    report = build_execution_report(
        trace_path=str(trace),
        gaps_path=str(gaps),
        patch_plan_path=str(plan),
        trace_validation_path=str(trace_v),
        gaps_validation_path=str(gaps_v),
        patch_plan_validation_path=str(plan_v),
    )

    assert report["pipeline"]["runtime"]["trace_events"] == 0
    assert report["status"] == "failed"
