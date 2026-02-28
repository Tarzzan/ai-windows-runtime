from compat_runtime.release_retrospective.cli import build_release_retrospective_report


def test_release_retrospective_generates_lessons():
    report = build_release_retrospective_report(
        delivery_signoff_report={"status": "blocked", "summary": {"dependency_blockers": 1}},
        readiness_delta_report={"summary": {"readiness_score_delta": -3}},
        release_gate_history_report={"summary": {"trajectory": "degrading"}},
    )
    assert report["summary"]["signoff_status"] == "blocked"
    assert report["lessons"]
