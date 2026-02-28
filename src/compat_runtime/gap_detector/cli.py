from __future__ import annotations

import argparse
import hashlib

from compat_runtime.common.io import read_json, write_json


SEVERITY_TO_CONFIDENCE = {
    "high": 0.9,
    "medium": 0.7,
    "low": 0.5,
}


def gap_summary(category: str, message: str) -> str:
    if category == "loader":
        return f"Loader/import blocker: {message}"
    if category == "com":
        return f"COM activation/runtime blocker: {message}"
    if category == "installer":
        return f"Installer phase blocker: {message}"
    if category == "network":
        return f"Network negotiation limitation: {message}"
    if category == "sync":
        return f"Synchronization primitive limitation: {message}"
    if category == "file":
        return f"File subsystem limitation: {message}"
    if category == "registry":
        return f"Registry subsystem limitation: {message}"
    if category == "unimplemented":
        return f"Potential missing implementation: {message}"
    return f"General runtime issue: {message}"


def build_gap_id(category: str, message: str) -> str:
    digest = hashlib.sha1(f"{category}:{message}".encode("utf-8")).hexdigest()[:10]
    return f"gap-{digest}"


def detect_gaps(trace: dict) -> dict:
    gaps = []
    seen = set()
    for event in trace.get("events", []):
        category = event.get("category", "runtime")
        message = event.get("message", "")
        severity = event.get("severity", "low")
        if severity == "low":
            continue
        gap_id = build_gap_id(category, message)
        if gap_id in seen:
            continue
        seen.add(gap_id)
        gaps.append(
            {
                "id": gap_id,
                "category": category,
                "severity": severity,
                "confidence": SEVERITY_TO_CONFIDENCE.get(severity, 0.5),
                "summary": gap_summary(category, message),
            }
        )

    return {"artifact_version": "1.0", "gaps": gaps}


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect compatibility gaps from trace")
    parser.add_argument("--trace", required=True, help="Trace JSON input")
    parser.add_argument("--output", required=True, help="Gaps JSON output")
    args = parser.parse_args()

    trace = read_json(args.trace)
    gaps = detect_gaps(trace)
    write_json(args.output, gaps)


if __name__ == "__main__":
    main()
