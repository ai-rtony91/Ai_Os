from __future__ import annotations

import json

from automation.orchestration.self_development.aios_full_autonomy_activation_gate import (
    ACTIVATION_STATUSES,
    SCHEMA,
    build_full_autonomy_activation_gate_result,
)


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
            "expected_branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_full_autonomy_activation_gate_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "requested_autonomy_level": "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
        "operating_profile": "12H_SUPERVISED",
        "human_owner_approval_evidence": "",
        "identity_spine_status": "PASS",
        "validator_chain_status": "PASS",
        "approval_sos_status": "CLEAR",
        "governed_soak_status": "PASS",
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
    }
    payload.update(overrides)
    return payload


def _result(**overrides: object) -> dict:
    return build_full_autonomy_activation_gate_result(_payload(**overrides))


def test_python_logic_emits_activation_gate_schema() -> None:
    result = _result()

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["activation_decision"]["status"] in ACTIVATION_STATUSES


def test_missing_human_owner_approval_blocks_level_5() -> None:
    result = _result(requested_autonomy_level="LEVEL_5_FULL_AUTONOMY_REQUESTED")

    assert result["activation_decision"]["status"] == "FULL_AUTONOMY_REQUESTED_NOT_APPROVED"
    assert result["activation_decision"]["true_full_autonomy_approved"] is False
    assert "human_owner_approval_evidence" in result["missing_requirements"]
    assert result["safety"]["status"] == "REVIEW_REQUIRED"


def test_identity_spine_missing_creates_review_required() -> None:
    result = _result(identity_spine_status="UNKNOWN")

    assert result["activation_decision"]["status"] == "REVIEW_REQUIRED"
    assert "identity_spine" in result["missing_requirements"]
    assert "Test-AiOsIdentitySpine.DRY_RUN.ps1" in result["next_safe_action"]


def test_validator_chain_missing_creates_review_required() -> None:
    result = _result(validator_chain_status="UNKNOWN")

    assert result["activation_decision"]["status"] == "REVIEW_REQUIRED"
    assert "validator_chain" in result["missing_requirements"]
    assert "Invoke-OrchestrationValidatorChain.DRY_RUN.ps1" in result["next_safe_action"]


def test_validator_chain_warn_reviewed_is_allowed_as_reviewed_evidence() -> None:
    result = _result(validator_chain_status="WARN_REVIEWED")

    assert result["activation_decision"]["status"] == "PACKET_PREVIEW_ALLOWED"
    assert result["safety"]["status"] == "PASS"


def test_sos_active_denies_activation() -> None:
    result = _result(approval_sos_status="SOS_ACTIVE")

    assert result["activation_decision"]["status"] == "DENIED"
    assert result["safety"]["status"] == "BLOCKED"
    assert "SOS_ACTIVE" in result["stop_conditions"]
    assert "Wake the Human Owner" in result["next_safe_action"]


def test_governed_soak_missing_creates_review_required() -> None:
    result = _result(governed_soak_status="UNKNOWN")

    assert result["activation_decision"]["status"] == "REVIEW_REQUIRED"
    assert "governed_self_development_soak" in result["missing_requirements"]
    assert "Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1" in result["next_safe_action"]


def test_pass_evidence_without_approval_allows_only_safe_posture() -> None:
    result = _result()

    assert result["activation_decision"]["status"] == "PACKET_PREVIEW_ALLOWED"
    assert result["activation_decision"]["protected_execution_allowed"] is False
    assert result["activation_decision"]["worker_launch_allowed"] is False
    assert "SUPERVISED_12H_ALLOWED" in result["blocked_postures"]


def test_explicit_approval_can_raise_ceiling_but_not_launch_workers() -> None:
    result = _result(human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")

    assert result["activation_decision"]["status"] == "SUPERVISED_12H_ALLOWED"
    assert result["approval_required"]["explicit_human_owner_approval_evidence_present"] is True
    assert result["activation_decision"]["worker_launch_allowed"] is False
    assert result["safety"]["launches_workers"] is False


def test_protected_actions_remain_blocked() -> None:
    result = _result(human_owner_approval_evidence="APPROVED_FOR_SUPERVISED_REVIEW")
    blocked = {item["action_id"] for item in result["protected_actions"]}

    for action_id in ("apply", "commit", "push", "worker_launch", "scheduler_enablement", "daemon_launch"):
        assert action_id in blocked
    assert result["safety"]["protected_actions_blocked"] is True
    assert result["safety"]["human_owner_required_before_protected_action"] is True


def test_no_queue_lock_approval_or_registry_mutation() -> None:
    result = _result()

    assert result["safety"]["mutates_queue"] is False
    assert result["safety"]["mutates_locks"] is False
    assert result["safety"]["mutates_approval"] is False
    assert result["safety"]["mutates_approvals"] is False
    assert result["safety"]["mutates_registry"] is False


def test_no_runtime_worker_scheduler_or_daemon_launch() -> None:
    result = _result()

    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["launches_workers"] is False
    assert result["safety"]["enables_scheduler"] is False
    assert result["safety"]["starts_daemon"] is False


def test_no_secrets_broker_or_live_trading() -> None:
    result = _result()

    assert result["safety"]["touches_secrets_or_env"] is False
    assert result["safety"]["secrets_or_env_access"] is False
    assert result["safety"]["broker_or_live_trading"] is False


def test_dirty_worktree_outside_approved_files_blocks_logic() -> None:
    result = _result(
        repo_state={
            "branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
            "expected_branch": "feature/full-autonomy-activation-gate-worker-posture-v1",
            "branch_matches_expected": True,
            "dirty": True,
            "dirty_allowed_for_full_autonomy_activation_gate_validation": False,
            "fail_on_dirty_worktree": True,
        }
    )

    assert result["activation_decision"]["status"] == "DENIED"
    assert result["safety"]["status"] == "BLOCKED"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]


def test_no_write_proof_blocks_forbidden_delta() -> None:
    result = _result(
        no_write_proof={
            "changed": True,
            "git_state_changed": False,
            "forbidden_surface_changed": True,
        }
    )

    assert result["activation_decision"]["status"] == "DENIED"
    assert result["safety"]["status"] == "BLOCKED_BY_WRITE_SURFACE_RISK"
    assert "WRITE_SURFACE_RISK" in result["stop_conditions"]


def test_profile_specific_safe_postures_without_approval() -> None:
    assert _result(operating_profile="24H_SUPERVISED")["activation_decision"]["status"] == "READ_ONLY_MONITOR"
    assert _result(operating_profile="WEEKEND")["activation_decision"]["status"] == "READ_ONLY_MONITOR"
    assert _result(operating_profile="VACATION")["activation_decision"]["status"] == "VALIDATOR_ONLY_ALLOWED"
    assert _result(operating_profile="FULL_AUTONOMY_SUPERVISED")["activation_decision"]["status"] == "PACKET_PREVIEW_ALLOWED"


def test_result_does_not_emit_protected_action_command_text() -> None:
    result = _result()
    encoded = json.dumps(result).lower()

    for phrase in ("git add", "git commit", "git push", "gh pr", "git merge", "start-aios", "open-aiosworker"):
        assert phrase not in encoded
