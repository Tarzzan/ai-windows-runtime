from compat_runtime.office_readiness.cli import build_office_readiness_report


def test_office_readiness_ready_when_bootstrap_is_clean():
    report = build_office_readiness_report(
        runtime_signal_report={
            "summary": {
                "hook_coverage_ratio": 0.91,
                "com_failures": 0,
                "registry_failures": 0,
                "installer_failures": 0,
            }
        },
        hook_backlog_report={"summary": {"p0_items": 0}},
        stability_window_report={"summary": {"window_status": "stable"}},
        installer_phase_report={
            "summary": {"has_errors": False},
            "phases": [{"phase": "bootstrap", "progress": 95}],
        },
    )

    assert report["status"] == "ready"
    assert report["summary"]["bootstrap_coverage"] == 0.95
    assert report["summary"]["bootstrap_phase_events"] == 0
    assert report["summary"]["bootstrap_phase_errors"] == 0


def test_office_readiness_blocked_with_unstable_window_and_p0():
    report = build_office_readiness_report(
        runtime_signal_report={
            "summary": {
                "hook_coverage_ratio": 0.3,
                "com_failures": 4,
                "registry_failures": 6,
                "installer_failures": 9,
            }
        },
        hook_backlog_report={"summary": {"p0_items": 5}},
        stability_window_report={"summary": {"window_status": "unstable"}},
        installer_phase_report={"summary": {"has_errors": True}, "phases": []},
    )

    assert report["status"] == "blocked"
    assert report["summary"]["unresolved_p0_items"] == 5
    assert report["summary"]["bootstrap_phase_events"] == 0
    assert report["summary"]["bootstrap_phase_errors"] == 0
    assert report["actions"]


def test_office_readiness_uses_bootstrap_rollup_counters():
    report = build_office_readiness_report(
        runtime_signal_report={
            "summary": {
                "hook_coverage_ratio": 0.9,
                "com_failures": 0,
                "registry_failures": 0,
                "installer_failures": 1,
            }
        },
        hook_backlog_report={
            "summary": {"p0_items": 3},
            "items": [
                {"domain": "com", "missing_hook": True, "urgency": "P0"},
                {"domain": "network", "missing_hook": True, "urgency": "P0"},
            ],
        },
        stability_window_report={"summary": {"window_status": "unstable"}},
        installer_phase_report={
            "summary": {"has_errors": True},
            "phases": [
                {
                    "phase": "bootstrap",
                    "events": 4,
                    "success": 1,
                    "progress": 1,
                    "errors": 2,
                }
            ],
        },
    )

    assert report["summary"]["bootstrap_coverage"] == 0.5
    assert report["summary"]["unresolved_p0_items"] == 1
    assert report["summary"]["installer_has_errors"] is True
    assert report["summary"]["bootstrap_phase_events"] == 4
    assert report["summary"]["bootstrap_phase_errors"] == 2
    assert report["status"] == "limited"
