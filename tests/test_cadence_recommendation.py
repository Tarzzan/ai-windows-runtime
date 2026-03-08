from compat_runtime.cadence_recommendation.cli import build_cadence_recommendation_report


def test_cadence_recommendation_slow_when_hot_and_high_friction():
    report = build_cadence_recommendation_report(
        governance_friction_report={"summary": {"friction_band": "high", "friction_score": 90}},
        delivery_temperature_report={"summary": {"temperature": "hot"}},
        control_recommendation_report={"summary": {"control_mode": "stabilize"}},
    )
    assert report["summary"]["cadence"] == "slow"


def test_cadence_recommendation_fast_when_cool_and_low_friction():
    report = build_cadence_recommendation_report(
        governance_friction_report={"summary": {"friction_band": "low", "friction_score": 10}},
        delivery_temperature_report={"summary": {"temperature": "cool"}},
        control_recommendation_report={"summary": {"control_mode": "accelerate"}},
    )
    assert report["summary"]["cadence"] == "fast"
