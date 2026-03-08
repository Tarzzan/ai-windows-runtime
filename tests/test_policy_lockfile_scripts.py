from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


EXPORT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export-active-policy.sh"
DRIFT_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-policy-drift.sh"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_export_active_policy_writes_in_requested_output_dir(tmp_path):
    out_dir = tmp_path / "custom-out"

    result = subprocess.run(
        [str(EXPORT_SCRIPT), str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (out_dir / "active-policy.json").exists()
    assert (out_dir / "validation" / "active-policy-validation.json").exists()


def test_export_active_policy_honors_profile_override(tmp_path):
    out_dir = tmp_path / "out"
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "default_profile": "alpha",
                "profiles": {
                    "alpha": {"release_decision": {"warning_budget": 2}},
                    "prod": {"release_decision": {"warning_budget": 0}},
                },
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_PATH"] = str(policy_path)
    env["COMPAT_POLICY_PROFILE"] = "prod"
    result = subprocess.run(
        [str(EXPORT_SCRIPT), str(out_dir)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    payload = json.loads((out_dir / "active-policy.json").read_text(encoding="utf-8"))
    assert payload["policy_profile"] == "prod"
    assert payload["policy"]["release_decision"]["warning_budget"] == 0


def test_policy_drift_script_passes_when_lockfile_matches(tmp_path):
    if shutil.which("jq") is None:
        return

    policy_payload = {
        "artifact_version": "1.0",
        "policy_profile": "alpha",
        "policy": {"release_decision": {"warning_budget": 2}},
    }
    _write_json(tmp_path / "active-policy.json", policy_payload)
    lockfile = tmp_path / "active-policy.lock.json"
    _write_json(lockfile, policy_payload)

    env = dict(os.environ)
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)
    result = subprocess.run(
        [str(DRIFT_SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "policy drift check: ok" in result.stdout


def test_policy_drift_script_fails_when_lockfile_differs(tmp_path):
    if shutil.which("jq") is None:
        return

    _write_json(
        tmp_path / "active-policy.json",
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
        [str(DRIFT_SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode != 0
    assert "active policy differs from lockfile" in result.stderr


def test_policy_drift_script_skips_when_lockfile_missing(tmp_path):
    if shutil.which("jq") is None:
        return

    _write_json(
        tmp_path / "active-policy.json",
        {
            "artifact_version": "1.0",
            "policy_profile": "alpha",
            "policy": {"release_decision": {"warning_budget": 2}},
        },
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_LOCKFILE"] = str(tmp_path / "does-not-exist.json")
    result = subprocess.run(
        [str(DRIFT_SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "no lockfile" in result.stdout


def test_policy_drift_script_fails_when_jq_is_missing(tmp_path):
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    (fake_bin / "dirname").symlink_to("/usr/bin/dirname")

    result = subprocess.run(
        ["/bin/bash", str(DRIFT_SCRIPT), str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": str(fake_bin)},
    )

    assert result.returncode == 2
    assert "missing dependency 'jq'" in result.stderr
