from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_safe_pr_autoland_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_safe_pr_autoland_policy", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pr_evidence(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pr_number": 241,
        "pr_state": "OPEN",
        "draft": False,
        "mergeable": True,
        "checks_status": "success",
        "changed_files": [
            "automation/orchestration/aios_safe_pr_autoland_policy.py",
            "tests/orchestration/test_aios_safe_pr_autoland_policy.py",
            "docs/orchestration/AIOS_SAFE_PR_AUTOLAND_POLICY.md",
        ],
        "additions": 260,
        "deletions": 0,
        "base_branch": "main",
        "head_branch": "lane/safe-pr-autoland-policy",
        "head_sha": "abc123",
        "expected_head_sha": "abc123",
        "safety_summary": "safe preview-only no high-risk flags",
        "validation_summary": "pytest passed",
    }
    payload.update(overrides)
    return payload


def assert_preview_only(policy: dict[str, object]) -> None:
    assert policy["commands_executed"] == []
    assert policy["merges_performed"] is False
    assert policy["pushes_performed"] is False
    assert policy["branches_deleted"] is False
    assert policy["resets_performed"] is False

    safety = policy["safety"]
    assert isinstance(safety, dict)
    assert safety["preview_only"] is True
    assert safety["evidence_only"] is True
    assert safety["command_execution"] is False
    assert safety["gh_execution"] is False
    assert safety["git_execution"] is False
    assert safety["network_access"] is False
    assert safety["approval_mutation"] is False
    assert safety["queue_mutation"] is False
    assert safety["scheduler_activation"] is False
    assert safety["daemon_activation"] is False
    assert safety["worker_dispatch"] is False
    assert safety["merge"] is False
    assert safety["push"] is False
    assert safety["branch_deletion"] is False
    assert safety["reset"] is False


def test_fully_green_safe_pr_returns_eligible_and_safe_to_autoland_true() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence())

    assert policy["schema"] == "AIOS_SAFE_PR_AUTOLAND_POLICY.v1"
    assert policy["autoland_status"] == "eligible"
    assert policy["safe_to_autoland"] is True
    assert policy["branch_delete_allowed"] is True
    assert policy["local_sync_allowed"] is True
    assert policy["merge_method"] == "squash"
    assert policy["human_wake_required"] is False
    assert policy["blocked_reasons"] == []
    assert set(policy["passed_conditions"]) == set(policy["required_conditions"])
    assert_preview_only(policy)


def test_pending_checks_are_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(checks_status="pending"))

    assert policy["autoland_status"] == "blocked"
    assert policy["safe_to_autoland"] is False
    assert "checks_not_success:pending" in policy["blocked_reasons"]
    assert_preview_only(policy)


def test_failing_checks_are_rejected() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(checks_status="failed"))

    assert policy["autoland_status"] == "rejected"
    assert policy["safe_to_autoland"] is False
    assert "checks_failed" in policy["blocked_reasons"]
    assert policy["human_wake_required"] is True
    assert_preview_only(policy)


def test_draft_pr_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(draft=True))

    assert policy["autoland_status"] == "blocked"
    assert "draft_pr" in policy["blocked_reasons"]
    assert_preview_only(policy)


def test_non_mergeable_pr_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(mergeable=False))

    assert policy["autoland_status"] == "blocked"
    assert "pr_not_mergeable:blocked" in policy["blocked_reasons"]
    assert_preview_only(policy)


def test_base_branch_not_main_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(base_branch="develop"))

    assert policy["autoland_status"] == "blocked"
    assert "base_branch_not_main:develop" in policy["blocked_reasons"]
    assert_preview_only(policy)


def test_head_branch_main_is_rejected() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(head_branch="main"))

    assert policy["autoland_status"] == "rejected"
    assert "head_branch_not_safe:main" in policy["blocked_reasons"]
    assert_preview_only(policy)


def test_expected_head_sha_mismatch_is_rejected() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(head_sha="abc123", expected_head_sha="def456")
    )

    assert policy["autoland_status"] == "rejected"
    assert "expected_head_sha_mismatch" in policy["blocked_reasons"]
    assert_preview_only(policy)


def test_protected_file_path_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(changed_files=["docs/governance/operational-doctrine.md"])
    )

    assert policy["autoland_status"] == "blocked"
    assert any(str(reason).startswith("protected_file_path:") for reason in policy["blocked_reasons"])
    assert_preview_only(policy)


def test_secret_path_is_rejected() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(changed_files=["automation/secrets/prod_token.json"])
    )

    assert policy["autoland_status"] == "rejected"
    assert any(
        str(reason).startswith("credential_or_secret_path:")
        for reason in policy["blocked_reasons"]
    )
    assert_preview_only(policy)


def test_broker_live_trading_path_is_rejected() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(changed_files=["automation/trading_lab/broker/live_order_router.py"])
    )

    assert policy["autoland_status"] == "rejected"
    assert any(
        str(reason).startswith("broker_live_trading_order_or_webhook_path:")
        for reason in policy["blocked_reasons"]
    )
    assert_preview_only(policy)


def test_approval_mutation_path_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(changed_files=["automation/orchestration/approval_inbox/card.json"])
    )

    assert policy["autoland_status"] == "blocked"
    assert any(str(reason).startswith("approval_mutation_path:") for reason in policy["blocked_reasons"])
    assert_preview_only(policy)


def test_queue_mutation_path_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(changed_files=["automation/orchestration/work_packets/active/pkt.json"])
    )

    assert policy["autoland_status"] == "blocked"
    assert any(str(reason).startswith("queue_mutation_path:") for reason in policy["blocked_reasons"])
    assert_preview_only(policy)


def test_scheduler_daemon_path_is_blocked() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(
        pr_evidence(changed_files=["automation/orchestration/scheduler/start_daemon.ps1"])
    )

    assert policy["autoland_status"] == "blocked"
    assert any(
        str(reason).startswith("scheduler_or_daemon_activation_path:")
        for reason in policy["blocked_reasons"]
    )
    assert_preview_only(policy)


def test_proposed_commands_are_exact_preview_landing_plan_only() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence())

    assert policy["proposed_commands"] == [
        "gh pr checks 241",
        "gh pr merge 241 --squash --delete-branch",
        "git fetch origin",
        "git reset --hard origin/main",
        "git status --short --branch",
    ]
    assert_preview_only(policy)


def test_blocked_policy_does_not_propose_landing_commands() -> None:
    module = load_module()

    policy = module.build_safe_pr_autoland_policy(pr_evidence(checks_status="pending"))

    assert policy["proposed_commands"] == []
    assert policy["branch_delete_allowed"] is False
    assert policy["local_sync_allowed"] is False
    assert_preview_only(policy)


def test_source_does_not_import_execution_network_or_file_write_tools() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "subprocess",
        "popen",
        "requests",
        "socket",
        "urllib",
        "http.client",
        "open(",
        "write_text",
        "write_bytes",
        "with open",
        "os.",
        "pathlib",
        "system(",
        "run(",
    ]:
        assert forbidden not in source
