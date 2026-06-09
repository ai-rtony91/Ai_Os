from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RECOMMENDATION_SCRIPT = REPO_ROOT / "automation" / "operator" / "Get-AiOsCommandApprovalRecommendation.DRY_RUN.ps1"
APPROVAL_TIER_POLICY = (
    REPO_ROOT / "automation" / "orchestration" / "policy" / "AIOS_APPROVAL_TIER_POLICY.json"
)

REQUIRED_FIELDS = [
    "approval_recommendation_defaults",
]

REQUIRED_DEFAULT_FIELDS = [
    "DEFAULT_PROCEED_OPTION",
    "DEFAULT_PROCEED_MEANING",
    "ASK_USER_ONLY_ON_PROTECTED_GATE",
    "DEFAULT_FOR_TIERS",
]


def _run_recommendation(command: str, lane: str, scope: str) -> tuple[int, str]:
    """Run the recommendation script for a command and extract the returned option."""
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RECOMMENDATION_SCRIPT),
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
    if result.returncode != 0:
        return (result.returncode, "")

    match = None
    for line in result.stdout.splitlines():
        match = re.search(r"^Recommended option:\s*(.+)$", line.strip())
        if match:
            break

    if not match:
        return (2, "")
    return (0, match.group(1).strip())


def validate(repo_root: Path) -> tuple[dict[str, object], list[str]]:
    failures: list[str] = []
    check_results: dict[str, bool] = {}

    policy = json.loads(APPROVAL_TIER_POLICY.read_text(encoding="utf-8"))
    defaults = policy.get("approval_recommendation_defaults", {})

    check_results["policy_required_fields_present"] = all(
        field in policy for field in REQUIRED_FIELDS
    )
    check_results["policy_defaults_required_fields_present"] = all(
        field in defaults for field in REQUIRED_DEFAULT_FIELDS
    )
    if not check_results["policy_required_fields_present"]:
        failures.append(f"Missing required fields in {APPROVAL_TIER_POLICY.relative_to(REPO_ROOT)}")
    if not check_results["policy_defaults_required_fields_present"]:
        failures.append(
            f"Missing required default recommendation fields in {APPROVAL_TIER_POLICY.relative_to(REPO_ROOT)}"
        )

    check_results["default_proceed_option_is_2"] = defaults.get("DEFAULT_PROCEED_OPTION") == 2
    check_results["default_proceed_meaning_is_expected"] = (
        defaults.get("DEFAULT_PROCEED_MEANING")
        == "continue next safe governed DRY_RUN/non-destructive step"
    )
    check_results["ask_user_only_on_protected_gate"] = bool(
        defaults.get("ASK_USER_ONLY_ON_PROTECTED_GATE")
    )
    check_results["default_for_tiers_includes_tier0_and_tier1"] = set(
        defaults.get("DEFAULT_FOR_TIERS", [])
    ) >= {"TIER_0_AUTO", "TIER_1_LOW_RISK"}

    if not check_results["default_proceed_option_is_2"]:
        failures.append("DEFAULT_PROCEED_OPTION must be 2")
    if not check_results["default_proceed_meaning_is_expected"]:
        failures.append("DEFAULT_PROCEED_MEANING must match the repo policy requirement")
    if not check_results["ask_user_only_on_protected_gate"]:
        failures.append("ASK_USER_ONLY_ON_PROTECTED_GATE must be true")
    if not check_results["default_for_tiers_includes_tier0_and_tier1"]:
        failures.append("DEFAULT_FOR_TIERS must include TIER_0_AUTO and TIER_1_LOW_RISK")

    safe_return_code, safe_option = _run_recommendation("git status --short --branch", "READ_ONLY", "repo")
    check_results["safe_readonly_default_option_2"] = safe_return_code == 0 and safe_option == "Option 2"
    if not check_results["safe_readonly_default_option_2"]:
        failures.append("Safe read-only commands must recommend Option 2")

    safe_tier1_return_code, safe_tier1_option = _run_recommendation(
        "git switch -c feature/default-tier-proceed", "BRANCH", "repo"
    )
    check_results["safe_tier1_default_option_2"] = safe_tier1_return_code == 0 and safe_tier1_option == "Option 2"
    if not check_results["safe_tier1_default_option_2"]:
        failures.append("Safe TIER_1_LOW_RISK commands must recommend Option 2")

    commit_return_code, commit_option = _run_recommendation('git commit -m "docs: test"', "COMMIT_ONLY", "AGENTS.md")
    merge_return_code, merge_option = _run_recommendation("gh pr merge 204 --merge --delete-branch=false", "MERGE_ONLY", "PR 204")
    push_return_code, push_option = _run_recommendation("git push -u origin feature/default-proceed-policy-v1", "PUSH_ONLY", "repo")
    check_results["commit_requires_approval_option_1"] = (
        commit_return_code == 0 and commit_option == "Option 1"
    )
    check_results["merge_requires_approval_option_1"] = (
        merge_return_code == 0 and merge_option == "Option 1"
    )
    check_results["push_requires_approval_option_1"] = (
        push_return_code == 0 and push_option == "Option 1"
    )
    if not check_results["commit_requires_approval_option_1"]:
        failures.append("Commit command should remain one-time approval (Option 1)")
    if not check_results["merge_requires_approval_option_1"]:
        failures.append("Merge command should remain one-time approval (Option 1)")
    if not check_results["push_requires_approval_option_1"]:
        failures.append("Push command should remain one-time approval (Option 1)")

    protected_return_code, protected_option = _run_recommendation(
        "python automation/forex_engine/run_live_broker_demo.py --mode=live",
        "READ_ONLY",
        "repo",
    )
    check_results["live_trading_blocked_with_hard_stop"] = (
        protected_return_code == 0 and protected_option == "Option 3 / HARD STOP"
    )
    if not check_results["live_trading_blocked_with_hard_stop"]:
        failures.append("Live trading/broker/webhook-like commands must hard-stop")

    secret_return_code, secret_option = _run_recommendation("echo .env", "READ_ONLY", "repo")
    check_results["secret_or_env_behavior_not_weakened"] = (
        secret_return_code == 0 and secret_option == "Option 3 / HARD STOP"
    )
    if not check_results["secret_or_env_behavior_not_weakened"]:
        failures.append("Secret/.env-like commands must remain hard-stop")

    status = "PASS" if not failures else "FAIL"
    return (
        {"status": status, "validator": "aios_default_proceed_policy_validator", "checks": check_results},
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate default proceed policy and recommendation behavior.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload, failures = validate(Path(args.repo_root).resolve())

    if not args.sample_check:
        payload = {"status": "BLOCKED", "reason": "--sample-check required"}
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print(payload["status"])
        return 2

    if args.json:
        payload["status"] = "PASS" if not failures else "FAIL"
        payload["failed_checks"] = failures
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"validator: {payload['validator']}")
        print(f"status: {'PASS' if not failures else 'FAIL'}")
        for check_name, check_value in payload["checks"].items():
            print(f"{check_name}: {check_value}")
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
