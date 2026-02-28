from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import write_json


REQUIRED_REPORTS = [
    "execution-report-validation.json",
    "trend-report-validation.json",
    "kpi-report-validation.json",
    "quality-gate-report-validation.json",
    "release-decision-report-validation.json",
    "iteration-plan-report-validation.json",
    "release-forecast-report-validation.json",
    "readiness-scorecard-report-validation.json",
    "execution-burndown-report-validation.json",
    "validation-command-pack-validation.json",
    "risk-watchlist-report-validation.json",
    "release-gate-history-report-validation.json",
    "pilot-readiness-report-validation.json",
    "ownership-assignment-report-validation.json",
    "remediation-sprint-report-validation.json",
    "release-brief-report-validation.json",
    "rollout-guardrails-report-validation.json",
]


def _entry(path: Path, name: str) -> dict:
    exists = path.exists()
    status = "healthy" if exists else "missing"
    return {
        "name": name,
        "exists": exists,
        "status": status,
        "path": str(path),
    }


def build_artifact_health_report(*, validation_dir: str) -> dict:
    root = Path(validation_dir)
    entries = [_entry(root / name, name) for name in REQUIRED_REPORTS]

    healthy = sum(1 for row in entries if row["status"] == "healthy")
    missing = len(entries) - healthy
    ratio = round(healthy / len(entries), 3) if entries else 0.0

    actions = []
    if missing > 0:
        actions.append("Regenerate missing validation reports before release packaging.")
    else:
        actions.append("All required validation reports are present.")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "required_reports": len(entries),
            "healthy_reports": healthy,
            "missing_reports": missing,
            "health_ratio": ratio,
        },
        "reports": entries,
        "actions": actions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build artifact health report")
    parser.add_argument(
        "--validation-dir", required=True, help="Validation report directory (e.g. out/validation)"
    )
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_artifact_health_report(validation_dir=args.validation_dir)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
