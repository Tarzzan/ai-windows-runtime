from __future__ import annotations

import argparse
import hashlib
import platform
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import read_json, write_json


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _artifact_entry(path: str) -> dict:
    file_path = Path(path)
    exists = file_path.exists()
    entry: dict = {"path": path, "exists": exists}
    if exists:
        entry["size_bytes"] = file_path.stat().st_size
        entry["sha256"] = _sha256(file_path)
    else:
        entry["size_bytes"] = 0
        entry["sha256"] = ""
    return entry


def _execution_failures(execution_report: dict) -> list[dict]:
    failures: list[dict] = []
    status = str(execution_report.get("status", "unknown"))
    if status != "ok":
        failures.append(
            {
                "source": "execution_report",
                "id": "pipeline_status",
                "status": status,
                "details": {
                    "base_trace_events": execution_report.get("pipeline", {})
                    .get("base", {})
                    .get("trace_events", 0),
                    "runtime_trace_events": execution_report.get("pipeline", {})
                    .get("runtime", {})
                    .get("trace_events", 0),
                },
            }
        )
    return failures


def _matrix_failures(compatibility_matrix: dict) -> list[dict]:
    failures: list[dict] = []
    for scenario in compatibility_matrix.get("scenarios", []):
        status = str(scenario.get("status", "unknown"))
        if status != "pass":
            failures.append(
                {
                    "source": "compatibility_matrix",
                    "id": str(scenario.get("id", "unknown-scenario")),
                    "status": status,
                    "details": {
                        "gaps": int(scenario.get("gaps", 0)),
                        "proposals": int(scenario.get("proposals", 0)),
                        "evidence": str(scenario.get("evidence", "")),
                    },
                }
            )
    return failures


def _checklist_issues(alpha_checklist: dict | None) -> list[dict]:
    if not alpha_checklist:
        return []

    issues: list[dict] = []
    for item in alpha_checklist.get("items", []):
        status = str(item.get("status", "unknown"))
        if status in {"fail", "warn"}:
            issues.append(
                {
                    "source": "alpha_release_checklist",
                    "id": str(item.get("id", "unknown-item")),
                    "status": status,
                    "details": {
                        "required": bool(item.get("required", False)),
                        "title": str(item.get("title", "")),
                        "evidence": str(item.get("evidence", "")),
                    },
                }
            )
    return issues


def _deterministic_id(failures: list[dict], artifacts: list[dict]) -> str:
    h = hashlib.sha256()
    for failure in sorted(failures, key=lambda x: (x.get("source", ""), x.get("id", ""))):
        h.update(str(failure.get("source", "")).encode("utf-8"))
        h.update(str(failure.get("id", "")).encode("utf-8"))
        h.update(str(failure.get("status", "")).encode("utf-8"))
    for artifact in sorted(artifacts, key=lambda x: x.get("path", "")):
        h.update(str(artifact.get("path", "")).encode("utf-8"))
        h.update(str(artifact.get("sha256", "")).encode("utf-8"))
        h.update(str(artifact.get("exists", False)).encode("utf-8"))
    return h.hexdigest()


def build_repro_package(
    execution_report: dict,
    compatibility_matrix: dict,
    *,
    alpha_checklist: dict | None = None,
    artifacts: list[str] | None = None,
) -> dict:
    artifact_entries = [_artifact_entry(path) for path in (artifacts or [])]

    failures = []
    failures.extend(_execution_failures(execution_report))
    failures.extend(_matrix_failures(compatibility_matrix))
    failures.extend(_checklist_issues(alpha_checklist))

    existing_artifacts = sum(1 for artifact in artifact_entries if artifact["exists"])
    missing_artifacts = len(artifact_entries) - existing_artifacts

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "deterministic_id": _deterministic_id(failures, artifact_entries),
        "ready_for_repro": len(failures) > 0,
        "summary": {
            "failure_count": len(failures),
            "artifact_count": len(artifact_entries),
            "existing_artifacts": existing_artifacts,
            "missing_artifacts": missing_artifacts,
        },
        "environment": {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
        },
        "failure_targets": failures,
        "reproduction_steps": {
            "recommended_commands": [
                "scripts/run-full-pipeline.sh out",
                "scripts/build-repro-package.sh out",
            ],
            "notes": [
                "Run on a clean Ubuntu host or isolated user profile.",
                "Attach referenced artifacts when opening an issue.",
            ],
        },
        "artifacts": artifact_entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic reproduction package")
    parser.add_argument("--execution-report", required=True, help="Execution report input path")
    parser.add_argument(
        "--compatibility-matrix", required=True, help="Compatibility matrix input path"
    )
    parser.add_argument(
        "--alpha-checklist", required=False, help="Optional alpha release checklist input path"
    )
    parser.add_argument("--output", required=True, help="Repro package output path")
    parser.add_argument(
        "--artifacts",
        required=False,
        nargs="*",
        help="Optional artifact list to hash and include in package",
    )
    args = parser.parse_args()

    execution = read_json(args.execution_report)
    matrix = read_json(args.compatibility_matrix)
    checklist = read_json(args.alpha_checklist) if args.alpha_checklist else None

    package = build_repro_package(
        execution,
        matrix,
        alpha_checklist=checklist,
        artifacts=args.artifacts,
    )
    write_json(args.output, package)


if __name__ == "__main__":
    main()

