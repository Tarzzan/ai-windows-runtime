from compat_runtime.delivery_temperature.cli import build_delivery_temperature_report


def test_delivery_temperature_hot_under_pressure():
    report = build_delivery_temperature_report(
        execution_pressure_report={"summary": {"pressure_index": 90}},
        launch_readiness_report={"status": "blocked"},
        release_decision_report={"decision": "no-go"},
    )
    assert report["summary"]["temperature"] == "hot"


def test_delivery_temperature_cool_when_ready():
    report = build_delivery_temperature_report(
        execution_pressure_report={"summary": {"pressure_index": 10}},
        launch_readiness_report={"status": "ready"},
        release_decision_report={"decision": "go"},
    )
    assert report["summary"]["temperature"] == "cool"
