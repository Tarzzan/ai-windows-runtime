from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


HOOK_DOMAINS = ["com", "winrt", "registry", "network", "installer"]


def _is_error(event: dict) -> bool:
    severity = str(event.get("severity", "low")).lower()
    stage = str(event.get("stage", "")).lower()
    message = str(event.get("message", "")).lower()
    return severity == "high" or stage == "error" or "error" in message or "failed" in message


def _domains_for_event(event: dict) -> list[str]:
    category = str(event.get("category", "")).lower()
    action = str(event.get("action", "")).lower()
    message = str(event.get("message", "")).lower()
    text = f"{category} {action} {message}"

    domains = []
    if category == "com" or "cocreateinstance" in text:
        domains.append("com")
    if "winrt" in text or "roactivateinstance" in text or "rogetactivationfactory" in text:
        domains.append("winrt")
    if category == "registry" or action.startswith("reg"):
        domains.append("registry")
    if category == "network" or "winhttp" in text or "http" in text or "tls" in text:
        domains.append("network")
    if category == "installer" or "bootstrap" in text or "c2r" in text:
        domains.append("installer")
    if (
        "crash" in text
        or "exception" in text
        or "segfault" in text
        or "access violation" in text
        or "fatal" in text
        or "timeout" in text
    ):
        domains.append("crash")

    if not domains:
        domains.append(category if category else "runtime")
    return domains


def _issue_id(source: str, domain: str, message: str) -> str:
    digest = hashlib.sha1(f"{source}|{domain}|{message}".encode("utf-8")).hexdigest()[:12]
    return f"issue-{digest}"


def _actions(coverage: list[dict], issues: list[dict]) -> list[str]:
    actions = []
    missing_hooks = [row["domain"] for row in coverage if not row["hook_present"]]
    if missing_hooks:
        actions.append(
            f"Add runtime hook evidence for missing domains: {', '.join(missing_hooks)}."
        )
    high_issues = sum(1 for issue in issues if issue.get("severity") == "high")
    if high_issues > 0:
        actions.append("Prioritize high-severity runtime issues before broad compatibility expansion.")
    if not actions:
        actions.append("Runtime signal coverage is healthy. Continue corpus expansion.")
    return actions


def build_runtime_signal_report(
    *,
    trace: dict | None = None,
    runtime_trace: dict | None = None,
) -> dict:
    per_domain: dict[str, dict] = {}
    issue_rows: list[dict] = []

    all_rows = []
    if trace:
        all_rows.extend([("trace", event) for event in trace.get("events", [])])
    if runtime_trace:
        all_rows.extend([("runtime-trace", event) for event in runtime_trace.get("events", [])])

    for source, event in all_rows:
        domains = _domains_for_event(event)
        is_error = _is_error(event)
        for domain in domains:
            if domain not in per_domain:
                per_domain[domain] = {
                    "domain": domain,
                    "events": 0,
                    "errors": 0,
                    "hook_present": False,
                    "sample_actions": [],
                }
            row = per_domain[domain]
            row["events"] += 1
            if is_error:
                row["errors"] += 1
            if source == "runtime-trace" and domain in HOOK_DOMAINS:
                row["hook_present"] = True

            action = event.get("action")
            if isinstance(action, str) and action and action not in row["sample_actions"]:
                if len(row["sample_actions"]) < 3:
                    row["sample_actions"].append(action)

        if is_error:
            primary = domains[0]
            message = str(event.get("message", "unknown runtime issue"))
            severity = str(event.get("severity", "high")).lower()
            issue_rows.append(
                {
                    "id": _issue_id(source, primary, message),
                    "source": source,
                    "domain": primary,
                    "severity": "high" if severity == "high" else "medium",
                    "timestamp": event.get("timestamp"),
                    "message": message,
                }
            )

    coverage = []
    for domain in HOOK_DOMAINS:
        row = per_domain.get(
            domain,
            {
                "domain": domain,
                "events": 0,
                "errors": 0,
                "hook_present": False,
                "sample_actions": [],
            },
        )
        coverage.append(row)

    covered_hooks = sum(1 for row in coverage if row["hook_present"])
    coverage_ratio = covered_hooks / len(HOOK_DOMAINS)
    domain_keys = [key for key, row in per_domain.items() if row["events"] > 0]
    issues = issue_rows[:20]

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "events_scanned": len(all_rows),
            "domains_detected": len(domain_keys),
            "hook_domains_total": len(HOOK_DOMAINS),
            "hook_domains_covered": covered_hooks,
            "hook_coverage_ratio": round(coverage_ratio, 3),
            "com_failures": int(per_domain.get("com", {}).get("errors", 0)),
            "winrt_failures": int(per_domain.get("winrt", {}).get("errors", 0)),
            "registry_failures": int(per_domain.get("registry", {}).get("errors", 0)),
            "network_failures": int(per_domain.get("network", {}).get("errors", 0)),
            "installer_failures": int(per_domain.get("installer", {}).get("errors", 0)),
            "crash_like_failures": int(per_domain.get("crash", {}).get("errors", 0)),
        },
        "coverage": coverage,
        "issues": issues,
        "actions": _actions(coverage, issues),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build runtime signal enrichment report")
    parser.add_argument("--trace", required=False, help="Base trace JSON path")
    parser.add_argument("--runtime-trace", required=False, help="Runtime trace JSON path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    trace = read_json(args.trace) if args.trace else None
    runtime_trace = read_json(args.runtime_trace) if args.runtime_trace else None
    artifact = build_runtime_signal_report(trace=trace, runtime_trace=runtime_trace)
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
