from compat_runtime.capacity_buffer.cli import build_capacity_buffer_report


def test_capacity_buffer_low_when_reserve_protected_and_overload_present():
    report = build_capacity_buffer_report(
        execution_reserve_report={"summary": {"execution_reserve": "protected"}},
        owner_load_report={"summary": {"overloaded_owners": 1}},
        backlog_refresh_report={"summary": {"refreshed_items": 8}},
    )
    assert report["summary"]["capacity_buffer_band"] == "low"


def test_capacity_buffer_high_with_surplus_and_no_overload():
    report = build_capacity_buffer_report(
        execution_reserve_report={"summary": {"execution_reserve": "surplus"}},
        owner_load_report={"summary": {"overloaded_owners": 0}},
        backlog_refresh_report={"summary": {"refreshed_items": 2}},
    )
    assert report["summary"]["capacity_buffer_band"] == "high"
