from compat_runtime.artifact_health.cli import build_artifact_health_report


def test_artifact_health_handles_missing_reports(tmp_path):
    report = build_artifact_health_report(validation_dir=str(tmp_path))
    assert report["summary"]["required_reports"] > 0
    assert report["summary"]["missing_reports"] > 0
    assert report["actions"]


def test_artifact_health_detects_existing_reports(tmp_path):
    (tmp_path / "execution-report-validation.json").write_text("{}", encoding="utf-8")
    report = build_artifact_health_report(validation_dir=str(tmp_path))
    assert report["summary"]["healthy_reports"] >= 1
