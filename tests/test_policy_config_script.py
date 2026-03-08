from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check-policy-config.sh"


def test_policy_config_script_passes_for_valid_config(tmp_path):
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
    result = subprocess.run(
        [str(SCRIPT), str(tmp_path / "out")],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "policy config check: ok" in result.stdout


def test_policy_config_script_fails_when_default_profile_is_missing(tmp_path):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "default_profile": "beta",
                "profiles": {
                    "alpha": {"release_decision": {"warning_budget": 2}},
                },
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_PATH"] = str(policy_path)
    result = subprocess.run(
        [str(SCRIPT), str(tmp_path / "out")],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode != 0
    assert "default_profile" in result.stderr


def test_policy_config_script_fails_schema_validation_for_invalid_type(tmp_path):
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "default_profile": "alpha",
                "profiles": {
                    "alpha": {"release_decision": {"warning_budget": "two"}},
                },
            }
        ),
        encoding="utf-8",
    )

    env = dict(os.environ)
    env["COMPAT_POLICY_PATH"] = str(policy_path)
    result = subprocess.run(
        [str(SCRIPT), str(tmp_path / "out")],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode != 0
    assert "warning_budget" in result.stdout or "warning_budget" in result.stderr
