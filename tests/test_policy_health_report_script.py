from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build-policy-health-report.sh"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_policy_health_report_script_marks_synced_lockfile(tmp_path):
    out_dir = tmp_path / "out"
    validation_dir = out_dir / "validation"
    validation_dir.mkdir(parents=True)

    active_policy = {
        "artifact_version": "1.0",
        "policy_profile": "alpha",
        "policy": {"release_decision": {"warning_budget": 2}},
    }
    _write_json(out_dir / "active-policy.json", active_policy)
    lockfile = tmp_path / "active-policy.lock.json"
    _write_json(lockfile, active_policy)
    _write_json(validation_dir / "alpha-gating-policy-config-validation.json", {"valid": True})

    env = dict(os.environ)
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)
    result = subprocess.run(
        [str(SCRIPT), str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    payload = json.loads((out_dir / "policy-health-report.json").read_text(encoding="utf-8"))
    assert payload["lockfile_exists"] is True
    assert payload["lockfile_sync"] is True
    assert payload["config_valid"] is True
    assert payload["policy_compliance_level"] == "compliant"


def test_policy_health_report_script_marks_drift_and_missing_validation(tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True)

    _write_json(
        out_dir / "active-policy.json",
        {
            "artifact_version": "1.0",
            "policy_profile": "alpha",
            "policy": {"release_decision": {"warning_budget": 2}},
        },
    )
    lockfile = tmp_path / "active-policy.lock.json"
    _write_json(
        lockfile,
        {
            "artifact_version": "1.0",
            "policy_profile": "alpha",
            "policy": {"release_decision": {"warning_budget": 0}},
        },
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)
    result = subprocess.run(
        [str(SCRIPT), str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    payload = json.loads((out_dir / "policy-health-report.json").read_text(encoding="utf-8"))
    assert payload["lockfile_exists"] is True
    assert payload["lockfile_sync"] is False
    assert payload["config_valid"] is False
    assert payload["policy_compliance_level"] == "non_compliant"
    assert any("differs from lockfile" in note for note in payload["notes"])
