from compat_runtime.kpi_tracker.cli import build_dashboard_timeseries, build_kpi_report


def _report(status: str, base_gaps: int, runtime_gaps: int) -> dict:
    return {
        "artifact_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
        "status": status,
        "pipeline": {
            "base": {
                "trace_events": 4,
                "gaps": base_gaps,
                "proposals": base_gaps,
                "validation": {"trace": True, "gaps": True, "patch_plan": True},
            },
            "runtime": {
                "trace_events": 3,
                "gaps": runtime_gaps,
                "proposals": runtime_gaps,
                "validation": {"trace": True},
            },
        },
    }


def test_kpi_report_computes_rates_and_risk():
    reports = [_report("failed", 3, 2), _report("ok", 1, 1)]
    trend = {
        "summary": {
            "improved_metrics": ["base_gaps"],
            "regressed_metrics": ["runtime_gaps"],
        }
    }

    report = build_kpi_report(reports, trend_report=trend)
    assert report["summary"]["total_runs"] == 2
    assert report["summary"]["ok_runs"] == 1
    assert report["summary"]["ok_rate"] == 0.5
    assert report["summary"]["risk_level"] == "medium"
    assert report["metrics"]["avg_base_gaps"] == 2.0
    assert report["metrics"]["improved_metrics_count"] == 1
    assert report["metrics"]["regressed_metrics_count"] == 1
    assert report["actions"]


def test_dashboard_timeseries_exports_points():
    reports = [_report("ok", 2, 1), _report("ok", 1, 1)]
    timeseries = build_dashboard_timeseries(reports, ["a.json", "b.json"])

    assert len(timeseries["points"]) == 2
    assert timeseries["points"][0]["path"] == "a.json"
    assert timeseries["points"][1]["base_gaps"] == 1
