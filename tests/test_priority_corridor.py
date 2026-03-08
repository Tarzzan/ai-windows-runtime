from compat_runtime.priority_corridor.cli import build_priority_corridor_report


def test_priority_corridor_p0_only_under_tight_throttle():
    report = build_priority_corridor_report(
        execution_throttle_report={"summary": {"throttle_mode": "tight"}},
        execution_focus_report={"summary": {"p0_focus_items": 4}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
    )
    assert report["summary"]["priority_corridor"] == "p0_only"


def test_priority_corridor_full_when_no_p0_and_open():
    report = build_priority_corridor_report(
        execution_throttle_report={"summary": {"throttle_mode": "open"}},
        execution_focus_report={"summary": {"p0_focus_items": 0}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["priority_corridor"] == "full"
