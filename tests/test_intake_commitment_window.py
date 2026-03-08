from compat_runtime.intake_commitment_window.cli import build_intake_commitment_window_report


def test_intake_commitment_window_locked_when_release_closed():
    report = build_intake_commitment_window_report(
        delivery_safety_margin_report={"summary": {"safety_margin_band": "guarded"}},
        intake_release_window_report={"summary": {"intake_release_window": "closed"}},
        execution_stability_guard_report={"summary": {"execution_stability_guard": "elevated"}},
    )
    assert report["summary"]["intake_commitment_window"] == "locked"


def test_intake_commitment_window_open_when_all_open():
    report = build_intake_commitment_window_report(
        delivery_safety_margin_report={"summary": {"safety_margin_band": "comfortable"}},
        intake_release_window_report={"summary": {"intake_release_window": "open"}},
        execution_stability_guard_report={"summary": {"execution_stability_guard": "normal"}},
    )
    assert report["summary"]["intake_commitment_window"] == "open"
