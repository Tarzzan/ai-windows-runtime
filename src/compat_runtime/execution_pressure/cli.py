from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _pressure_level(index: int) -> str:
    if index >= 75:
        return "critical"
    if index >= 50:
        return "high"
    if index >= 25:
        return "medium"
    return "low"


def _actions(level: str, dependency_blockers: int, missing_validation: int) -> list[str]:
    actions: list[str] = []
    if level in {"critical", "high"}:
        actions.append("Limit new scope intake and focus on stabilization throughput.")
    else:
        actions.append("Maintain controlled delivery pace with weekly pressure checkpoints.")

    if dependency_blockers > 0:
        actions.append("Escalate dependency blockers with owners before next signoff gate.")
    if missing_validation > 0:
        actions.append("Close validation coverage gaps to reduce delivery pressure volatility.")
    return actions


def build_execution_pressure_report(
    *,
    execution_momentum_report: dict,
    dependency_watch_report: dict,
    validation_coverage_report: dict,
) -> dict:
    momentum_summary = execution_momentum_report.get("summary", {})
    dep_summary = dependency_watch_report.get("summary", {})
    coverage_summary = validation_coverage_report.get("summary", {})

    momentum_index = int(momentum_summary.get("momentum_index", 0))
    dependency_blockers = int(dep_summary.get("dependencies_blocking", 0))
    p0_risks = int(dep_summary.get("p0_risks", 0))
    missing_validation = int(coverage_summary.get("missing_reports", 0))

    base_pressure = max(0, 100 - momentum_index)
    dependency_penalty = min(30, dependency_blockers * 10)
    risk_penalty = min(20, p0_risks * 4)
    validation_penalty = min(20, missing_validation * 6)

    pressure_index = max(0, min(100, base_pressure + dependency_penalty + risk_penalty + validation_penalty))
    pressure_level = _pressure_level(pressure_index)

    summary = {
        "pressure_index": pressure_index,
        "pressure_level": pressure_level,
        "momentum_index": momentum_index,
        "dependency_blockers": dependency_blockers,
        "p0_risks": p0_risks,
        "missing_validation_reports": missing_validation,
    }

    scoring = {
        "base_pressure": base_pressure,
        "dependency_penalty": dependency_penalty,
        "risk_penalty": risk_penalty,
        "validation_penalty": validation_penalty,
    }

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "scoring": scoring,
        "actions": _actions(pressure_level, dependency_blockers, missing_validation),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build execution pressure report")
    parser.add_argument("--execution-momentum-report", required=True, help="Execution momentum report path")
    parser.add_argument("--dependency-watch-report", required=True, help="Dependency watch report path")
    parser.add_argument("--validation-coverage-report", required=True, help="Validation coverage report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_execution_pressure_report(
        execution_momentum_report=read_json(args.execution_momentum_report),
        dependency_watch_report=read_json(args.dependency_watch_report),
        validation_coverage_report=read_json(args.validation_coverage_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
