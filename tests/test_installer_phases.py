from compat_runtime.installer_phases.cli import build_installer_phase_report


def _trace(events: list[dict]) -> dict:
    return {"artifact_version": "1.0", "events": events}


def test_installer_phase_report_detects_phases_and_errors():
    base = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "category": "installer",
                "message": "C2R bootstrap handshake failed",
                "severity": "high",
            },
            {
                "timestamp": "2026-01-01T00:00:01+00:00",
                "category": "network",
                "message": "winhttp download timeout",
                "severity": "high",
            },
        ]
    )
    runtime = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:02+00:00",
                "category": "registry",
                "message": "win32.RegQueryValueExW error",
                "severity": "high",
                "action": "RegQueryValueExW",
                "stage": "Error",
            }
        ]
    )

    report = build_installer_phase_report(trace=base, runtime_trace=runtime)
    assert report["summary"]["events_scanned"] == 3
    assert report["summary"]["phases_detected"] >= 2
    assert report["summary"]["has_errors"] is True
    assert report["phases"]
    assert report["actions"]


def test_installer_phase_report_handles_empty():
    report = build_installer_phase_report()
    assert report["summary"]["events_scanned"] == 0
    assert report["summary"]["phases_detected"] == 0
    assert report["timeline"] == []

