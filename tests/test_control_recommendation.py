from compat_runtime.control_recommendation.cli import build_control_recommendation_report


def test_control_recommendation_strict_if_policy_fails():
    report = build_control_recommendation_report(
        delivery_temperature_report={"summary": {"temperature": "hot"}},
        execution_confidence_report={"summary": {"confidence_band": "low"}},
        execution_pressure_report={"summary": {"pressure_level": "critical"}},
        release_policy_report={"status": "fail"},
    )
    assert report["summary"]["control_mode"] == "strict"


def test_control_recommendation_accelerate_when_clean():
    report = build_control_recommendation_report(
        delivery_temperature_report={"summary": {"temperature": "cool"}},
        execution_confidence_report={"summary": {"confidence_band": "high"}},
        execution_pressure_report={"summary": {"pressure_level": "low"}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["control_mode"] == "accelerate"
