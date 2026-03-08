from compat_runtime.execution_pressure.cli import build_execution_pressure_report


def test_execution_pressure_critical_when_momentum_low_and_blocked():
    report = build_execution_pressure_report(
        execution_momentum_report={"summary": {"momentum_index": 5}},
        dependency_watch_report={"summary": {"dependencies_blocking": 2, "p0_risks": 4}},
        validation_coverage_report={"summary": {"missing_reports": 3}},
    )

    assert report["summary"]["pressure_level"] in {"high", "critical"}
    assert report["summary"]["pressure_index"] >= 75
    assert report["actions"]


def test_execution_pressure_low_when_clean():
    report = build_execution_pressure_report(
        execution_momentum_report={"summary": {"momentum_index": 90}},
        dependency_watch_report={"summary": {"dependencies_blocking": 0, "p0_risks": 0}},
        validation_coverage_report={"summary": {"missing_reports": 0}},
    )

    assert report["summary"]["pressure_level"] == "low"
    assert report["summary"]["pressure_index"] < 25
