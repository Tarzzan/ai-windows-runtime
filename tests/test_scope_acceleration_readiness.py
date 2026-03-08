from compat_runtime.scope_acceleration_readiness.cli import build_scope_acceleration_readiness_report


def test_scope_acceleration_readiness_blocked_when_expansion_closed_and_p0_high():
    report = build_scope_acceleration_readiness_report(
        scope_expansion_gate_report={"summary": {"scope_expansion_gate": "closed"}},
        scope_expansion_readiness_report={"summary": {"scope_expansion_readiness_score": 35}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
    )
    assert report["summary"]["scope_acceleration_readiness_band"] == "blocked"


def test_scope_acceleration_readiness_ready_when_expansion_open_and_no_p0():
    report = build_scope_acceleration_readiness_report(
        scope_expansion_gate_report={"summary": {"scope_expansion_gate": "open"}},
        scope_expansion_readiness_report={"summary": {"scope_expansion_readiness_score": 85}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["scope_acceleration_readiness_band"] == "ready"
