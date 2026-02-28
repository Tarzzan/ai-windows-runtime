from compat_runtime.validation_coverage.cli import build_validation_coverage_report


def test_validation_coverage_missing(tmp_path):
    report = build_validation_coverage_report(validation_dir=str(tmp_path))
    assert report["summary"]["required_reports"] > 0
    assert report["summary"]["missing_reports"] > 0
