from compat_runtime.release_gate_history.cli import build_release_gate_history_report


def test_release_gate_history_builds_snapshots():
    report = build_release_gate_history_report(
        dashboard_timeseries={
            "points": [
                {
                    "index": 1,
                    "generated_at": "2026-01-01T00:00:00+00:00",
                    "status": "ok",
                    "base_gaps": 4,
                    "runtime_gaps": 2,
                }
            ]
        },
        trend_report={"summary": {"improved_metrics": ["a"], "regressed_metrics": ["b", "c"]}},
        quality_gate_report={"gate": "fail"},
        release_decision_report={"decision": "no-go"},
        readiness_scorecard_report={"score": 10, "band": "red"},
    )

    assert report["summary"]["snapshots"] == 2
    assert report["summary"]["trajectory"] == "degrading"
    assert report["snapshots"]
    assert report["actions"]


def test_release_gate_history_handles_stable_trend():
    report = build_release_gate_history_report(
        dashboard_timeseries={"points": []},
        trend_report={"summary": {"improved_metrics": [], "regressed_metrics": []}},
        quality_gate_report={"gate": "pass"},
        release_decision_report={"decision": "go"},
        readiness_scorecard_report={"score": 88, "band": "green"},
    )
    assert report["summary"]["trajectory"] == "stable"
