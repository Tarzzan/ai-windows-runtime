from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-policy-lockfile-sync.sh"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_policy_lockfile_sync_script_passes_when_policy_matches(tmp_path):
    if shutil.which("jq") is None:
        return

    lockfile = tmp_path / "active-policy.lock.json"

    policy_file = tmp_path / "policy.json"
    policy_file.write_text(
        json.dumps(
            {
                "default_profile": "alpha",
                "profiles": {"alpha": {"release_decision": {"warning_budget": 2}}},
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_PATH"] = str(policy_file)
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)

    refresh_script = Path(__file__).resolve().parents[1] / "scripts" / "refresh-policy-lockfile.sh"
    refresh = subprocess.run(
        [str(refresh_script)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert refresh.returncode == 0

    result = subprocess.run(
        [str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "policy lockfile sync: ok" in result.stdout


def test_policy_lockfile_sync_script_fails_when_policy_differs(tmp_path):
    if shutil.which("jq") is None:
        return

    lockfile = tmp_path / "active-policy.lock.json"
    _write_json(
        lockfile,
        {
            "artifact_version": "1.0",
            "policy_profile": "alpha",
            "policy": {"release_decision": {"warning_budget": 2}},
        },
    )

    policy_file = tmp_path / "policy.json"
    policy_file.write_text(
        json.dumps(
            {
                "default_profile": "alpha",
                "profiles": {"alpha": {"release_decision": {"warning_budget": 0}}},
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_PATH"] = str(policy_file)
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)

    result = subprocess.run(
        [str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode != 0
    assert "drift detected" in result.stderr
    assert "refresh-policy-lockfile.sh" in result.stderr


def test_policy_lockfile_sync_script_fix_mode_refreshes_lockfile(tmp_path):
    if shutil.which("jq") is None:
        return

    lockfile = tmp_path / "active-policy.lock.json"
    _write_json(
        lockfile,
        {
            "artifact_version": "1.0",
            "policy_profile": "alpha",
            "policy": {"release_decision": {"warning_budget": 2}},
        },
    )

    policy_file = tmp_path / "policy.json"
    policy_file.write_text(
        json.dumps(
            {
                "default_profile": "alpha",
                "profiles": {"alpha": {"release_decision": {"warning_budget": 0}}},
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_PATH"] = str(policy_file)
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)

    result = subprocess.run(
        [str(SCRIPT), "--fix"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "policy lockfile sync: fixed" in result.stdout

    payload = json.loads(lockfile.read_text(encoding="utf-8"))
    assert payload["policy"]["release_decision"]["warning_budget"] == 0
