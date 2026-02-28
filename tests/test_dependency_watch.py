from compat_runtime.dependency_watch.cli import build_dependency_watch_report


def test_dependency_watch_detects_blockers():
    report = build_dependency_watch_report(
        productization_readiness={
            "ready": False,
            "checks": [{"id": "a", "path": "x", "status": "fail"}, {"id": "b", "status": "pass"}],
        },
        risk_watchlist_report={"summary": {"p0_entries": 2}},
        execution_report={"status": "gate"},
    )
    assert report["summary"]["dependencies_blocking"] == 1
