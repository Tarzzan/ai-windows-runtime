from compat_runtime.crash_signatures.cli import build_crash_signature_report


def _trace(events: list[dict]) -> dict:
    return {"artifact_version": "1.0", "events": events}


def test_crash_signatures_extracts_prioritized_signatures():
    base = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "category": "loader",
                "message": "err:module:import_dll failed to load KERNELBASE.dll",
                "severity": "high",
            },
            {
                "timestamp": "2026-01-01T00:00:01+00:00",
                "category": "installer",
                "message": "C2R bootstrap handshake failed",
                "severity": "high",
            },
        ]
    )
    runtime = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:02+00:00",
                "category": "sync",
                "message": "win32.WaitForSingleObject error: timeout while waiting",
                "severity": "high",
            }
        ]
    )

    report = build_crash_signature_report(trace=base, runtime_trace=runtime)
    assert report["summary"]["events_scanned"] == 3
    assert report["summary"]["signatures"] >= 2
    assert report["signatures"]
    assert report["actions"]


def test_crash_signatures_handles_no_anomaly():
    base = _trace(
        [
            {
                "timestamp": "2026-01-01T00:00:00+00:00",
                "category": "runtime",
                "message": "normal startup",
                "severity": "low",
            }
        ]
    )
    report = build_crash_signature_report(trace=base)
    assert report["summary"]["signatures"] == 0
    assert report["signatures"] == []

