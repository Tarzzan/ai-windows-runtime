from compat_runtime.trend_report.cli import build_trend_report


def _execution_report(
    *,
    status: str,
    base_trace_events: int,
    base_gaps: int,
    base_proposals: int,
    runtime_trace_events: int,
    runtime_gaps: int,
    runtime_proposals: int,
) -> dict:
    return {
        "artifact_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": status,
        "pipeline": {
            "base": {
                "trace_events": base_trace_events,
                "gaps": base_gaps,
                "proposals": base_proposals,
                "validation": {
                    "trace": True,
                    "gaps": True,
                    "patch_plan": True,
                },
            },
            "runtime": {
                "trace_events": runtime_trace_events,
                "gaps": runtime_gaps,
                "proposals": runtime_proposals,
                "validation": {"trace": True},
            },
        },
    }


def test_trend_report_detects_improvement_and_regression():
    baseline = _execution_report(
        status="failed",
        base_trace_events=4,
        base_gaps=3,
        base_proposals=3,
        runtime_trace_events=5,
        runtime_gaps=2,
        runtime_proposals=2,
    )
    current = _execution_report(
        status="ok",
        base_trace_events=4,
        base_gaps=1,
        base_proposals=1,
        runtime_trace_events=6,
        runtime_gaps=3,
        runtime_proposals=3,
    )

    report = build_trend_report(current_report=current, baseline_report=baseline)
    assert report["summary"]["status_delta"] == 1
    assert "base_gaps" in report["summary"]["improved_metrics"]
    assert "runtime_gaps" in report["summary"]["regressed_metrics"]
    assert any(metric["name"] == "base_trace_events" for metric in report["metrics"])


def test_trend_report_without_baseline_defaults_to_zero_baseline():
    current = _execution_report(
        status="ok",
        base_trace_events=3,
        base_gaps=1,
        base_proposals=1,
        runtime_trace_events=2,
        runtime_gaps=1,
        runtime_proposals=1,
    )
    report = build_trend_report(current_report=current)

    assert report["summary"]["baseline_status"] == "failed"
    assert report["summary"]["current_status"] == "ok"
    assert report["summary"]["status_delta"] == 1
