from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_dependency_watch_report(
    *, productization_readiness: dict, risk_watchlist_report: dict, execution_report: dict
) -> dict:
    checks = productization_readiness.get("checks", [])
    failing_dependencies = [row for row in checks if str(row.get("status", "fail")) != "pass"]

    summary = {
        "dependencies_total": len(checks),
        "dependencies_blocking": len(failing_dependencies),
        "productization_ready": bool(productization_readiness.get("ready", False)),
        "p0_risks": int(risk_watchlist_report.get("summary", {}).get("p0_entries", 0)),
        "execution_status": str(execution_report.get("status", "unknown")),
    }

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "blocking_dependencies": [
            {
                "id": str(row.get("id", "dependency")),
                "path": str(row.get("path", "")),
                "status": str(row.get("status", "fail")),
            }
            for row in failing_dependencies
        ],
        "actions": ["Resolve dependency blockers before final delivery signoff."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dependency watch report")
    parser.add_argument("--productization-readiness", required=True, help="Productization readiness")
    parser.add_argument("--risk-watchlist-report", required=True, help="Risk watchlist report")
    parser.add_argument("--execution-report", required=True, help="Execution report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_dependency_watch_report(
        productization_readiness=read_json(args.productization_readiness),
        risk_watchlist_report=read_json(args.risk_watchlist_report),
        execution_report=read_json(args.execution_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
