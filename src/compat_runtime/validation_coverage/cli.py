from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import write_json


REQUIRED_REPORTS = [
    "ownership-assignment-report-validation.json",
    "remediation-sprint-report-validation.json",
    "release-brief-report-validation.json",
    "rollout-guardrails-report-validation.json",
    "artifact-health-report-validation.json",
    "delivery-cockpit-report-validation.json",
    "stakeholder-update-report-validation.json",
    "handoff-checklist-report-validation.json",
]


def _entry(path: Path, name: str) -> dict:
    exists = path.exists()
    return {
        "name": name,
        "exists": exists,
        "status": "covered" if exists else "missing",
        "path": str(path),
    }


def build_validation_coverage_report(*, validation_dir: str) -> dict:
    root = Path(validation_dir)
    entries = [_entry(root / name, name) for name in REQUIRED_REPORTS]

    covered = sum(1 for row in entries if row["status"] == "covered")
    missing = len(entries) - covered

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "required_reports": len(entries),
            "covered_reports": covered,
            "missing_reports": missing,
            "coverage_ratio": round((covered / len(entries)) if entries else 0.0, 3),
        },
        "reports": entries,
        "actions": ["Close missing validation coverage before final launch readiness decision."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build validation coverage report")
    parser.add_argument("--validation-dir", required=True, help="Validation report directory")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_validation_coverage_report(validation_dir=args.validation_dir)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
