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


def _action_priority_score(action: str, status: dict[str, Any], risk_summary: dict[str, Any]) -> int:
    text = action.lower()
    score = 10

    for token in ["p0", "urgent", "critical", "blocker", "bloquer", "blocked", "escalate"]:
        if token in text:
            score += 18

    if any(token in text for token in ["triage", "watchlist", "risk", "risque"]):
        score += 12

    if any(token in text for token in ["stabilize", "stabilisation", "cooling", "reduce scope"]):
        score += 10

    if any(token in text for token in ["pipeline", "validation", "re-run", "re-run full"]):
        score += 8

    if any(token in text for token in ["packaging", "pilot", "launch"]):
        score += 4

    if status.get("transition_readiness_band") == "blocked" and any(
        token in text for token in ["transition", "scope", "admission"]
    ):
        score += 16

    if status.get("scope_admission_gate") == "closed" and any(
        token in text for token in ["scope", "admission", "gate"]
    ):
        score += 16

    if status.get("scope_reentry_readiness_band") == "blocked" and any(
        token in text for token in ["reentree", "reentry", "scope", "readiness"]
    ):
        score += 16

    if status.get("scope_unlock_gate") == "locked" and any(
        token in text for token in ["unlock", "deblocage", "scope", "gate"]
    ):
        score += 14

    if status.get("temperature") == "hot":
        if any(token in text for token in ["stabilize", "cooling", "scope", "risk"]):
            score += 12

    if status.get("intervention_mode") == "urgent":
        if any(token in text for token in ["urgent", "triage", "stabilize", "risk"]):
            score += 12

    p0_entries = int(risk_summary.get("p0_entries", 0))
    if p0_entries > 0 and any(token in text for token in ["p0", "triage", "watchlist", "risk"]):
        score += min(20, p0_entries * 4)

    return score


def prioritize_actions(
    actions: list[str], status: dict[str, Any], risk_summary: dict[str, Any], limit: int = 20
) -> list[str]:
    ranked = sorted(
        ((action, _action_priority_score(action, status, risk_summary)) for action in actions),
        key=lambda item: (-item[1], item[0].lower()),
    )
    return [action for action, _ in ranked[:limit]]


def build_aligned_backlog(
    *,
    current_phase: int,
    status: dict[str, Any],
    risk_summary: dict[str, Any],
    legacy_backlog: list[str],
) -> list[str]:
    items: list[str] = []
    next_phase = current_phase + 1

    items.append(
        f"Phase {next_phase}: lot de stabilisation prioritaire (P0, transition, admission) avant extension de perimetre."
    )

    if int(risk_summary.get("p0_entries", 0)) > 0:
        items.append("Assigner proprietaires + echeances sur chaque entree P0 de la watchlist.")
        items.append("Executer un triage quotidien P0 jusqu'a reduction du risque critique.")

    if status.get("transition_readiness_band") == "blocked":
        items.append("Lever le blocage de readiness de transition avec preuves de validation.")
    if status.get("scope_admission_gate") == "closed":
        items.append("Passer le gate d'admission scope de closed a guarded/open avant nouveau lot.")
    if status.get("intake_transition_policy") == "hold":
        items.append("Sortir la politique intake du mode hold avec criteres explicites.")
    if status.get("temperature") == "hot":
        items.append("Appliquer un plan de refroidissement delivery (reduction scope + boucles courtes).")
    if status.get("intervention_mode") == "urgent":
        items.append("Executer un sprint de remediations urgentes ciblees sur les chemins bloquants.")

    items.append("Relancer pipeline complet et bundle release apres chaque remediations critiques.")
    items.append("Verifier coherence dashboard: release go/ready doit rester coherent avec les signaux de risque.")
    items.append(
        f"Definir et documenter les phases {next_phase}-{next_phase + 2} sur base des ecarts restants."
    )

    # Keep a small tail of legacy backlog for context, without making it the primary roadmap.
    for legacy in legacy_backlog[:5]:
        items.append(f"[Contexte historique] {legacy}")

    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped[:30]


