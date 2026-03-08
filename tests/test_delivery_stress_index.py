from compat_runtime.delivery_stress_index.cli import build_delivery_stress_index_report


def test_delivery_stress_index_high_when_frozen_and_p0_high():
    report = build_delivery_stress_index_report(
        scope_freeze_guard_report={"summary": {"scope_freeze_guard": "freeze"}},
        throughput_guard_band_report={"summary": {"throughput_guard_score": 10}},
        risk_watchlist_report={"summary": {"p0_entries": 4}},
    )
    assert report["summary"]["delivery_stress_band"] == "high"


def test_delivery_stress_index_low_when_open_and_low_p0():
    report = build_delivery_stress_index_report(
        scope_freeze_guard_report={"summary": {"scope_freeze_guard": "open"}},
        throughput_guard_band_report={"summary": {"throughput_guard_score": 90}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
    )
    assert report["summary"]["delivery_stress_band"] == "low"
