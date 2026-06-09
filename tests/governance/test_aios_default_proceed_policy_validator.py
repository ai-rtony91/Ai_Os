from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "automation" / "validators" / "aios_default_proceed_policy_validator.py"
POLICY = REPO_ROOT / "automation" / "orchestration" / "policy" / "AIOS_DEFAULT_PROCEED_POLICY.json"


def test_default_proceed_policy_file_has_required_settings() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))

    assert policy["DEFAULT_PROCEED_OPTION"] == 2
    assert (
        policy["DEFAULT_PROCEED_MEANING"]
        == "continue next safe governed DRY_RUN/non-destructive step"
    )
    assert policy["ASK_USER_ONLY_ON_PROTECTED_GATE"] is True


def test_default_proceed_policy_validator_passes_for_sample_checks() -> None:
    result = subprocess.run(
        [
            "python",
            str(VALIDATOR),
            "--sample-check",
            "--repo-root",
            str(REPO_ROOT),
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "PASS"
    assert payload["checks"]["policy_required_fields_present"] is True
    assert payload["checks"]["default_proceed_option_is_2"] is True
    assert payload["checks"]["safe_readonly_default_option_2"] is True
    assert payload["checks"]["commit_requires_approval_option_1"] is True
    assert payload["checks"]["merge_requires_approval_option_1"] is True
    assert payload["checks"]["push_requires_approval_option_1"] is True
    assert payload["checks"]["live_trading_blocked_with_hard_stop"] is True
    assert payload["checks"]["secret_or_env_behavior_not_weakened"] is True