def localize_action(action: str) -> str:
    text = action.strip()
    replacements = [
        ("Execute urgent intervention sprint on blockers and P0 risk items.", "Executer un sprint d'intervention urgent sur les bloqueurs et les risques P0."),
        ("Stabilize commitments and avoid net-new scope until P0 backlog shrinks.", "Stabiliser les engagements et eviter tout nouveau scope tant que le backlog P0 ne baisse pas."),
        ("Maintain locked scope while P0 pressure and commitment lock remain active.", "Maintenir le scope verrouille tant que la pression P0 et le verrou d'engagement restent actifs."),
        ("Keep conservative portfolio budget until P0 risk pressure decreases.", "Maintenir un budget portefeuille conservateur tant que la pression de risque P0 ne baisse pas."),
        ("Enforce strict commitment guard until policy and P0 risk posture improve.", "Renforcer strictement le garde d'engagement tant que la policy et la posture de risque P0 ne s'ameliorent pas."),
        ("Focus on blocker burn-down before adding new implementation scope.", "Concentrer l'effort sur la reduction des bloqueurs avant d'ajouter du nouveau scope d'implementation."),
        ("Escalate P0 watchlist entries in next triage meeting.", "Escalader les entrees P0 de la watchlist a la prochaine reunion de triage."),
        ("Track P1 watchlist entries with explicit owners and due dates.", "Suivre les entrees P1 de la watchlist avec proprietaires et dates d'echeance explicites."),
        ("Authorize launch only when status is ready and guardrails stay active.", "Autoriser le lancement uniquement si le statut est pret et que les garde-fous restent actifs."),
        ("Re-run full pipeline after any critical remediation change.", "Relancer le pipeline complet apres chaque remediation critique."),
        ("Apply delivery cooling plan: reduce scope and shorten feedback loops.", "Appliquer un plan de refroidissement delivery: reduire le scope et raccourcir les boucles de feedback."),
        ("Prioritize stabilization controls on blockers and high-risk execution paths.", "Prioriser les controles de stabilisation sur les bloqueurs et les chemins d'execution a haut risque."),
        ("Quality gate is green. Proceed with release packaging and pilot validation.", "Le quality gate est au vert. Poursuivre le packaging release et la validation pilote."),
    ]
    for src, dst in replacements:
        if text == src:
            return dst
    generic = text
    generic = generic.replace("Control efficiency is low", "L'efficience du controle est faible")
    generic = generic.replace("Apply strict execution stability guard while risk pressure remains elevated.", "Appliquer strictement le garde de stabilite d'execution tant que la pression de risque reste elevee.")
    generic = generic.replace("until", "tant que")
    generic = generic.replace(" and ", " et ")
    generic = generic.replace("shorten feedback loops", "raccourcir les boucles de feedback")
    generic = generic.replace("reduce scope", "reduire le scope")
    generic = generic.replace("increase validation discipline", "renforcer la discipline de validation")
    generic = generic.replace("policy", "politique")
    return generic


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
    delivery_stress_index = read_json(out_dir / "delivery-stress-index-report.json", {})
    intake_pacing_window = read_json(out_dir / "intake-pacing-window-report.json", {})
    scope_transition_gate = read_json(out_dir / "scope-transition-gate-report.json", {})
    transition_readiness_index = read_json(out_dir / "transition-readiness-index-report.json", {})
    intake_transition_policy = read_json(out_dir / "intake-transition-policy-report.json", {})
    scope_admission_gate = read_json(out_dir / "scope-admission-gate-report.json", {})
    scope_reentry_readiness = read_json(out_dir / "scope-reentry-readiness-report.json", {})
    intake_resumption_policy = read_json(out_dir / "intake-resumption-policy-report.json", {})
    scope_unlock_gate = read_json(out_dir / "scope-unlock-gate-report.json", {})
    scope_expansion_readiness = read_json(out_dir / "scope-expansion-readiness-report.json", {})
    intake_expansion_policy = read_json(out_dir / "intake-expansion-policy-report.json", {})
    scope_expansion_gate = read_json(out_dir / "scope-expansion-gate-report.json", {})
    scope_acceleration_readiness = read_json(out_dir / "scope-acceleration-readiness-report.json", {})
    intake_acceleration_policy = read_json(out_dir / "intake-acceleration-policy-report.json", {})
    scope_acceleration_gate = read_json(out_dir / "scope-acceleration-gate-report.json", {})
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

    risk_summary = risk_watchlist.get("summary", {})

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
        "delivery_stress_band": (delivery_stress_index.get("summary", {}) or {}).get(
            "delivery_stress_band", "unknown"
        ),
        "delivery_stress_score": (delivery_stress_index.get("summary", {}) or {}).get(
            "delivery_stress_score", 0
        ),
        "intake_pacing_window": (intake_pacing_window.get("summary", {}) or {}).get(
            "intake_pacing_window", "unknown"
        ),
        "scope_transition_gate": (scope_transition_gate.get("summary", {}) or {}).get(
            "scope_transition_gate", "unknown"
        ),
        "transition_readiness_band": (transition_readiness_index.get("summary", {}) or {}).get(
            "transition_readiness_band", "unknown"
        ),
        "transition_readiness_score": (transition_readiness_index.get("summary", {}) or {}).get(
            "transition_readiness_score", 0
        ),
        "intake_transition_policy": (intake_transition_policy.get("summary", {}) or {}).get(
            "intake_transition_policy", "unknown"
        ),
        "scope_admission_gate": (scope_admission_gate.get("summary", {}) or {}).get(
            "scope_admission_gate", "unknown"
        ),
        "scope_reentry_readiness_band": (scope_reentry_readiness.get("summary", {}) or {}).get(
            "scope_reentry_readiness_band", "unknown"
        ),
        "scope_reentry_readiness_score": (scope_reentry_readiness.get("summary", {}) or {}).get(
            "scope_reentry_readiness_score", 0
        ),
        "intake_resumption_policy": (intake_resumption_policy.get("summary", {}) or {}).get(
            "intake_resumption_policy", "unknown"
        ),
        "scope_unlock_gate": (scope_unlock_gate.get("summary", {}) or {}).get(
            "scope_unlock_gate", "unknown"
        ),
        "scope_expansion_readiness_band": (scope_expansion_readiness.get("summary", {}) or {}).get(
            "scope_expansion_readiness_band", "unknown"
        ),
        "scope_expansion_readiness_score": (scope_expansion_readiness.get("summary", {}) or {}).get(
            "scope_expansion_readiness_score", 0
        ),
        "intake_expansion_policy": (intake_expansion_policy.get("summary", {}) or {}).get(
            "intake_expansion_policy", "unknown"
        ),
        "scope_expansion_gate": (scope_expansion_gate.get("summary", {}) or {}).get(
            "scope_expansion_gate", "unknown"
        ),
        "scope_acceleration_readiness_band": (scope_acceleration_readiness.get("summary", {}) or {}).get(
            "scope_acceleration_readiness_band", "unknown"
        ),
        "scope_acceleration_readiness_score": (scope_acceleration_readiness.get("summary", {}) or {}).get(
            "scope_acceleration_readiness_score", 0
        ),
        "intake_acceleration_policy": (intake_acceleration_policy.get("summary", {}) or {}).get(
            "intake_acceleration_policy", "unknown"
        ),
        "scope_acceleration_gate": (scope_acceleration_gate.get("summary", {}) or {}).get(
            "scope_acceleration_gate", "unknown"
        ),
    }

    raw_actions: list[str] = []
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
        delivery_stress_index.get("actions", []),
        intake_pacing_window.get("actions", []),
        scope_transition_gate.get("actions", []),
        transition_readiness_index.get("actions", []),
        intake_transition_policy.get("actions", []),
        scope_admission_gate.get("actions", []),
        scope_reentry_readiness.get("actions", []),
        intake_resumption_policy.get("actions", []),
        scope_unlock_gate.get("actions", []),
        scope_expansion_readiness.get("actions", []),
        intake_expansion_policy.get("actions", []),
        scope_expansion_gate.get("actions", []),
        scope_acceleration_readiness.get("actions", []),
        intake_acceleration_policy.get("actions", []),
        scope_acceleration_gate.get("actions", []),
    ]:
        for item in source:
            text = localize_action(str(item).strip())
            if text and text not in raw_actions:
                raw_actions.append(text)

    next_actions = prioritize_actions(raw_actions, status, risk_summary, limit=20)
    aligned_backlog = build_aligned_backlog(
        current_phase=current_phase,
        status=status,
        risk_summary=risk_summary,
        legacy_backlog=backlog,
    )

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
        "remaining_backlog": aligned_backlog,
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
            "delivery_stress_index": delivery_stress_index,
            "intake_pacing_window": intake_pacing_window,
            "scope_transition_gate": scope_transition_gate,
            "transition_readiness_index": transition_readiness_index,
            "intake_transition_policy": intake_transition_policy,
            "scope_admission_gate": scope_admission_gate,
            "scope_reentry_readiness": scope_reentry_readiness,
            "intake_resumption_policy": intake_resumption_policy,
            "scope_unlock_gate": scope_unlock_gate,
            "scope_expansion_readiness": scope_expansion_readiness,
            "intake_expansion_policy": intake_expansion_policy,
            "scope_expansion_gate": scope_expansion_gate,
            "scope_acceleration_readiness": scope_acceleration_readiness,
            "intake_acceleration_policy": intake_acceleration_policy,
            "scope_acceleration_gate": scope_acceleration_gate,
        },
        "risks": {
            "summary": risk_summary,
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
