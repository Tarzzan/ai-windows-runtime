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
