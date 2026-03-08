from compat_runtime.throughput_guard_band.cli import build_throughput_guard_band_report


def test_throughput_guard_band_tight_when_scope_locked():
    report = build_throughput_guard_band_report(
        scope_lock_state_report={"summary": {"scope_lock_state": "locked"}},
        delivery_safety_margin_report={"summary": {"safety_margin_score": 10}},
        execution_reserve_report={"summary": {"execution_reserve": "protected"}},
    )
    assert report["summary"]["throughput_guard_band"] == "tight"


def test_throughput_guard_band_wide_when_scope_flexible():
    report = build_throughput_guard_band_report(
        scope_lock_state_report={"summary": {"scope_lock_state": "flexible"}},
        delivery_safety_margin_report={"summary": {"safety_margin_score": 90}},
        execution_reserve_report={"summary": {"execution_reserve": "surplus"}},
    )
    assert report["summary"]["throughput_guard_band"] == "wide"
