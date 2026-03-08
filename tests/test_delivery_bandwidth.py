from compat_runtime.delivery_bandwidth.cli import build_delivery_bandwidth_report


def test_delivery_bandwidth_narrow_when_pressure_high():
    report = build_delivery_bandwidth_report(
        queue_pressure_report={"summary": {"queue_pressure_score": 90}},
        cadence_recommendation_report={"summary": {"cadence": "slow"}},
        owner_load_report={"summary": {"overloaded_owners": 2}},
    )
    assert report["summary"]["bandwidth_mode"] == "narrow"


def test_delivery_bandwidth_wide_when_pressure_low():
    report = build_delivery_bandwidth_report(
        queue_pressure_report={"summary": {"queue_pressure_score": 10}},
        cadence_recommendation_report={"summary": {"cadence": "fast"}},
        owner_load_report={"summary": {"overloaded_owners": 0}},
    )
    assert report["summary"]["bandwidth_mode"] == "wide"
