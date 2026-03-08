#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PHASE_DOC_RE = re.compile(r"^(\d+)-phase-(\d+)-(.+)\.md$")
CAPABILITY_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
CURRENT_PHASE_RE = re.compile(r"Current scope \(Phase (\d+)\)")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def sh(repo: Path, *args: str) -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(repo), *args], text=True)
        return out.strip()
    except Exception:
        return ""


def parse_readme(readme_path: Path) -> dict[str, Any]:
    text = read_text(readme_path)
    current_phase = 0
    m = CURRENT_PHASE_RE.search(text)
    if m:
        current_phase = int(m.group(1))

    capabilities: list[str] = []
    in_capabilities = False
    for line in text.splitlines():
        if "Core runtime capabilities" in line:
            in_capabilities = True
            continue
        if in_capabilities and line.startswith("## "):
            break
        if in_capabilities:
            cap = CAPABILITY_RE.match(line)
            if cap:
                capabilities.append(cap.group(1).strip())

    return {
        "current_phase": current_phase,
        "capabilities_count": len(capabilities),
        "capabilities_preview": capabilities[-10:],
    }


def parse_phase_docs(docs_dir: Path, current_phase: int) -> list[dict[str, Any]]:
    phases: list[dict[str, Any]] = []
    for p in sorted(docs_dir.iterdir() if docs_dir.exists() else [], key=lambda x: x.name):
        m = PHASE_DOC_RE.match(p.name)
        if not m:
            continue
        phase_num = int(m.group(2))
        slug = m.group(3)
        title_line = read_text(p).splitlines()[0] if p.exists() else ""
        title = title_line.lstrip("# ").strip() if title_line.startswith("#") else slug
        status = "planned"
        if phase_num < current_phase:
            status = "completed"
        elif phase_num == current_phase:
            status = "in_progress"

        phases.append(
            {
                "phase": phase_num,
                "title": title,
                "slug": slug,
                "status": status,
                "file": f"docs/{p.name}",
            }
        )

    return sorted(phases, key=lambda x: x["phase"])


def parse_backlog(backlog_path: Path) -> list[str]:
    text = read_text(backlog_path)
    items: list[str] = []
    for line in text.splitlines():
        m = CAPABILITY_RE.match(line)
        if m:
            items.append(m.group(1).strip())
    return items[:30]


def gather_validation(validation_dir: Path) -> dict[str, Any]:
    reports = sorted(validation_dir.glob("*-validation.json")) if validation_dir.exists() else []
    total = len(reports)
    invalid: list[str] = []
    valid = 0
    for p in reports:
        data = read_json(p, {})
        if bool(data.get("valid", False)):
            valid += 1
        else:
            invalid.append(p.name)
    rate = round((valid / total) * 100, 2) if total else 0.0
    return {
        "total": total,
        "valid": valid,
        "invalid": len(invalid),
        "valid_rate": rate,
        "invalid_files": invalid[:20],
    }


def gather_commits(repo: Path, limit: int = 15) -> list[dict[str, str]]:
    raw = sh(
        repo,
        "log",
        f"-n{limit}",
        "--date=iso",
        "--pretty=format:%H%x1f%h%x1f%ad%x1f%s",
    )
    commits: list[dict[str, str]] = []
    if not raw:
        return commits
    for row in raw.splitlines():
        parts = row.split("\x1f")
        if len(parts) != 4:
            continue
        commits.append(
            {
                "hash": parts[0],
                "short": parts[1],
                "date": parts[2],
                "subject": parts[3],
            }
        )
    return commits


