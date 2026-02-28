from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_text, write_json


RULES = [
    ("err:module", "loader", "high"),
    ("fixme:", "unimplemented", "medium"),
    ("err:ole", "com", "high"),
    ("winhttp", "network", "medium"),
    ("c2r", "installer", "high"),
]


def infer_event(line: str) -> tuple[str, str]:
    lower = line.lower()
    for marker, category, severity in RULES:
        if marker in lower:
            return category, severity
    return "runtime", "low"


def build_trace(input_path: str) -> dict:
    events = []
    for raw in read_text(input_path).splitlines():
        text = raw.strip()
        if not text:
            continue
        category, severity = infer_event(text)
        events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "category": category,
                "message": text,
                "severity": severity,
            }
        )
    return {"artifact_version": "1.0", "events": events}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build normalized trace artifact from raw log")
    parser.add_argument("--input", required=True, help="Raw log input")
    parser.add_argument("--output", required=True, help="Trace JSON output")
    args = parser.parse_args()

    trace = build_trace(args.input)
    write_json(args.output, trace)


if __name__ == "__main__":
    main()
