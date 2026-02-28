from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


ANOMALY_KEYWORDS = [
    "crash",
    "exception",
    "segfault",
    "access violation",
    "fatal",
    "timeout",
    "failed",
    "error",
]


def _is_anomaly(event: dict) -> bool:
    severity = str(event.get("severity", "low")).lower()
    if severity == "high":
        return True
    text = str(event.get("message", "")).lower()
    return any(keyword in text for keyword in ANOMALY_KEYWORDS)


def _signature_kind(category: str, message: str) -> str:
    text = message.lower()
    if "timeout" in text:
        return "timeout"
    if any(word in text for word in ["crash", "exception", "segfault", "access violation", "fatal"]):
        return "crash"
    if "failed" in text and category == "loader":
        return "dependency"
    if category in {"registry", "file", "network", "com", "installer"}:
        return category
    return "runtime"


def _normalize_message(message: str) -> str:
    compact = message.strip().lower()
    compact = re.sub(r"0x[0-9a-f]+", "<hex>", compact)
    compact = re.sub(r"\d+", "<num>", compact)
    return compact


def _sig_id(category: str, kind: str, normalized: str) -> str:
    digest = hashlib.sha1(f"{category}|{kind}|{normalized}".encode("utf-8")).hexdigest()[:12]
    return f"sig-{digest}"


def _priority(kind: str, count: int) -> str:
    if kind == "crash":
        return "P0"
    if kind in {"timeout", "dependency"} and count >= 2:
        return "P0"
    if kind in {"timeout", "dependency", "installer", "network", "com"}:
        return "P1"
    return "P2"


def _actions(high_priority: int, total: int) -> list[str]:
    actions = []
    if high_priority > 0:
        actions.append("Prioritize P0 crash signatures before broader compatibility work.")
    if total > 0:
        actions.append("Attach crash-signature-report.json to triage tickets for reproducibility.")
    if not actions:
        actions.append("No crash signature detected. Continue collecting runtime evidence.")
    return actions


def build_crash_signature_report(
    *,
    trace: dict | None = None,
    runtime_trace: dict | None = None,
) -> dict:
    all_events = []
    if trace:
        all_events.extend([("trace", event) for event in trace.get("events", [])])
    if runtime_trace:
        all_events.extend([("runtime-trace", event) for event in runtime_trace.get("events", [])])

    buckets: dict[str, dict] = {}
    for source, event in all_events:
        if not _is_anomaly(event):
            continue
        category = str(event.get("category", "runtime"))
        message = str(event.get("message", ""))
        normalized = _normalize_message(message)
        kind = _signature_kind(category, message)
        sig = _sig_id(category, kind, normalized)

        if sig not in buckets:
            buckets[sig] = {
                "id": sig,
                "kind": kind,
                "category": category,
                "normalized_message": normalized,
                "count": 0,
                "sources": set(),
                "first_seen": event.get("timestamp"),
                "last_seen": event.get("timestamp"),
                "sample_messages": [],
            }

        row = buckets[sig]
        row["count"] += 1
        row["sources"].add(source)
        ts = event.get("timestamp")
        if row["first_seen"] is None and ts is not None:
            row["first_seen"] = ts
        if ts is not None:
            row["last_seen"] = ts
        if message and message not in row["sample_messages"] and len(row["sample_messages"]) < 3:
            row["sample_messages"].append(message)

    signatures = []
    high_priority = 0
    for row in buckets.values():
        priority = _priority(row["kind"], row["count"])
        if priority == "P0":
            high_priority += 1
        signatures.append(
            {
                "id": row["id"],
                "kind": row["kind"],
                "category": row["category"],
                "priority": priority,
                "count": row["count"],
                "sources": sorted(row["sources"]),
                "first_seen": row["first_seen"],
                "last_seen": row["last_seen"],
                "normalized_message": row["normalized_message"],
                "sample_messages": row["sample_messages"],
            }
        )

    signatures.sort(key=lambda x: (x["priority"], -x["count"], x["id"]))
    # Keep P0 first, then P1, then P2.
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    signatures.sort(key=lambda x: (priority_order.get(x["priority"], 3), -x["count"], x["id"]))

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "events_scanned": len(all_events),
            "signatures": len(signatures),
            "high_priority_signatures": high_priority,
        },
        "signatures": signatures,
        "actions": _actions(high_priority=high_priority, total=len(signatures)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build crash signature report from trace artifacts")
    parser.add_argument("--trace", required=False, help="Base trace JSON path")
    parser.add_argument("--runtime-trace", required=False, help="Runtime trace JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    trace = read_json(args.trace) if args.trace else None
    runtime_trace = read_json(args.runtime_trace) if args.runtime_trace else None
    artifact = build_crash_signature_report(trace=trace, runtime_trace=runtime_trace)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()

