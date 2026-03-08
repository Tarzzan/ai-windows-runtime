from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import read_json, write_json
from compat_runtime.common.policy import load_alpha_gating_policy


def _metric(report: dict, path: tuple[str, ...]) -> int:
    node = report
    for key in path:
        if not isinstance(node, dict):
            return 0
        node = node.get(key)
    return int(node) if isinstance(node, int) else 0


def _bool_path(report: dict, path: tuple[str, ...]) -> bool:
    node = report
    for key in path:
        if not isinstance(node, dict):
            return False
        node = node.get(key)
    return bool(node)


def build_compatibility_matrix(
    execution_report: dict,
    *,
    trend_report: dict | None = None,
    kpi_report: dict | None = None,
) -> dict:
    policy = load_alpha_gating_policy().get("release_readiness", {})
    kpi_high_without_failed_runs_pass = bool(
        policy.get("kpi_high_without_failed_runs_pass", True)
    )
    base_trace_events = _metric(execution_report, ("pipeline", "base", "trace_events"))
    base_gaps = _metric(execution_report, ("pipeline", "base", "gaps"))
    base_proposals = _metric(execution_report, ("pipeline", "base", "proposals"))
    runtime_trace_events = _metric(execution_report, ("pipeline", "runtime", "trace_events"))
    runtime_gaps = _metric(execution_report, ("pipeline", "runtime", "gaps"))
    runtime_proposals = _metric(execution_report, ("pipeline", "runtime", "proposals"))

    base_validation = all(
        [
            _bool_path(execution_report, ("pipeline", "base", "validation", "trace")),
            _bool_path(execution_report, ("pipeline", "base", "validation", "gaps")),
            _bool_path(execution_report, ("pipeline", "base", "validation", "patch_plan")),
        ]
    )
    runtime_validation = _bool_path(execution_report, ("pipeline", "runtime", "validation", "trace"))
    execution_ok = execution_report.get("status") == "ok"

    regressed_metrics = len(
        (trend_report or {}).get("summary", {}).get("regressed_metrics", [])
    )
    kpi_summary = (kpi_report or {}).get("summary", {})
    risk_level = kpi_summary.get("risk_level", "unknown")
    failed_runs = int(kpi_summary.get("failed_runs", 0))

    scenarios = [
        {
            "id": "base-sample-trace",
            "status": "pass" if base_validation and execution_ok else "fail",
            "gaps": base_gaps,
            "proposals": base_proposals,
            "evidence": "out/trace.json + out/gaps.json + out/patch-plan.json",
        },
        {
            "id": "runtime-telemetry-sample",
            "status": "pass" if runtime_validation and runtime_trace_events > 0 else "fail",
            "gaps": runtime_gaps,
            "proposals": runtime_proposals,
            "evidence": "out/runtime-trace.json + out/runtime-gaps.json + out/runtime-patch-plan.json",
        },
    ]

    risk_blocks_release = risk_level == "high" and (
        failed_runs > 0 or not kpi_high_without_failed_runs_pass
    )
    release_ready = execution_ok and base_validation and runtime_validation and not risk_blocks_release

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "channel": "alpha",
        "release_ready": release_ready,
        "summary": {
            "execution_status": execution_report.get("status", "unknown"),
            "risk_level": risk_level,
            "failed_runs": failed_runs,
            "regressed_metrics_count": regressed_metrics,
            "base_trace_events": base_trace_events,
            "runtime_trace_events": runtime_trace_events,
        },
        "scenarios": scenarios,
    }


