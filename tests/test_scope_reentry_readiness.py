from compat_runtime.scope_reentry_readiness.cli import build_scope_reentry_readiness_report


def test_scope_reentry_readiness_blocked_with_closed_gate_and_p0_pressure():
    report = build_scope_reentry_readiness_report(
        scope_admission_gate_report={"summary": {"scope_admission_gate": "closed"}},
        transition_readiness_index_report={"summary": {"transition_readiness_score": 30}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
    )
    assert report["summary"]["scope_reentry_readiness_band"] == "blocked"


def test_scope_reentry_readiness_ready_with_open_gate_and_no_p0():
    report = build_scope_reentry_readiness_report(
        scope_admission_gate_report={"summary": {"scope_admission_gate": "open"}},
        transition_readiness_index_report={"summary": {"transition_readiness_score": 85}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["scope_reentry_readiness_band"] == "ready"
