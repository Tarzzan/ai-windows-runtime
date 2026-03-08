from compat_runtime.execution_reserve.cli import build_execution_reserve_report


def test_execution_reserve_protected_when_blocked_or_overloaded():
    report = build_execution_reserve_report(
        delivery_intake_sync_report={"summary": {"delivery_intake_sync": "blocked"}},
        scope_budget_report={"summary": {"scope_budget_mode": "tight"}},
        owner_load_report={"summary": {"overloaded_owners": 1}},
    )
    assert report["summary"]["execution_reserve"] == "protected"


def test_execution_reserve_surplus_on_expanding_flexible_no_overload():
    report = build_execution_reserve_report(
        delivery_intake_sync_report={"summary": {"delivery_intake_sync": "expanding"}},
        scope_budget_report={"summary": {"scope_budget_mode": "flexible"}},
        owner_load_report={"summary": {"overloaded_owners": 0}},
    )
    assert report["summary"]["execution_reserve"] == "surplus"
