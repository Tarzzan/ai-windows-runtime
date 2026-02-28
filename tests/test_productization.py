from pathlib import Path

from compat_runtime.productization.cli import build_productization_readiness_report


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_productization_readiness_passes_with_required_docs(tmp_path):
    _write(
        tmp_path / "docs/contributor-runbook.md",
        "# Contributor Runbook\n## Environment Setup\n## End-to-End Validation\n",
    )
    _write(
        tmp_path / "docs/compatibility-matrix-template.md",
        "# Compatibility Matrix Template\n## Fields\n## Example Row\n",
    )
    _write(
        tmp_path / "docs/corpus-contribution-protocol.md",
        "# Corpus Contribution Protocol\n## Submission Requirements\n## Validation Steps\n",
    )
    _write(
        tmp_path / "docs/security-review-checklist.md",
        "# Security Review Checklist\n## Threat Modeling\n## Release Gate\n",
    )

    report = build_productization_readiness_report(str(tmp_path))
    assert report["ready"] is True
    assert report["summary"]["fail_checks"] == 0


def test_productization_readiness_fails_when_heading_missing(tmp_path):
    _write(
        tmp_path / "docs/contributor-runbook.md",
        "# Contributor Runbook\n## Environment Setup\n",
    )

    report = build_productization_readiness_report(str(tmp_path))
    assert report["ready"] is False
    assert report["summary"]["fail_checks"] >= 1
    first = next(check for check in report["checks"] if check["id"] == "contributor_runbook")
    assert "## End-to-End Validation" in first["missing_headings"]
