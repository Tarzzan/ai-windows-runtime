from compat_runtime.intake_queue_policy.cli import build_intake_queue_policy_report


def test_intake_queue_policy_restrictive_when_buffer_low():
    report = build_intake_queue_policy_report(
        capacity_buffer_report={"summary": {"capacity_buffer_band": "low"}},
        delivery_intake_sync_report={"summary": {"delivery_intake_sync": "aligned"}},
        commitment_guard_report={"summary": {"commitment_guard": "moderate"}},
    )
    assert report["summary"]["intake_queue_policy"] == "restrictive"


def test_intake_queue_policy_permissive_when_all_open():
    report = build_intake_queue_policy_report(
        capacity_buffer_report={"summary": {"capacity_buffer_band": "high"}},
        delivery_intake_sync_report={"summary": {"delivery_intake_sync": "expanding"}},
        commitment_guard_report={"summary": {"commitment_guard": "adaptive"}},
    )
    assert report["summary"]["intake_queue_policy"] == "permissive"
