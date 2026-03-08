from compat_runtime.execution_throttle.cli import build_execution_throttle_report


def test_execution_throttle_tight_when_friction_high():
    report = build_execution_throttle_report(
        cadence_recommendation_report={"summary": {"cadence": "slow"}},
        governance_friction_report={"summary": {"friction_band": "high"}},
        owner_load_report={"summary": {"overloaded_owners": 1}},
    )
    assert report["summary"]["throttle_mode"] == "tight"


def test_execution_throttle_open_when_clean():
    report = build_execution_throttle_report(
        cadence_recommendation_report={"summary": {"cadence": "fast"}},
        governance_friction_report={"summary": {"friction_band": "low"}},
        owner_load_report={"summary": {"overloaded_owners": 0}},
    )
    assert report["summary"]["throttle_mode"] == "open"
