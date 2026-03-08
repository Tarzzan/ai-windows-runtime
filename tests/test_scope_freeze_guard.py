from compat_runtime.scope_freeze_guard.cli import build_scope_freeze_guard_report


def test_scope_freeze_guard_freeze_when_slot_minimal():
    report = build_scope_freeze_guard_report(
        intake_slot_policy_report={"summary": {"intake_slot_policy": "minimal"}},
        scope_lock_state_report={"summary": {"scope_lock_state": "controlled"}},
        risk_watchlist_report={"summary": {"p0_entries": 1}},
    )
    assert report["summary"]["scope_freeze_guard"] == "freeze"


def test_scope_freeze_guard_open_when_all_clear():
    report = build_scope_freeze_guard_report(
        intake_slot_policy_report={"summary": {"intake_slot_policy": "expanded"}},
        scope_lock_state_report={"summary": {"scope_lock_state": "flexible"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["scope_freeze_guard"] == "open"
