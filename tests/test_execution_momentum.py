from compat_runtime.execution_momentum.cli import build_execution_momentum_report


def test_execution_momentum_fragile_when_degrading_and_loaded():
    report = build_execution_momentum_report(
        execution_confidence_report={"summary": {"confidence_score": 45, "confidence_band": "medium", "execution_mode": "controlled", "p0_entries": 3}},
        execution_burndown_report={"summary": {"blocking_tasks": 6}},
        release_gate_history_report={"summary": {"trajectory": "degrading"}},
        incident_feedback_report={"summary": {"p0_feedback": 2}},
    )

    assert report["summary"]["posture"] == "fragile"
    assert report["summary"]["momentum_index"] < 40
    assert report["actions"]


def test_execution_momentum_advancing_when_signals_are_clean():
    report = build_execution_momentum_report(
        execution_confidence_report={"summary": {"confidence_score": 92, "confidence_band": "high", "execution_mode": "accelerate", "p0_entries": 0}},
        execution_burndown_report={"summary": {"blocking_tasks": 0}},
        release_gate_history_report={"summary": {"trajectory": "improving"}},
        incident_feedback_report={"summary": {"p0_feedback": 0}},
    )

    assert report["summary"]["posture"] == "advancing"
    assert report["summary"]["momentum_index"] >= 70
