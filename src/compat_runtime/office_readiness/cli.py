from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


OFFICE_DOMAINS = {"com", "winrt", "registry", "installer"}


def _clamp_ratio(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _bootstrap_phase(installer_phase_report: dict) -> dict:
    phases = installer_phase_report.get("phases", [])
    for phase in phases:
        if isinstance(phase, dict) and "bootstrap" in str(phase.get("phase", "")).lower():
            return phase
    return {}


def _bootstrap_coverage(bootstrap_phase: dict, runtime_signal_report: dict) -> float:
    if bootstrap_phase:
        # Preferred ratio field, if present from richer installer rollups.
        completion_ratio = bootstrap_phase.get("completion_ratio")
        if isinstance(completion_ratio, (int, float)):
            return _clamp_ratio(float(completion_ratio))

        # Legacy mode where progress is a percent integer [0..100].
        progress = bootstrap_phase.get("progress")
        events = int(bootstrap_phase.get("events", 0))
        if isinstance(progress, (int, float)) and events <= 1 and float(progress) > 1.0:
            return _clamp_ratio(float(progress) / 100.0)

        # Phase rollup mode where progress/success/errors are counters.
        success = int(bootstrap_phase.get("success", 0))
        progress_count = int(bootstrap_phase.get("progress", 0))
        errors = int(bootstrap_phase.get("errors", 0))
        observed = events if events > 0 else success + progress_count + errors
        if observed > 0:
            non_error = max(observed - errors, 0)
            return _clamp_ratio(non_error / observed)

    return float(runtime_signal_report.get("summary", {}).get("hook_coverage_ratio", 0.0))


def _replay_stability(stability_window_report: dict) -> str:
    value = str(stability_window_report.get("summary", {}).get("window_status", "unstable"))
    if value in {"stable", "watch", "unstable"}:
        return value
    return "unstable"


def _office_p0_items(hook_backlog_report: dict) -> int:
    items = hook_backlog_report.get("items", [])
    if not isinstance(items, list) or not items:
        return int(hook_backlog_report.get("summary", {}).get("p0_items", 0))

    return sum(
        1
        for item in items
        if isinstance(item, dict)
        and item.get("domain") in OFFICE_DOMAINS
        and bool(item.get("missing_hook", False))
        and str(item.get("urgency", "")).upper() == "P0"
    )


def _status(coverage: float, unresolved_p0: int, stability: str, bootstrap_has_errors: bool) -> str:
    if coverage >= 0.8 and unresolved_p0 == 0 and stability in {"stable", "watch"} and not bootstrap_has_errors:
        return "ready"
    if coverage >= 0.45 and unresolved_p0 <= 2 and not (bootstrap_has_errors and unresolved_p0 > 1):
        return "limited"
    return "blocked"


def _actions(status: str) -> list[str]:
    if status == "ready":
        return [
            "Run Office bootstrap validation pack on every release candidate.",
            "Track COM and registry failures in runtime signal reports for drift detection.",
        ]
    if status == "limited":
        return [
            "Resolve remaining P0 Office hook items before broad installer rollout.",
            "Increase bootstrap coverage with deterministic replay traces.",
        ]
    return [
        "Office readiness is blocked: prioritize unresolved P0 hook backlog items.",
        "Stabilize replay window and re-run installer/bootstrap validation before next phase.",
    ]


def build_office_readiness_report(
    *,
    runtime_signal_report: dict,
    hook_backlog_report: dict,
    stability_window_report: dict,
    installer_phase_report: dict,
) -> dict:
    runtime_summary = runtime_signal_report.get("summary", {})
    bootstrap_phase = _bootstrap_phase(installer_phase_report)

    coverage = _bootstrap_coverage(bootstrap_phase, runtime_signal_report)
    unresolved_p0 = _office_p0_items(hook_backlog_report)
    stability = _replay_stability(stability_window_report)
    com_failures = int(runtime_summary.get("com_failures", 0))
    registry_failures = int(runtime_summary.get("registry_failures", 0))
    installer_failures = int(runtime_summary.get("installer_failures", 0))
    bootstrap_errors = int(bootstrap_phase.get("errors", 0)) if bootstrap_phase else 0
    installer_has_errors = bootstrap_errors > 0

    status = _status(coverage, unresolved_p0, stability, installer_has_errors)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "bootstrap_coverage": round(coverage, 4),
            "unresolved_p0_items": unresolved_p0,
            "replay_stability": stability,
            "com_failures": com_failures,
            "registry_failures": registry_failures,
            "installer_failures": installer_failures,
            "installer_has_errors": installer_has_errors,
            "bootstrap_phase_events": int(bootstrap_phase.get("events", 0)) if bootstrap_phase else 0,
            "bootstrap_phase_errors": bootstrap_errors,
        },
        "actions": _actions(status),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Office readiness report")
    parser.add_argument("--runtime-signal-report", required=True, help="Runtime signal report path")
    parser.add_argument("--hook-backlog-report", required=True, help="Hook backlog report path")
    parser.add_argument("--stability-window-report", required=True, help="Stability window report path")
    parser.add_argument("--installer-phase-report", required=True, help="Installer phase report path")
    parser.add_argument("--output", required=True, help="Output report path")
    args = parser.parse_args()

    artifact = build_office_readiness_report(
        runtime_signal_report=read_json(args.runtime_signal_report),
        hook_backlog_report=read_json(args.hook_backlog_report),
        stability_window_report=read_json(args.stability_window_report),
        installer_phase_report=read_json(args.installer_phase_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
