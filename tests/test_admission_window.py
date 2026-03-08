from compat_runtime.admission_window.cli import build_admission_window_report


def test_admission_window_restricted_when_gated_or_focus_saturated():
    report = build_admission_window_report(
        scope_budget_report={"summary": {"scope_budget_mode": "balanced"}},
        admission_control_report={"summary": {"admission_state": "gated"}},
        execution_focus_report={"summary": {"p0_focus_items": 1}},
    )
    assert report["summary"]["admission_window"] == "restricted"


def test_admission_window_open_when_conditions_are_open():
    report = build_admission_window_report(
        scope_budget_report={"summary": {"scope_budget_mode": "flexible"}},
        admission_control_report={"summary": {"admission_state": "open"}},
        execution_focus_report={"summary": {"p0_focus_items": 0}},
    )
    assert report["summary"]["admission_window"] == "open"
