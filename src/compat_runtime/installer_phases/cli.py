from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


PHASE_RULES = [
    ("bootstrap", ["bootstrap", "createprocess", "setup", "c2r"]),
    ("network_handshake", ["winhttp", "http", "download", "network"]),
    ("registry_config", ["reg", "registry"]),
    ("file_stage", ["file", "write", "extract", "copy"]),
    ("finalize", ["success", "final", "closehandle", "terminateprocess"]),
]


def _detect_phase(event: dict) -> str:
    text = f"{event.get('message', '')} {event.get('action', '')} {event.get('stage', '')}".lower()
    for phase, keywords in PHASE_RULES:
        if any(keyword in text for keyword in keywords):
            return phase
    return "runtime_misc"


def _detect_status(event: dict) -> str:
    stage = str(event.get("stage", "")).lower()
    if stage == "error":
        return "error"

    severity = str(event.get("severity", "low")).lower()
    message = str(event.get("message", "")).lower()
    if severity == "high" or any(word in message for word in ["failed", "error", "timeout"]):
        return "error"
    if stage in {"success", "ok"}:
        return "success"
    return "progress"


def _ingest(source_name: str, payload: dict | None) -> list[dict]:
    if not payload:
        return []
    rows = []
    for event in payload.get("events", []):
        phase = _detect_phase(event)
        status = _detect_status(event)
        rows.append(
            {
                "timestamp": event.get("timestamp"),
                "source": source_name,
                "phase": phase,
                "status": status,
                "category": str(event.get("category", "runtime")),
                "message": str(event.get("message", "")),
            }
        )
    return rows


def _phase_rollup(entries: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for entry in entries:
        phase = entry["phase"]
        if phase not in grouped:
            grouped[phase] = {
                "phase": phase,
                "events": 0,
                "errors": 0,
                "success": 0,
                "progress": 0,
                "first_seen": entry.get("timestamp"),
                "last_seen": entry.get("timestamp"),
            }
        row = grouped[phase]
        row["events"] += 1
        status = entry["status"]
        if status == "error":
            row["errors"] += 1
        elif status == "success":
            row["success"] += 1
        else:
            row["progress"] += 1
        ts = entry.get("timestamp")
        if row["first_seen"] is None and ts is not None:
            row["first_seen"] = ts
        if ts is not None:
            row["last_seen"] = ts

    ordered = sorted(grouped.values(), key=lambda x: (-x["events"], x["phase"]))
    for row in ordered:
        if row["errors"] > 0:
            row["phase_status"] = "error"
        elif row["success"] > 0:
            row["phase_status"] = "success"
        else:
            row["phase_status"] = "progress"
    return ordered


def _actions(has_error: bool, phase_count: int) -> list[str]:
    actions = []
    if has_error:
        actions.append("Prioritize installer phases marked with error status for triage.")
    if phase_count > 0:
        actions.append("Use installer-phase-report.json to align runtime instrumentation with failures.")
    if not actions:
        actions.append("No installer phase markers detected. Capture richer installer traces.")
    return actions


def build_installer_phase_report(
    *,
    trace: dict | None = None,
    runtime_trace: dict | None = None,
) -> dict:
    timeline = _ingest("trace", trace) + _ingest("runtime-trace", runtime_trace)
    phases = _phase_rollup(timeline)
    error_events = sum(1 for event in timeline if event["status"] == "error")
    has_error = error_events > 0

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "events_scanned": len(timeline),
            "phases_detected": len(phases),
            "error_events": error_events,
            "has_errors": has_error,
        },
        "phases": phases,
        "timeline": timeline[:120],
        "actions": _actions(has_error=has_error, phase_count=len(phases)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build installer phase marker report")
    parser.add_argument("--trace", required=False, help="Base trace JSON path")
    parser.add_argument("--runtime-trace", required=False, help="Runtime trace JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    trace = read_json(args.trace) if args.trace else None
    runtime_trace = read_json(args.runtime_trace) if args.runtime_trace else None
    artifact = build_installer_phase_report(trace=trace, runtime_trace=runtime_trace)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

