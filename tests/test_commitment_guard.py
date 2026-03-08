from compat_runtime.commitment_guard.cli import build_commitment_guard_report


def test_commitment_guard_strict_when_policy_not_pass():
    report = build_commitment_guard_report(
        admission_window_report={"summary": {"admission_window": "open"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
        release_policy_report={"status": "fail"},
    )
    assert report["summary"]["commitment_guard"] == "strict"


def test_commitment_guard_adaptive_on_open_low_risk_and_pass():
    report = build_commitment_guard_report(
        admission_window_report={"summary": {"admission_window": "open"}},
        risk_watchlist_report={"summary": {"p0_entries": 0}},
        release_policy_report={"status": "pass"},
    )
    assert report["summary"]["commitment_guard"] == "adaptive"
