from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _window(scope_mode: str, admission_state: str, focus_items: int) -> str:
    if admission_state == "gated" or scope_mode == "tight" or focus_items >= 3:
        return "restricted"
    if admission_state == "selective" or scope_mode == "balanced" or focus_items >= 1:
        return "controlled"
    return "open"


def build_admission_window_report(
    *, scope_budget_report: dict, admission_control_report: dict, execution_focus_report: dict
) -> dict:
    scope = scope_budget_report.get("summary", {})
    admission = admission_control_report.get("summary", {})
    focus = execution_focus_report.get("summary", {})

    scope_mode = str(scope.get("scope_budget_mode", "tight"))
    admission_state = str(admission.get("admission_state", "gated"))
    p0_focus_items = int(focus.get("p0_focus_items", 0))

    window_state = _window(scope_mode, admission_state, p0_focus_items)

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "admission_window": window_state,
            "scope_budget_mode": scope_mode,
            "admission_state": admission_state,
            "p0_focus_items": p0_focus_items,
        },
        "actions": [
            "Restrict admission window while focus queue remains saturated."
            if window_state == "restricted"
            else "Review admission window at each governance checkpoint."
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build admission window report")
    p.add_argument("--scope-budget-report", required=True)
    p.add_argument("--admission-control-report", required=True)
    p.add_argument("--execution-focus-report", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()

    out = build_admission_window_report(
        scope_budget_report=read_json(a.scope_budget_report),
        admission_control_report=read_json(a.admission_control_report),
        execution_focus_report=read_json(a.execution_focus_report),
    )
    write_json(a.output, out)


if __name__ == "__main__":
    main()
