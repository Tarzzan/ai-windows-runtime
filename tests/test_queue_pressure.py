from compat_runtime.queue_pressure.cli import build_queue_pressure_report


def test_queue_pressure_high_when_tight_and_overloaded():
    report = build_queue_pressure_report(
        owner_load_report={"summary": {"overloaded_owners": 2}},
        execution_throttle_report={"summary": {"throttle_mode": "tight"}},
        priority_corridor_report={"summary": {"priority_corridor": "p0_only"}},
    )
    assert report["summary"]["queue_pressure_band"] == "high"


def test_queue_pressure_low_when_open_full():
    report = build_queue_pressure_report(
        owner_load_report={"summary": {"overloaded_owners": 0}},
        execution_throttle_report={"summary": {"throttle_mode": "open"}},
        priority_corridor_report={"summary": {"priority_corridor": "full"}},
    )
    assert report["summary"]["queue_pressure_band"] in {"low", "medium"}
