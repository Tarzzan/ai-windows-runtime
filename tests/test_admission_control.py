from compat_runtime.admission_control.cli import build_admission_control_report


def test_admission_control_gated_when_policy_fails():
    report = build_admission_control_report(
        intake_capacity_report={"summary": {"intake_capacity_mode": "expandable"}},
        release_policy_report={"status": "fail"},
        priority_corridor_report={"summary": {"priority_corridor": "full"}},
    )
    assert report["summary"]["admission_state"] == "gated"


def test_admission_control_open_when_capacity_and_policy_allow_it():
    report = build_admission_control_report(
        intake_capacity_report={"summary": {"intake_capacity_mode": "expandable"}},
        release_policy_report={"status": "pass"},
        priority_corridor_report={"summary": {"priority_corridor": "full"}},
    )
    assert report["summary"]["admission_state"] == "open"
