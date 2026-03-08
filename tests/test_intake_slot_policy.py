from compat_runtime.intake_slot_policy.cli import build_intake_slot_policy_report


def test_intake_slot_policy_minimal_when_guard_tight():
    report = build_intake_slot_policy_report(
        throughput_guard_band_report={"summary": {"throughput_guard_band": "tight"}},
        intake_commitment_window_report={"summary": {"intake_commitment_window": "managed"}},
        intake_queue_policy_report={"summary": {"intake_queue_policy": "managed"}},
    )
    assert report["summary"]["intake_slot_policy"] == "minimal"


def test_intake_slot_policy_expanded_when_all_open():
    report = build_intake_slot_policy_report(
        throughput_guard_band_report={"summary": {"throughput_guard_band": "wide"}},
        intake_commitment_window_report={"summary": {"intake_commitment_window": "open"}},
        intake_queue_policy_report={"summary": {"intake_queue_policy": "permissive"}},
    )
    assert report["summary"]["intake_slot_policy"] == "expanded"
