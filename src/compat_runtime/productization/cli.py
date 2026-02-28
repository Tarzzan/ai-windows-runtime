from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import write_json


REQUIRED_DOCS = [
    {
        "id": "contributor_runbook",
        "path": "docs/contributor-runbook.md",
        "headings": [
            "# Contributor Runbook",
            "## Environment Setup",
            "## End-to-End Validation",
        ],
    },
    {
        "id": "compatibility_matrix_template",
        "path": "docs/compatibility-matrix-template.md",
        "headings": [
            "# Compatibility Matrix Template",
            "## Fields",
            "## Example Row",
        ],
    },
    {
        "id": "corpus_protocol",
        "path": "docs/corpus-contribution-protocol.md",
        "headings": [
            "# Corpus Contribution Protocol",
            "## Submission Requirements",
            "## Validation Steps",
        ],
    },
    {
        "id": "security_review_checklist",
        "path": "docs/security-review-checklist.md",
        "headings": [
            "# Security Review Checklist",
            "## Threat Modeling",
            "## Release Gate",
        ],
    },
]


def _evaluate_doc(root: Path, item: dict) -> dict:
    doc_path = root / item["path"]
    exists = doc_path.exists()
    missing_headings: list[str] = []
    if exists:
        text = doc_path.read_text(encoding="utf-8")
        for heading in item["headings"]:
            if heading not in text:
                missing_headings.append(heading)
    else:
        missing_headings = list(item["headings"])

    headings_ok = exists and not missing_headings
    status = "pass" if headings_ok else "fail"

    return {
        "id": item["id"],
        "path": item["path"],
        "exists": exists,
        "headings_ok": headings_ok,
        "missing_headings": missing_headings,
        "status": status,
    }


def build_productization_readiness_report(root_dir: str) -> dict:
    root = Path(root_dir)
    checks = [_evaluate_doc(root, item) for item in REQUIRED_DOCS]
    pass_count = sum(1 for check in checks if check["status"] == "pass")
    fail_count = len(checks) - pass_count

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ready": fail_count == 0,
        "summary": {
            "total_checks": len(checks),
            "pass_checks": pass_count,
            "fail_checks": fail_count,
        },
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate productization governance artifacts in repository"
    )
    parser.add_argument("--root", default=".", help="Repository root directory")
    parser.add_argument("--output", required=True, help="Readiness report JSON output")
    args = parser.parse_args()

    report = build_productization_readiness_report(args.root)
    write_json(args.output, report)

    if not report["ready"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
