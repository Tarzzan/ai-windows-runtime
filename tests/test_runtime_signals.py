from compat_runtime.runtime_signals.cli import build_runtime_signal_report


def _trace(events: list[dict]) -> dict:
    return {"artifact_version": "1.0", "events": events}


def test_runtime_signal_report_tracks_domain_failures_and_coverage():
    base = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "category": "com",
                "message": "err:ole:CoCreateInstance no class object",
                "severity": "high",
            },
            {
                "timestamp": "2026-01-01T00:00:01+00:00",
                "category": "runtime",
                "message": "RoActivateInstance failed for Windows.Storage",
                "severity": "high",
            },
        ]
    )
    runtime = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:02+00:00",
                "category": "installer",
                "message": "win32.CreateProcessW success",
                "severity": "low",
                "action": "CreateProcessW",
                "stage": "Success",
            },
            {
                "timestamp": "2026-01-01T00:00:03+00:00",
                "category": "registry",
                "message": "win32.RegQueryValueExW error",
                "severity": "high",
                "action": "RegQueryValueExW",
                "stage": "Error",
            },
            {
                "timestamp": "2026-01-01T00:00:04+00:00",
                "category": "runtime",
                "message": "win32.WinHttpSendRequest error: timeout",
                "severity": "high",
                "action": "WinHttpSendRequest",
                "stage": "Error",
            },
        ]
    )

    report = build_runtime_signal_report(trace=base, runtime_trace=runtime)
    assert report["summary"]["events_scanned"] == 5
    assert report["summary"]["com_failures"] >= 1
    assert report["summary"]["winrt_failures"] >= 1
    assert report["summary"]["registry_failures"] >= 1
    assert report["summary"]["network_failures"] >= 1
    assert report["summary"]["hook_domains_covered"] >= 3
    assert report["summary"]["hook_coverage_ratio"] >= 0.6
    assert report["issues"]
    assert report["actions"]


def test_runtime_signal_report_handles_empty_inputs():
    report = build_runtime_signal_report()
    assert report["summary"]["events_scanned"] == 0
    assert report["summary"]["domains_detected"] == 0
    assert report["summary"]["hook_domains_covered"] == 0
    assert report["coverage"]
    assert report["issues"] == []
