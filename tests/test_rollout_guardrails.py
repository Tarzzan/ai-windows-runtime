from compat_runtime.rollout_guardrails.cli import build_rollout_guardrails_report


def test_rollout_guardrails_reports_stop_conditions():
    report = build_rollout_guardrails_report(
        pilot_readiness_report={"recommendation": "limited_pilot"},
        rollback_hints_report={"hints": [{"rollback_level": "full"}, {"rollback_level": "minimal"}]},
        proposal_risk_report={"summary": {"high_risk": 2}},
        crash_signature_report={"summary": {"high_priority_signatures": 1}},
    )

    assert report["summary"]["rollout_phase"] == "pilot_limited"
    assert report["summary"]["full_rollback_paths"] == 1
    assert report["stop_conditions"]
    assert report["actions"]
