from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_verification_snapshot_report(
    *,
    validation_coverage_report: dict,
    next_cycle_bootstrap_report: dict,
    delivery_signoff_report: dict,
) -> dict:
    coverage_summary = validation_coverage_report.get("summary", {})
    bootstrap_summary = next_cycle_bootstrap_report.get("summary", {})
    signoff_summary = delivery_signoff_report.get("summary", {})

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "coverage_ratio": float(coverage_summary.get("coverage_ratio", 0.0)),
            "missing_reports": int(coverage_summary.get("missing_reports", 0)),
            "bootstrap_status": str(next_cycle_bootstrap_report.get("status", "blocked")),
            "bootstrap_commands": int(bootstrap_summary.get("bootstrap_commands", 0)),
            "signoff_status": str(delivery_signoff_report.get("status", "blocked")),
            "dependency_blockers": int(signoff_summary.get("dependency_blockers", 0)),
        },
        "actions": ["Capture this snapshot before governance checkpoint review."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build verification snapshot report")
    parser.add_argument("--validation-coverage-report", required=True, help="Validation coverage report")
    parser.add_argument("--next-cycle-bootstrap-report", required=True, help="Next cycle bootstrap report")
    parser.add_argument("--delivery-signoff-report", required=True, help="Delivery signoff report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_verification_snapshot_report(
        validation_coverage_report=read_json(args.validation_coverage_report),
        next_cycle_bootstrap_report=read_json(args.next_cycle_bootstrap_report),
        delivery_signoff_report=read_json(args.delivery_signoff_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
