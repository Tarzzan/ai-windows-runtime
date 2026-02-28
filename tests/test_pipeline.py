from compat_runtime.gap_detector.cli import detect_gaps
from compat_runtime.patch_orchestrator.cli import build_patch_plan
from compat_runtime.trace_collector.cli import build_trace


def test_pipeline_detects_high_impact_events(tmp_path):
    log_file = tmp_path / "sample.log"
    log_file.write_text(
        "err:module:import_dll failed\n"
        "err:ole:CoCreateInstance failed\n"
        "fixme:winhttp:stub\n",
        encoding="utf-8",
    )

    trace = build_trace(str(log_file))
    gaps = detect_gaps(trace)
    plan = build_patch_plan(gaps)

    assert len(trace["events"]) == 3
    assert len(gaps["gaps"]) >= 2
    assert len(plan["proposals"]) == len(gaps["gaps"])
    assert any(p["priority"] == "P0" for p in plan["proposals"])
