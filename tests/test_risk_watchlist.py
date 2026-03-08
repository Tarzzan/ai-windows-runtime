from compat_runtime.risk_watchlist.cli import build_risk_watchlist_report


def test_risk_watchlist_collects_priority_entries():
    report = build_risk_watchlist_report(
        proposal_risk_report={
            "proposals": [
                {"gap_id": "g1", "risk_level": "high", "risk_score": 95},
                {"gap_id": "g2", "risk_level": "medium", "risk_score": 60},
            ]
        },
        hook_backlog_report={
            "items": [
                {"domain": "com", "missing_hook": True, "urgency": "P0", "errors": 1, "related_high_risk": 1}
            ]
        },
        runtime_signal_report={
            "issues": [{"id": "i1", "severity": "high", "domain": "com", "message": "CoCreate failed"}]
        },
        release_policy_report={"status": "fail", "failures": ["x"]},
    )

    assert report["summary"]["entries_total"] >= 3
    assert report["summary"]["p0_entries"] >= 1
    assert report["summary"]["release_policy_status"] == "fail"
    assert report["summary"]["release_policy_failures"] == 1
    assert report["actions"]


def test_risk_watchlist_handles_no_signals():
    report = build_risk_watchlist_report(
        proposal_risk_report={"proposals": []},
        hook_backlog_report={"items": []},
        runtime_signal_report={"issues": []},
    )
    assert report["summary"]["entries_total"] == 0
    assert report["summary"]["p0_entries"] == 0
    assert report["summary"]["release_policy_status"] == "missing"
