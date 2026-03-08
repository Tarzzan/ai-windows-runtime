from compat_runtime.governance_friction.cli import build_governance_friction_report


def test_governance_friction_high_under_urgent_mode():
    report = build_governance_friction_report(
        control_efficiency_report={"summary": {"efficiency_score": 15}},
        intervention_plan_report={"summary": {"intervention_mode": "urgent"}},
        validation_coverage_report={"summary": {"missing_reports": 2}},
    )
    assert report["summary"]["friction_band"] == "high"


def test_governance_friction_low_when_stable():
    report = build_governance_friction_report(
        control_efficiency_report={"summary": {"efficiency_score": 90}},
        intervention_plan_report={"summary": {"intervention_mode": "routine"}},
        validation_coverage_report={"summary": {"missing_reports": 0}},
    )
    assert report["summary"]["friction_band"] in {"low", "medium"}
