from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def _posture(momentum_index: int) -> str:
    if momentum_index >= 70:
        return "advancing"
    if momentum_index >= 40:
        return "holding"
    return "fragile"


def _actions(posture: str, p0_entries: int, incident_p0: int) -> list[str]:
    actions: list[str] = []
    if posture == "advancing":
        actions.append("Maintain execution cadence and protect validation quality gates.")
    elif posture == "holding":
        actions.append("Reduce P0 load and tighten owner deadlines to recover momentum.")
    else:
        actions.append("Freeze non-critical scope and stabilize blockers before acceleration.")

    if p0_entries > 0 or incident_p0 > 0:
        actions.append("Run focused P0 triage with explicit rollback and validation checkpoints.")
    return actions


def build_execution_momentum_report(
    *,
    execution_confidence_report: dict,
    execution_burndown_report: dict,
    release_gate_history_report: dict,
    incident_feedback_report: dict,
) -> dict:
    confidence_summary = execution_confidence_report.get("summary", {})
    burndown_summary = execution_burndown_report.get("summary", {})
    history_summary = release_gate_history_report.get("summary", {})
    incident_summary = incident_feedback_report.get("summary", {})

    confidence_score = int(confidence_summary.get("confidence_score", 0))
    trajectory = str(history_summary.get("trajectory", "stable"))
    blockers = int(burndown_summary.get("blocking_tasks", 0))
    p0_entries = int(confidence_summary.get("p0_entries", 0))
    incident_p0 = int(incident_summary.get("p0_feedback", 0))

    trajectory_delta = {"improving": 12, "stable": 0, "degrading": -12}.get(trajectory, 0)
    blocker_penalty = min(25, blockers * 3)
    incident_penalty = min(20, incident_p0 * 5)
    p0_penalty = min(20, p0_entries * 5)

    momentum_index = max(
        0,
        min(100, confidence_score + trajectory_delta - blocker_penalty - incident_penalty - p0_penalty),
    )
    posture = _posture(momentum_index)

    summary = {
        "momentum_index": momentum_index,
        "posture": posture,
        "confidence_band": str(confidence_summary.get("confidence_band", "low")),
        "execution_mode": str(confidence_summary.get("execution_mode", "stabilize")),
        "trajectory": trajectory,
        "blocking_tasks": blockers,
        "p0_entries": p0_entries,
        "incident_p0_feedback": incident_p0,
    }

    scoring = {
        "base_confidence_score": confidence_score,
        "trajectory_delta": trajectory_delta,
        "blocker_penalty": blocker_penalty,
        "incident_penalty": incident_penalty,
        "p0_penalty": p0_penalty,
    }

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "scoring": scoring,
        "actions": _actions(posture, p0_entries, incident_p0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build execution momentum report")
    parser.add_argument(
        "--execution-confidence-report", required=True, help="Execution confidence report path"
    )
    parser.add_argument("--execution-burndown-report", required=True, help="Execution burndown report path")
    parser.add_argument(
        "--release-gate-history-report", required=True, help="Release gate history report path"
    )
    parser.add_argument("--incident-feedback-report", required=True, help="Incident feedback report path")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_execution_momentum_report(
        execution_confidence_report=read_json(args.execution_confidence_report),
        execution_burndown_report=read_json(args.execution_burndown_report),
        release_gate_history_report=read_json(args.release_gate_history_report),
        incident_feedback_report=read_json(args.incident_feedback_report),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
