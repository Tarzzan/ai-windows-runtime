from compat_runtime.commitment_pacing.cli import build_commitment_pacing_report


def test_commitment_pacing_stabilize_with_gated_admission():
    report = build_commitment_pacing_report(
        admission_control_report={"summary": {"admission_state": "gated"}},
        backlog_refresh_report={"items": [{"priority": "P0"}]},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "narrow"}},
    )
    assert report["summary"]["commitment_mode"] == "stabilize"


def test_commitment_pacing_expand_with_open_and_no_p0():
    report = build_commitment_pacing_report(
        admission_control_report={"summary": {"admission_state": "open"}},
        backlog_refresh_report={"items": [{"priority": "P2"}]},
        delivery_bandwidth_report={"summary": {"bandwidth_mode": "wide"}},
    )
    assert report["summary"]["commitment_mode"] == "expand"
