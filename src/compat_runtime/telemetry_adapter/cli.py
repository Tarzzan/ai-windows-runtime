from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


SEVERITY_BY_STAGE = {
    "start": "low",
    "success": "low",
    "error": "high",
}


def infer_category(action: str) -> str:
    if action.startswith("Reg"):
        return "registry"
    if "File" in action or action == "SetFilePointerEx":
        return "file"
    if "Wait" in action or "Event" in action or "Mutex" in action:
        return "sync"
    if action in {"CreateProcessW", "TerminateProcess"}:
        return "installer"
    if (
        "Virtual" in action
        or "ProcessMemory" in action
        or action in {"CreateThread", "GetExitCodeProcess", "CloseHandle"}
    ):
        return "runtime"
    return "runtime"


def normalize_runtime_telemetry(
    telemetry: dict,
    *,
    errors_only: bool = False,
) -> dict:
    events = []
    for event in telemetry.get("events", []):
        action = event.get("action", "UnknownAction")
        stage_raw = event.get("stage", "Start")
        stage = stage_raw.lower()
        if errors_only and stage != "error":
            continue

        detail = event.get("detail")
        category = infer_category(action)
        severity = SEVERITY_BY_STAGE.get(stage, "low")

        message = f"{event.get('component', 'runtime')}.{action} {stage}"
        if detail:
            message = f"{message}: {detail}"

        events.append(
            {
                "timestamp": event.get("timestamp")
                or datetime.now(timezone.utc).isoformat(),
                "category": category,
                "message": message,
                "severity": severity,
                "source": "runtime-telemetry",
                "seq": event.get("seq"),
                "component": event.get("component"),
                "action": action,
                "stage": stage_raw,
            }
        )

    return {"artifact_version": "1.0", "events": events}


def build_trace_from_runtime_telemetry(
    telemetry: dict,
    *,
    errors_only: bool = False,
    base_trace: dict | None = None,
) -> dict:
    adapted = normalize_runtime_telemetry(telemetry, errors_only=errors_only)
    if base_trace is None:
        return adapted

    merged_events = list(base_trace.get("events", [])) + adapted["events"]
    return {
        "artifact_version": base_trace.get("artifact_version", "1.0"),
        "events": merged_events,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Adapt runtime telemetry events into trace artifact format"
    )
    parser.add_argument(
        "--telemetry", required=True, help="Runtime telemetry JSON input"
    )
    parser.add_argument("--output", required=True, help="Trace JSON output")
    parser.add_argument(
        "--base-trace",
        required=False,
        help="Optional existing trace JSON to merge with adapted telemetry",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Include only telemetry events with stage=Error",
    )
    args = parser.parse_args()

    telemetry = read_json(args.telemetry)
    base_trace = read_json(args.base_trace) if args.base_trace else None
    trace = build_trace_from_runtime_telemetry(
        telemetry,
        errors_only=args.errors_only,
        base_trace=base_trace,
    )
    write_json(args.output, trace)


if __name__ == "__main__":
    main()
