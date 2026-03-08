from compat_runtime.scope_lock_state.cli import build_scope_lock_state_report


def test_scope_lock_state_locked_when_commitment_locked():
    report = build_scope_lock_state_report(
        intake_commitment_window_report={"summary": {"intake_commitment_window": "locked"}},
        scope_rebalance_report={"summary": {"scope_rebalance": "hold"}},
        risk_watchlist_report={"summary": {"p0_entries": 1}},
    )
    assert report["summary"]["scope_lock_state"] == "locked"


def test_scope_lock_state_flexible_when_open_no_p0():
    report = build_scope_lock_state_report(
        intake_commitment_window_report={"summary": {"intake_commitment_window": "open"}},
        scope_rebalance_report={"summary": {"scope_rebalance": "expand"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["scope_lock_state"] == "flexible"