def build_dashboard_data(repo: Path) -> dict[str, Any]:
    readme = parse_readme(repo / "README.md")
    phases = parse_phase_docs(repo / "docs", readme["current_phase"])
    backlog = parse_backlog(repo / "docs" / "50-backlog.md")

    out_dir = repo / "out"
    quality_gate = read_json(out_dir / "quality-gate-report.json", {})
    release_decision = read_json(out_dir / "release-decision-report.json", {})
    launch_readiness = read_json(out_dir / "launch-readiness-report.json", {})
    release_policy = read_json(out_dir / "release-policy-report.json", {})
    execution_confidence = read_json(out_dir / "execution-confidence-report.json", {})
    execution_momentum = read_json(out_dir / "execution-momentum-report.json", {})
    execution_pressure = read_json(out_dir / "execution-pressure-report.json", {})
    delivery_temperature = read_json(out_dir / "delivery-temperature-report.json", {})
    control_recommendation = read_json(out_dir / "control-recommendation-report.json", {})
    control_efficiency = read_json(out_dir / "control-efficiency-report.json", {})
    intervention_plan = read_json(out_dir / "intervention-plan-report.json", {})
    governance_friction = read_json(out_dir / "governance-friction-report.json", {})
    cadence_recommendation = read_json(out_dir / "cadence-recommendation-report.json", {})
    execution_focus = read_json(out_dir / "execution-focus-report.json", {})
    owner_load = read_json(out_dir / "owner-load-report.json", {})
    execution_throttle = read_json(out_dir / "execution-throttle-report.json", {})
    priority_corridor = read_json(out_dir / "priority-corridor-report.json", {})
    queue_pressure = read_json(out_dir / "queue-pressure-report.json", {})
    delivery_bandwidth = read_json(out_dir / "delivery-bandwidth-report.json", {})
    intake_guard = read_json(out_dir / "intake-guard-report.json", {})
    intake_capacity = read_json(out_dir / "intake-capacity-report.json", {})
    admission_control = read_json(out_dir / "admission-control-report.json", {})
    commitment_pacing = read_json(out_dir / "commitment-pacing-report.json", {})
    scope_budget = read_json(out_dir / "scope-budget-report.json", {})
    admission_window = read_json(out_dir / "admission-window-report.json", {})
    commitment_guard = read_json(out_dir / "commitment-guard-report.json", {})
    portfolio_risk_budget = read_json(out_dir / "portfolio-risk-budget-report.json", {})
    delivery_intake_sync = read_json(out_dir / "delivery-intake-sync-report.json", {})
    execution_reserve = read_json(out_dir / "execution-reserve-report.json", {})
    capacity_buffer = read_json(out_dir / "capacity-buffer-report.json", {})
    intake_queue_policy = read_json(out_dir / "intake-queue-policy-report.json", {})
    scope_rebalance = read_json(out_dir / "scope-rebalance-report.json", {})
    flow_control_budget = read_json(out_dir / "flow-control-budget-report.json", {})
    intake_release_window = read_json(out_dir / "intake-release-window-report.json", {})
    execution_stability_guard = read_json(out_dir / "execution-stability-guard-report.json", {})
    delivery_safety_margin = read_json(out_dir / "delivery-safety-margin-report.json", {})
    intake_commitment_window = read_json(out_dir / "intake-commitment-window-report.json", {})
    scope_lock_state = read_json(out_dir / "scope-lock-state-report.json", {})
    throughput_guard_band = read_json(out_dir / "throughput-guard-band-report.json", {})
    intake_slot_policy = read_json(out_dir / "intake-slot-policy-report.json", {})
    scope_freeze_guard = read_json(out_dir / "scope-freeze-guard-report.json", {})
    risk_watchlist = read_json(out_dir / "risk-watchlist-report.json", {})
    validation = gather_validation(out_dir / "validation")

    commits = gather_commits(repo, limit=20)
    latest_commit = commits[0] if commits else {}

    max_phase = max((p["phase"] for p in phases), default=0)
    current_phase = readme["current_phase"] or max_phase
    progress_percent = round((current_phase / max_phase) * 100, 2) if max_phase else 0.0

    in_progress = [p for p in phases if p["status"] == "in_progress"]
    if not in_progress and phases:
        in_progress = [phases[-1]]

    next_actions: list[str] = []
    for source in [
        quality_gate.get("actions", []),
        release_policy.get("failures", []),
        risk_watchlist.get("actions", []),
        launch_readiness.get("actions", []),
        delivery_temperature.get("actions", []),
        control_recommendation.get("actions", []),
        control_efficiency.get("actions", []),
        intervention_plan.get("actions", []),
        governance_friction.get("actions", []),
        cadence_recommendation.get("actions", []),
        execution_focus.get("actions", []),
        owner_load.get("actions", []),
        execution_throttle.get("actions", []),
        priority_corridor.get("actions", []),
        queue_pressure.get("actions", []),
        delivery_bandwidth.get("actions", []),
        intake_guard.get("actions", []),
        intake_capacity.get("actions", []),
        admission_control.get("actions", []),
        commitment_pacing.get("actions", []),
        scope_budget.get("actions", []),
        admission_window.get("actions", []),
        commitment_guard.get("actions", []),
        portfolio_risk_budget.get("actions", []),
        delivery_intake_sync.get("actions", []),
        execution_reserve.get("actions", []),
        capacity_buffer.get("actions", []),
        intake_queue_policy.get("actions", []),
        scope_rebalance.get("actions", []),
        flow_control_budget.get("actions", []),
        intake_release_window.get("actions", []),
        execution_stability_guard.get("actions", []),
        delivery_safety_margin.get("actions", []),
        intake_commitment_window.get("actions", []),
        scope_lock_state.get("actions", []),
        throughput_guard_band.get("actions", []),
        intake_slot_policy.get("actions", []),
        scope_freeze_guard.get("actions", []),
    ]:
        for item in source:
            text = str(item).strip()
            if text and text not in next_actions:
                next_actions.append(text)

    status = {
        "quality_gate": quality_gate.get("gate", "unknown"),
        "release_decision": release_decision.get("decision", "unknown"),
        "launch_readiness": launch_readiness.get("status", "unknown"),
        "policy_status": release_policy.get("status", "missing"),
        "policy_compliance": (release_policy.get("summary", {}) or {}).get(
            "policy_compliance_level", "unknown"
        ),
        "execution_confidence_band": (execution_confidence.get("summary", {}) or {}).get(
            "confidence_band", "unknown"
        ),
        "execution_mode": (execution_confidence.get("summary", {}) or {}).get(
            "execution_mode", "unknown"
        ),
        "momentum_posture": (execution_momentum.get("summary", {}) or {}).get(
            "posture", "unknown"
        ),
        "momentum_index": (execution_momentum.get("summary", {}) or {}).get(
            "momentum_index", 0
        ),
        "pressure_level": (execution_pressure.get("summary", {}) or {}).get(
            "pressure_level", "unknown"
        ),
        "pressure_index": (execution_pressure.get("summary", {}) or {}).get(
            "pressure_index", 0
        ),
        "temperature": (delivery_temperature.get("summary", {}) or {}).get(
            "temperature", "unknown"
        ),
        "temperature_index": (delivery_temperature.get("summary", {}) or {}).get(
            "temperature_index", 0
        ),
        "control_mode": (control_recommendation.get("summary", {}) or {}).get(
            "control_mode", "unknown"
        ),
        "efficiency_band": (control_efficiency.get("summary", {}) or {}).get(
            "efficiency_band", "unknown"
        ),
        "efficiency_score": (control_efficiency.get("summary", {}) or {}).get(
            "efficiency_score", 0
        ),
        "intervention_mode": (intervention_plan.get("summary", {}) or {}).get(
            "intervention_mode", "unknown"
        ),
        "friction_band": (governance_friction.get("summary", {}) or {}).get(
            "friction_band", "unknown"
        ),
        "friction_score": (governance_friction.get("summary", {}) or {}).get(
            "friction_score", 0
        ),
        "cadence": (cadence_recommendation.get("summary", {}) or {}).get(
            "cadence", "unknown"
        ),
        "focus_items": (execution_focus.get("summary", {}) or {}).get(
            "p0_focus_items", 0
        ),
        "owners_in_scope": (execution_focus.get("summary", {}) or {}).get(
            "owners_in_scope", 0
        ),
        "overloaded_owners": (owner_load.get("summary", {}) or {}).get(
            "overloaded_owners", 0
        ),
        "throttle_mode": (execution_throttle.get("summary", {}) or {}).get(
            "throttle_mode", "unknown"
        ),
        "priority_corridor": (priority_corridor.get("summary", {}) or {}).get(
            "priority_corridor", "unknown"
        ),
        "queue_pressure_band": (queue_pressure.get("summary", {}) or {}).get(
            "queue_pressure_band", "unknown"
        ),
        "queue_pressure_score": (queue_pressure.get("summary", {}) or {}).get(
            "queue_pressure_score", 0
        ),
        "bandwidth_mode": (delivery_bandwidth.get("summary", {}) or {}).get(
            "bandwidth_mode", "unknown"
        ),
        "bandwidth_score": (delivery_bandwidth.get("summary", {}) or {}).get(
            "bandwidth_score", 0
        ),
        "intake_guard": (intake_guard.get("summary", {}) or {}).get(
            "intake_guard", "unknown"
        ),
        "intake_capacity_mode": (intake_capacity.get("summary", {}) or {}).get(
            "intake_capacity_mode", "unknown"
        ),
        "intake_capacity_score": (intake_capacity.get("summary", {}) or {}).get(
            "intake_capacity_score", 0
        ),
        "admission_state": (admission_control.get("summary", {}) or {}).get(
            "admission_state", "unknown"
        ),
        "commitment_mode": (commitment_pacing.get("summary", {}) or {}).get(
            "commitment_mode", "unknown"
        ),
        "scope_budget_mode": (scope_budget.get("summary", {}) or {}).get(
            "scope_budget_mode", "unknown"
        ),
        "scope_budget_score": (scope_budget.get("summary", {}) or {}).get(
            "scope_budget_score", 0
        ),
        "admission_window": (admission_window.get("summary", {}) or {}).get(
            "admission_window", "unknown"
        ),
        "commitment_guard": (commitment_guard.get("summary", {}) or {}).get(
            "commitment_guard", "unknown"
        ),
        "risk_budget_mode": (portfolio_risk_budget.get("summary", {}) or {}).get(
            "risk_budget_mode", "unknown"
        ),
        "risk_budget_score": (portfolio_risk_budget.get("summary", {}) or {}).get(
            "risk_budget_score", 0
        ),
        "delivery_intake_sync": (delivery_intake_sync.get("summary", {}) or {}).get(
            "delivery_intake_sync", "unknown"
        ),
        "execution_reserve": (execution_reserve.get("summary", {}) or {}).get(
            "execution_reserve", "unknown"
        ),
        "capacity_buffer_band": (capacity_buffer.get("summary", {}) or {}).get(
            "capacity_buffer_band", "unknown"
        ),
        "capacity_buffer_score": (capacity_buffer.get("summary", {}) or {}).get(
            "capacity_buffer_score", 0
        ),
        "intake_queue_policy": (intake_queue_policy.get("summary", {}) or {}).get(
            "intake_queue_policy", "unknown"
        ),
        "scope_rebalance": (scope_rebalance.get("summary", {}) or {}).get(
            "scope_rebalance", "unknown"
        ),
        "flow_control_mode": (flow_control_budget.get("summary", {}) or {}).get(
            "flow_control_mode", "unknown"
        ),
        "flow_control_score": (flow_control_budget.get("summary", {}) or {}).get(
            "flow_control_score", 0
        ),
        "intake_release_window": (intake_release_window.get("summary", {}) or {}).get(
            "intake_release_window", "unknown"
        ),
        "execution_stability_guard": (execution_stability_guard.get("summary", {}) or {}).get(
            "execution_stability_guard", "unknown"
        ),
        "safety_margin_band": (delivery_safety_margin.get("summary", {}) or {}).get(
            "safety_margin_band", "unknown"
        ),
        "safety_margin_score": (delivery_safety_margin.get("summary", {}) or {}).get(
            "safety_margin_score", 0
        ),
        "intake_commitment_window": (intake_commitment_window.get("summary", {}) or {}).get(
            "intake_commitment_window", "unknown"
        ),
        "scope_lock_state": (scope_lock_state.get("summary", {}) or {}).get(
            "scope_lock_state", "unknown"
        ),
        "throughput_guard_band": (throughput_guard_band.get("summary", {}) or {}).get(
            "throughput_guard_band", "unknown"
        ),
        "throughput_guard_score": (throughput_guard_band.get("summary", {}) or {}).get(
            "throughput_guard_score", 0
        ),
        "intake_slot_policy": (intake_slot_policy.get("summary", {}) or {}).get(
            "intake_slot_policy", "unknown"
        ),
        "scope_freeze_guard": (scope_freeze_guard.get("summary", {}) or {}).get(
            "scope_freeze_guard", "unknown"
        ),
    }

    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo": str(repo),
            "branch": sh(repo, "rev-parse", "--abbrev-ref", "HEAD"),
            "latest_commit": latest_commit,
        },
        "progress": {
            "current_phase": current_phase,
            "max_phase": max_phase,
            "progress_percent": progress_percent,
            "capabilities_count": readme["capabilities_count"],
            "capabilities_preview": readme["capabilities_preview"],
        },
        "status": status,
        "timeline": phases,
        "in_progress": in_progress,
        "remaining_backlog": backlog,
        "quality": {
            "validation": validation,
            "quality_gate": quality_gate,
            "release_decision": release_decision,
            "launch_readiness": launch_readiness,
            "execution_confidence": execution_confidence,
            "execution_momentum": execution_momentum,
            "execution_pressure": execution_pressure,
            "delivery_temperature": delivery_temperature,
            "control_recommendation": control_recommendation,
            "control_efficiency": control_efficiency,
            "intervention_plan": intervention_plan,
            "governance_friction": governance_friction,
            "cadence_recommendation": cadence_recommendation,
            "execution_focus": execution_focus,
            "owner_load": owner_load,
            "execution_throttle": execution_throttle,
            "priority_corridor": priority_corridor,
            "queue_pressure": queue_pressure,
            "delivery_bandwidth": delivery_bandwidth,
            "intake_guard": intake_guard,
            "intake_capacity": intake_capacity,
            "admission_control": admission_control,
            "commitment_pacing": commitment_pacing,
            "scope_budget": scope_budget,
            "admission_window": admission_window,
            "commitment_guard": commitment_guard,
            "portfolio_risk_budget": portfolio_risk_budget,
            "delivery_intake_sync": delivery_intake_sync,
            "execution_reserve": execution_reserve,
            "capacity_buffer": capacity_buffer,
            "intake_queue_policy": intake_queue_policy,
            "scope_rebalance": scope_rebalance,
            "flow_control_budget": flow_control_budget,
            "intake_release_window": intake_release_window,
            "execution_stability_guard": execution_stability_guard,
            "delivery_safety_margin": delivery_safety_margin,
            "intake_commitment_window": intake_commitment_window,
            "scope_lock_state": scope_lock_state,
            "throughput_guard_band": throughput_guard_band,
            "intake_slot_policy": intake_slot_policy,
            "scope_freeze_guard": scope_freeze_guard,
        },
        "risks": {
            "summary": risk_watchlist.get("summary", {}),
            "entries": risk_watchlist.get("entries", [])[:50],
        },
        "next_actions": next_actions[:20],
        "commits": commits,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build dashboard data JSON")
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]), help="Repo root")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    payload = build_dashboard_data(repo)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"dashboard data: {out}")


if __name__ == "__main__":
    main()
