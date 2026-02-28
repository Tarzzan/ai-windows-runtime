from compat_runtime.gap_detector.cli import detect_gaps
from compat_runtime.patch_orchestrator.cli import build_patch_plan
from compat_runtime.telemetry_adapter.cli import build_trace_from_runtime_telemetry
from compat_runtime.trace_collector.cli import build_trace


def sample_telemetry() -> dict:
    return {
        "artifact_version": "1.0",
        "events": [
            {
                "seq": 1,
                "component": "win32",
                "action": "CreateProcessW",
                "stage": "Start",
                "detail": None,
            },
            {
                "seq": 2,
                "component": "win32",
                "action": "CreateProcessW",
                "stage": "Success",
                "detail": "process",
            },
            {
                "seq": 3,
                "component": "win32",
                "action": "RegQueryValueExW",
                "stage": "Error",
                "detail": "registry value not found",
            },
        ],
    }


def test_telemetry_adapter_merges_with_base_trace(tmp_path):
    log_file = tmp_path / "sample.log"
    log_file.write_text("fixme:winhttp:stub\n", encoding="utf-8")

    base_trace = build_trace(str(log_file))
    telemetry_trace = build_trace_from_runtime_telemetry(
        sample_telemetry(),
        base_trace=base_trace,
    )

    assert len(telemetry_trace["events"]) == 4
    assert telemetry_trace["events"][-1]["category"] == "registry"
    assert telemetry_trace["events"][-1]["severity"] == "high"
    assert telemetry_trace["events"][-1]["source"] == "runtime-telemetry"


def test_telemetry_adapter_errors_flow_to_gap_and_patch_plan():
    trace = build_trace_from_runtime_telemetry(sample_telemetry(), errors_only=True)
    gaps = detect_gaps(trace)
    plan = build_patch_plan(gaps)

    assert len(trace["events"]) == 1
    assert trace["events"][0]["category"] == "registry"
    assert len(gaps["gaps"]) == 1
    assert gaps["gaps"][0]["category"] == "registry"
    assert plan["proposals"][0]["priority"] == "P1"
