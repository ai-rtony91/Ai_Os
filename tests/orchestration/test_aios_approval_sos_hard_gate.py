from __future__ import annotations

import json

from automation.orchestration.operator_control.aios_approval_sos_hard_gate import (
    PROTECTED_ACTIONS,
    SCHEMA,
    build_approval_sos_hard_gate_result,
)


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "main",
            "expected_branch": "main",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_approval_sos_hard_gate_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
    }
    payload.update(overrides)
    return payload


def test_python_logic_emits_hard_gate_schema() -> None:
    result = build_approval_sos_hard_gate_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["safety"]["status"] == "PASS"


def test_hard_gate_blocks_every_required_protected_action() -> None:
    result = build_approval_sos_hard_gate_result(_payload())
    blocked_ids = {item["action_id"] for item in result["blocked_actions"]}

    assert blocked_ids == {action_id for action_id, _label in PROTECTED_ACTIONS}
    assert result["safety"]["protected_actions_blocked"] is True
    assert result["approval_state"]["explicit_human_owner_approval_present"] is False


def test_hard_gate_requires_human_owner_for_apply_commit_push_pr_merge() -> None:
    result = build_approval_sos_hard_gate_result(_payload())
    required = set(result["human_owner_required_for"])

    for action_id in ("apply", "commit", "push", "pr", "merge"):
        assert action_id in required


def test_hard_gate_blocks_runtime_worker_scheduler_daemon_and_mutations() -> None:
    result = build_approval_sos_hard_gate_result(_payload())
    required = set(result["human_owner_required_for"])

    for action_id in (
        "runtime_start",
        "worker_launch",
        "scheduler_enablement",
        "daemon_launch",
        "queue_mutation",
        "lock_mutation",
        "approval_mutation",
        "registry_mutation",
    ):
        assert action_id in required


def test_hard_gate_blocks_writes_secrets_and_live_trading_paths() -> None:
    result = build_approval_sos_hard_gate_result(_payload())
    required = set(result["human_owner_required_for"])

    for action_id in (
        "packet_draft_write",
        "proposed_packet_write",
        "reports_write",
        "telemetry_write",
        "relay_write",
        "broker_oanda_webhook_order_live_trading",
        "secrets_env_access",
    ):
        assert action_id in required
    assert result["safety"]["secrets_or_env_access"] is False
    assert result["safety"]["broker_or_live_trading"] is False


def test_read_only_inspection_is_allowed_without_granting_execution() -> None:
    result = build_approval_sos_hard_gate_result(_payload())

    assert "repo_status_inspection" in result["allowed_read_only_actions"]
    assert result["safety"]["read_only_inspection_allowed"] is True
    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["launches_workers"] is False


def test_branch_mismatch_blocks() -> None:
    result = build_approval_sos_hard_gate_result(
        _payload(
            repo_state={
                "branch": "feature/x",
                "expected_branch": "main",
                "branch_matches_expected": False,
                "dirty": False,
                "fail_on_dirty_worktree": True,
            }
        )
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "BRANCH_MISMATCH" in result["stop_conditions"]


def test_dirty_worktree_outside_exact_scope_blocks() -> None:
    result = build_approval_sos_hard_gate_result(
        _payload(
            repo_state={
                "branch": "main",
                "expected_branch": "main",
                "branch_matches_expected": True,
                "dirty": True,
                "dirty_allowed_for_approval_sos_hard_gate_validation": False,
                "fail_on_dirty_worktree": True,
            }
        )
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]


def test_no_write_proof_blocks_forbidden_delta() -> None:
    result = build_approval_sos_hard_gate_result(
        _payload(
            no_write_proof={
                "changed": True,
                "git_state_changed": False,
                "forbidden_surface_changed": True,
            }
        )
    )

    assert result["safety"]["status"] == "BLOCKED_BY_WRITE_SURFACE_RISK"
    assert "WRITE_SURFACE_RISK" in result["stop_conditions"]


def test_result_never_emits_packet_body_or_protected_command_text() -> None:
    result = build_approval_sos_hard_gate_result(_payload())
    encoded = json.dumps(result).lower()

    assert "codex-only prompt" not in encoded
    assert "ai_os execution token" not in encoded
    for phrase in ("git add", "git commit", "git push", "gh pr", "start-aios"):
        assert phrase not in encoded
