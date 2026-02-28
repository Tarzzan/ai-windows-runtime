from compat_runtime.hook_backlog.cli import build_hook_backlog_report


def _runtime_signal_report(coverage: list[dict]) -> dict:
    return {"summary": {"events_scanned": 8}, "coverage": coverage}


def _patch_plan(proposals: list[dict]) -> dict:
    return {"proposals": proposals}


def _proposal_risk(proposals: list[dict]) -> dict:
    return {"proposals": proposals}


def test_hook_backlog_highlights_missing_high_impact_domains():
    runtime_signal = _runtime_signal_report(
        [
            {"domain": "com", "events": 3, "errors": 2, "hook_present": False},
            {"domain": "winrt", "events": 1, "errors": 1, "hook_present": False},
            {"domain": "registry", "events": 2, "errors": 1, "hook_present": True},
            {"domain": "network", "events": 2, "errors": 0, "hook_present": False},
            {"domain": "installer", "events": 4, "errors": 2, "hook_present": True},
        ]
    )
    patch_plan = _patch_plan(
        [
            {"gap_id": "g1", "title": "Implement or stub required COM activation path"},
            {"gap_id": "g2", "title": "Improve winhttp/protocol compatibility layer"},
            {"gap_id": "g3", "title": "Instrument installer bootstrap handshake"},
        ]
    )
    risk = _proposal_risk(
        [
            {"gap_id": "g1", "risk_level": "high"},
            {"gap_id": "g2", "risk_level": "medium"},
            {"gap_id": "g3", "risk_level": "high"},
        ]
    )

    report = build_hook_backlog_report(
        runtime_signal_report=runtime_signal,
        patch_plan=patch_plan,
        proposal_risk_report=risk,
    )

    assert report["summary"]["domains_considered"] == 5
    assert report["summary"]["missing_hooks"] >= 2
    assert report["summary"]["p0_items"] >= 1
    assert report["summary"]["related_high_risk_proposals"] >= 1
    assert report["items"][0]["missing_hook"] is True
    assert report["actions"]


def test_hook_backlog_handles_fully_covered_domains():
    runtime_signal = _runtime_signal_report(
        [
            {"domain": "com", "events": 1, "errors": 0, "hook_present": True},
            {"domain": "winrt", "events": 0, "errors": 0, "hook_present": True},
            {"domain": "registry", "events": 1, "errors": 0, "hook_present": True},
            {"domain": "network", "events": 1, "errors": 0, "hook_present": True},
            {"domain": "installer", "events": 1, "errors": 0, "hook_present": True},
        ]
    )

    report = build_hook_backlog_report(
        runtime_signal_report=runtime_signal,
        patch_plan=_patch_plan([]),
        proposal_risk_report=_proposal_risk([]),
    )

    assert report["summary"]["missing_hooks"] == 0
    assert report["summary"]["p0_items"] == 0
    assert report["items"][-1]["missing_hook"] is False
