from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "refresh-policy-lockfile.sh"


def test_refresh_policy_lockfile_script_generates_lockfile(tmp_path):
    lockfile = tmp_path / "active-policy.lock.json"
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
    env["COMPAT_POLICY_LOCKFILE"] = str(lockfile)
    result = subprocess.run(
        [str(SCRIPT)],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )

    assert result.returncode == 0
    assert "policy lockfile refresh: ok" in result.stdout
    payload = json.loads(lockfile.read_text(encoding="utf-8"))
    assert payload["policy_profile"] == "prod"
    assert payload["policy"]["release_decision"]["warning_budget"] == 0
