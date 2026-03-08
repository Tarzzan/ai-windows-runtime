from compat_runtime.intake_pacing_window.cli import build_intake_pacing_window_report


def test_intake_pacing_window_slow_when_stress_high():
    report = build_intake_pacing_window_report(
        delivery_stress_index_report={"summary": {"delivery_stress_band": "high"}},
        intake_slot_policy_report={"summary": {"intake_slot_policy": "moderate"}},
        intake_release_window_report={"summary": {"intake_release_window": "limited"}},
    )
    assert report["summary"]["intake_pacing_window"] == "slow"


def test_intake_pacing_window_fast_when_all_open():
    report = build_intake_pacing_window_report(
        delivery_stress_index_report={"summary": {"delivery_stress_band": "low"}},
        intake_slot_policy_report={"summary": {"intake_slot_policy": "expanded"}},
        intake_release_window_report={"summary": {"intake_release_window": "open"}},
    )
    assert report["summary"]["intake_pacing_window"] == "fast"
