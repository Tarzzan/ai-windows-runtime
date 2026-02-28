from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from compat_runtime.common.io import read_json, write_json


def _count(path: str | None, key: str) -> int:
    if not path:
        return 0
    if not Path(path).exists():
        return 0
    payload = read_json(path)
    return len(payload.get(key, []))


def _valid(path: str | None) -> bool:
    if not path:
        return False
    if not Path(path).exists():
        return False
    payload = read_json(path)
    return bool(payload.get("valid", False))


def build_execution_report(
    *,
    trace_path: str,
    gaps_path: str,
    patch_plan_path: str,
    trace_validation_path: str,
    gaps_validation_path: str,
    patch_plan_validation_path: str,
    runtime_trace_path: str | None = None,
    runtime_gaps_path: str | None = None,
    runtime_patch_plan_path: str | None = None,
    runtime_trace_validation_path: str | None = None,
) -> dict:
    report = {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": {
            "base": {
                "trace_events": _count(trace_path, "events"),
                "gaps": _count(gaps_path, "gaps"),
                "proposals": _count(patch_plan_path, "proposals"),
                "validation": {
                    "trace": _valid(trace_validation_path),
                    "gaps": _valid(gaps_validation_path),
                    "patch_plan": _valid(patch_plan_validation_path),
                },
            },
            "runtime": {
                "trace_events": _count(runtime_trace_path, "events"),
                "gaps": _count(runtime_gaps_path, "gaps"),
                "proposals": _count(runtime_patch_plan_path, "proposals"),
                "validation": {
                    "trace": _valid(runtime_trace_validation_path),
                },
            },
        },
    }

    base_validation_ok = all(report["pipeline"]["base"]["validation"].values())
    runtime_validation = report["pipeline"]["runtime"]["validation"]["trace"]
    runtime_required = report["pipeline"]["runtime"]["trace_events"] > 0
    runtime_ok = runtime_validation if runtime_required else True
    report["status"] = "ok" if (base_validation_ok and runtime_ok) else "failed"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build machine-readable execution report from artifact outputs"
    )
    parser.add_argument("--trace", required=True, help="Base trace JSON path")
    parser.add_argument("--gaps", required=True, help="Base gaps JSON path")
    parser.add_argument("--patch-plan", required=True, help="Base patch plan JSON path")
    parser.add_argument(
        "--trace-validation", required=True, help="Base trace validation report path"
    )
    parser.add_argument(
        "--gaps-validation", required=True, help="Base gaps validation report path"
    )
    parser.add_argument(
        "--patch-plan-validation",
        required=True,
        help="Base patch-plan validation report path",
    )
    parser.add_argument(
        "--runtime-trace",
        required=False,
        help="Optional runtime trace JSON path",
    )
    parser.add_argument(
        "--runtime-gaps",
        required=False,
        help="Optional runtime gaps JSON path",
    )
    parser.add_argument(
        "--runtime-patch-plan",
        required=False,
        help="Optional runtime patch plan JSON path",
    )
    parser.add_argument(
        "--runtime-trace-validation",
        required=False,
        help="Optional runtime trace validation report path",
    )
    parser.add_argument("--output", required=True, help="Execution report JSON output")
    args = parser.parse_args()

    report = build_execution_report(
        trace_path=args.trace,
        gaps_path=args.gaps,
        patch_plan_path=args.patch_plan,
        trace_validation_path=args.trace_validation,
        gaps_validation_path=args.gaps_validation,
        patch_plan_validation_path=args.patch_plan_validation,
        runtime_trace_path=args.runtime_trace,
        runtime_gaps_path=args.runtime_gaps,
        runtime_patch_plan_path=args.runtime_patch_plan,
        runtime_trace_validation_path=args.runtime_trace_validation,
    )
    write_json(args.output, report)


if __name__ == "__main__":
    main()