def build_alpha_release_checklist(
    compatibility_matrix: dict,
    *,
    trend_report: dict | None = None,
    kpi_report: dict | None = None,
) -> dict:
    policy = load_alpha_gating_policy().get("release_readiness", {})
    kpi_high_without_failed_runs_pass = bool(
        policy.get("kpi_high_without_failed_runs_pass", True)
    )
    regression_warn_threshold = int(policy.get("regression_warn_threshold", 4))
    kpi_summary = (kpi_report or {}).get("summary", {})
    risk_level = kpi_summary.get("risk_level", "unknown")
    failed_runs = int(kpi_summary.get("failed_runs", 0))
    regressed = len((trend_report or {}).get("summary", {}).get("regressed_metrics", []))

    items = [
        {
            "id": "pipeline_green",
            "title": "Pipeline complet vert",
            "required": True,
            "status": "pass"
            if compatibility_matrix.get("summary", {}).get("execution_status") == "ok"
            else "fail",
            "evidence": "out/execution-report.json",
        },
        {
            "id": "base_runtime_scenarios",
            "title": "Scénarios de base et runtime validés",
            "required": True,
            "status": "pass"
            if all(s.get("status") == "pass" for s in compatibility_matrix.get("scenarios", []))
            else "fail",
            "evidence": "out/compatibility-matrix.json",
        },
        {
            "id": "risk_level",
            "title": "Niveau de risque acceptable",
            "required": True,
            "status": (
                "pass"
                if risk_level in {"low", "medium"}
                else (
                    "pass"
                    if risk_level == "high"
                    and failed_runs == 0
                    and kpi_high_without_failed_runs_pass
                    else "fail"
                )
            ),
            "evidence": "out/kpi-report.json",
        },
        {
            "id": "regression_review",
            "title": "Régressions analysées",
            "required": False,
            "status": "warn" if regressed > regression_warn_threshold else "pass",
            "evidence": "out/trend-report.json",
        },
        {
            "id": "bundle_manifest",
            "title": "Manifeste de livrable généré",
            "required": False,
            "status": "todo",
            "evidence": "out/release-bundle-manifest.json",
        },
    ]

    required_failures = sum(
        1 for item in items if item.get("required") and item.get("status") == "fail"
    )
    pass_count = sum(1 for item in items if item.get("status") == "pass")
    warn_count = sum(1 for item in items if item.get("status") == "warn")
    fail_count = sum(1 for item in items if item.get("status") == "fail")

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_ready": required_failures == 0,
        "summary": {
            "total_items": len(items),
            "pass_items": pass_count,
            "warn_items": warn_count,
            "fail_items": fail_count,
            "required_failures": required_failures,
        },
        "items": items,
    }


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def build_release_bundle_manifest(artifacts: list[str]) -> dict:
    entries = []
    missing = []
    for path in artifacts:
        if not Path(path).exists():
            missing.append(path)
            continue
        entries.append(
            {
                "path": path,
                "size_bytes": Path(path).stat().st_size,
                "sha256": _sha256(path),
            }
        )

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "files": entries,
        "missing": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release readiness artifacts")
    parser.add_argument("--execution-report", required=True, help="Execution report input")
    parser.add_argument("--trend-report", required=False, help="Trend report input")
    parser.add_argument("--kpi-report", required=False, help="KPI report input")
    parser.add_argument(
        "--matrix-output", required=True, help="Compatibility matrix output path"
    )
    parser.add_argument(
        "--checklist-output", required=True, help="Alpha release checklist output path"
    )
    parser.add_argument(
        "--manifest-output", required=False, help="Optional release bundle manifest output path"
    )
    parser.add_argument(
        "--artifacts",
        required=False,
        nargs="*",
        help="Optional artifact paths for manifest checksum generation",
    )
    args = parser.parse_args()

    execution = read_json(args.execution_report)
    trend = read_json(args.trend_report) if args.trend_report else None
    kpi = read_json(args.kpi_report) if args.kpi_report else None

    matrix = build_compatibility_matrix(execution, trend_report=trend, kpi_report=kpi)
    checklist = build_alpha_release_checklist(matrix, trend_report=trend, kpi_report=kpi)

    write_json(args.matrix_output, matrix)
    write_json(args.checklist_output, checklist)

    if args.manifest_output:
        manifest = build_release_bundle_manifest(args.artifacts or [])
        write_json(args.manifest_output, manifest)


if __name__ == "__main__":
    main()
