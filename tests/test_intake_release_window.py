from compat_runtime.intake_release_window.cli import build_intake_release_window_report


def test_intake_release_window_closed_when_flow_tight():
    report = build_intake_release_window_report(
        flow_control_budget_report={"summary": {"flow_control_mode": "tight"}},
        intake_queue_policy_report={"summary": {"intake_queue_policy": "managed"}},
        admission_window_report={"summary": {"admission_window": "controlled"}},
    )
    assert report["summary"]["intake_release_window"] == "closed"


def test_intake_release_window_open_when_all_open():
    report = build_intake_release_window_report(
        flow_control_budget_report={"summary": {"flow_control_mode": "open"}},
        intake_queue_policy_report={"summary": {"intake_queue_policy": "permissive"}},
        admission_window_report={"summary": {"admission_window": "open"}},
    )
    assert report["summary"]["intake_release_window"] == "open"
