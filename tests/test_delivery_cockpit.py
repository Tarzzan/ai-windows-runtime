from compat_runtime.delivery_cockpit.cli import build_delivery_cockpit_report


def test_delivery_cockpit_status_computed():
    report = build_delivery_cockpit_report(
        release_brief_report={
            "summary": {
                "readiness_score": 70,
                "pilot_recommendation": "limited_pilot",
                "blocking_tasks": 2,
                "release_policy_status": "pass",
                "release_policy_failures": 0,
            }
        },
        remediation_sprint_report={"summary": {"sprint_now_tasks": 3}},
        artifact_health_report={"summary": {"missing_reports": 0, "health_ratio": 1.0}},
    )
    assert report["summary"]["cockpit_status"] == "watch"
    assert report["summary"]["release_policy_status"] == "pass"
    assert report["summary"]["release_policy_failures"] == 0
    assert report["actions"]
