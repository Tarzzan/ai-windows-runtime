from compat_runtime.scope_expansion_readiness.cli import build_scope_expansion_readiness_report


def test_scope_expansion_readiness_blocked_with_locked_unlock_and_p0_pressure():
    report = build_scope_expansion_readiness_report(
        scope_unlock_gate_report={"summary": {"scope_unlock_gate": "locked"}},
        scope_reentry_readiness_report={"summary": {"scope_reentry_readiness_score": 30}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
    )
    assert report["summary"]["scope_expansion_readiness_band"] == "blocked"


def test_scope_expansion_readiness_ready_with_unlocked_gate_and_no_p0():
    report = build_scope_expansion_readiness_report(
        scope_unlock_gate_report={"summary": {"scope_unlock_gate": "unlocked"}},
        scope_reentry_readiness_report={"summary": {"scope_reentry_readiness_score": 85}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["scope_expansion_readiness_band"] == "ready"
