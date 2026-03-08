from __future__ import annotations

import argparse
from datetime import datetime, timezone

from compat_runtime.common.io import read_json, write_json


def build_evidence_catalog_report(
    *, verification_snapshot_report: dict, release_packet_report: dict, repro_package: dict
) -> dict:
    snapshot_summary = verification_snapshot_report.get("summary", {})
    packet_summary = release_packet_report.get("summary", {})
    artifacts = repro_package.get("artifacts", [])

    return {
        "artifact_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "catalog_items": len(artifacts),
            "coverage_ratio": float(snapshot_summary.get("coverage_ratio", 0.0)),
            "packet_ready": bool(packet_summary.get("packet_ready", False)),
            "bundle_missing": int(packet_summary.get("bundle_missing", 0)),
            "policy_config_valid": bool(packet_summary.get("policy_config_valid", False)),
            "policy_lockfile_sync": bool(packet_summary.get("policy_lockfile_sync", False)),
            "policy_compliance_level": str(
                packet_summary.get("policy_compliance_level", "non_compliant")
            ),
        },
        "catalog": [
            {
                "path": str(item.get("path", "")),
                "exists": bool(item.get("exists", False)),
                "checksum": str(item.get("sha256", "")),
            }
            for item in artifacts[:80]
        ],
        "actions": ["Use this catalog as evidence baseline for checkpoint and audit review."],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build evidence catalog report")
    parser.add_argument("--verification-snapshot-report", required=True, help="Verification snapshot")
    parser.add_argument("--release-packet-report", required=True, help="Release packet report")
    parser.add_argument("--repro-package", required=True, help="Repro package report")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    artifact = build_evidence_catalog_report(
        verification_snapshot_report=read_json(args.verification_snapshot_report),
        release_packet_report=read_json(args.release_packet_report),
        repro_package=read_json(args.repro_package),
    )
    write_json(args.output, artifact)


if __name__ == "__main__":
    main()
