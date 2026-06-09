from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "automation" / "validators" / "aios_default_proceed_policy_validator.py"
POLICY = REPO_ROOT / "automation" / "orchestration" / "policy" / "AIOS_APPROVAL_TIER_POLICY.json"


def test_default_proceed_policy_file_has_required_settings() -> None:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    defaults = policy["approval_recommendation_defaults"]

    assert defaults["DEFAULT_PROCEED_OPTION"] == 2
    assert (
        defaults["DEFAULT_PROCEED_MEANING"]
        == "continue next safe governed DRY_RUN/non-destructive step"
    )
    assert defaults["ASK_USER_ONLY_ON_PROTECTED_GATE"] is True
    assert "TIER_0_AUTO" in defaults["DEFAULT_FOR_TIERS"]
    assert "TIER_1_LOW_RISK" in defaults["DEFAULT_FOR_TIERS"]


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
    assert payload["checks"]["policy_defaults_required_fields_present"] is True
    assert payload["checks"]["default_proceed_option_is_2"] is True
    assert payload["checks"]["default_for_tiers_includes_tier0_and_tier1"] is True
    assert payload["checks"]["safe_readonly_default_option_2"] is True
    assert payload["checks"]["safe_tier1_default_option_2"] is True
    assert payload["checks"]["commit_requires_approval_option_1"] is True
    assert payload["checks"]["merge_requires_approval_option_1"] is True
    assert payload["checks"]["push_requires_approval_option_1"] is True
    assert payload["checks"]["live_trading_blocked_with_hard_stop"] is True
    assert payload["checks"]["secret_or_env_behavior_not_weakened"] is True


def _recommended_option(command: str, lane: str, scope: str) -> str:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(REPO_ROOT / "automation\\operator\\Get-AiOsCommandApprovalRecommendation.DRY_RUN.ps1"),
            "-CommandText",
            command,
            "-LaneType",
            lane,
            "-ScopeHint",
            scope,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    marker = "Recommended option:"
    for line in result.stdout.splitlines():
        if line.strip().startswith(marker):
            return line.split(":", 1)[1].strip()

    raise AssertionError(f"No recommendation option found for command: {command!r}")


def test_tier0_and_tier1_safe_commands_keep_option_2_default() -> None:
    assert _recommended_option("git status --short --branch", "READ_ONLY", "repo") == "Option 2"
    assert _recommended_option("git switch -c feature/default-tier-proceed", "BRANCH", "repo") == "Option 2"


def test_tier2_and_protected_actions_do_not_use_option_2_default() -> None:
    assert _recommended_option("git reset --hard HEAD", "READ_ONLY", "repo") == "Option 3 / HARD STOP"
    assert (
        _recommended_option("git branch -D feature/temp-safe-default", "BRANCH", "repo")
        == "Option 3 / HARD STOP"
    )
    assert (
        _recommended_option(
            "gh pr merge 204 --merge --delete-branch=false", "MERGE_ONLY", "PR 204"
        )
        == "Option 1"
    )
    assert (
        _recommended_option(
            'git commit -m "docs: test safe default proceed policy"', "COMMIT_ONLY", "AGENTS.md"
        )
        == "Option 1"
    )
    assert (
        _recommended_option(
            "git push -u origin feature/default-proceed-policy-v1", "PUSH_ONLY", "repo"
        )
        == "Option 1"
    )
    assert (
        _recommended_option(
            "python automation/forex_engine/run_live_broker_demo.py --mode=live",
            "READ_ONLY",
            "repo",
        )
        == "Option 3 / HARD STOP"
    )
    assert (
        _recommended_option("pwsh -File temp-do-not-run.APPLY.ps1", "READ_ONLY", "repo")
        == "Option 3 / HARD STOP"
    )
