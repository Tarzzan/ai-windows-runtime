from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "show-active-policy.sh"


def test_show_active_policy_script_uses_default_profile():
    env = dict(os.environ)
    env.pop("COMPAT_POLICY_PATH", None)
    env.pop("COMPAT_POLICY_PROFILE", None)

    result = subprocess.run(
        [str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["policy_profile"] == "alpha"
    assert payload["policy"]["release_decision"]["warning_budget"] == 2


def test_show_active_policy_script_honors_profile_override(tmp_path):
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
        [str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["policy_profile"] == "prod"
    assert payload["policy"]["release_decision"]["warning_budget"] == 0
