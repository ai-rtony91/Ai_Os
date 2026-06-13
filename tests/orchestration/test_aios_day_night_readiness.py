from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from automation.orchestration.supervisor.aios_day_night_readiness import (
    NEXT_SAFE_PACKET,
    SCHEMA,
    build_readiness_result,
    sanitize_command_field,
)


def _validator_router(**overrides: object) -> dict:
    payload = {
        "schema": "AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1",
        "safety": {
            "status": "PASS",
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_relay": False,
            "starts_runtime": False,
            "launches_workers": False,
            "protected_action_recommended": False,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
        },
        "validator_catalog": [],
        "evidence_sources": [],
        "excluded_surfaces": [],
        "stop_conditions": [],
    }
    payload.update(overrides)
    return payload


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "feature/governed-self-development-closure-v1",
            "expected_branch": "feature/governed-self-development-closure-v1",
            "branch_matches_expected": True,
            "dirty": False,
            "dirty_allowed_for_day_night_readiness_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "self_audit_result": {"schema": "AIOS_SELF_AUDIT_LOOP_RESULT.v1", "safety": {"status": "PASS"}},
        "packet_router_result": {"schema": "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1", "safety": {"status": "PASS"}},
        "validator_evidence_router_result": _validator_router(),
        "campaign_no_ready": {
            "schema": "AIOS_CAMPAIGN_NO_READY_STAGE_DISCOVERY.v1",
            "overall_readiness": "NO_READY_STAGE",
            "no_ready_stage_classification": "COMPLETE_IDLE",
        },
        "campaign_next_task": {
            "schema": "AIOS_CAMPAIGN_NEXT_TASK_RECOMMENDATION.v1",
            "overall_readiness": "NO_READY_STAGE",
            "next_packet_candidate": None,
        },
        "action_recommendation": {
            "recommended_command": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1 -OutputJson",
            "approval_matches": 0,
        },
        "approval_inbox_summary": {
            "pending_count": 0,
            "blocked_count": 0,
        },
        "runtime_worker_state": {
            "runtime_risk_detected": False,
            "worker_launch_detected": False,
            "scheduler_or_daemon_detected": False,
        },
        "backup_interference_state": {
            "interference_detected": False,
            "repo_local_backup_lock_present": False,
            "backup_in_progress": False,
            "snapshot_restore_candidate_present": False,
        },
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
    }
    payload.update(overrides)
    return payload


def test_python_logic_emits_day_night_readiness_schema() -> None:
    result = build_readiness_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["readiness"]["classification"] == "SUPERVISED_RECOMMENDATION_ALLOWED"


def test_off_mode_blocks_recommendation_and_execution() -> None:
    result = build_readiness_result(_payload(requested_operator_mode="OFF"))

    assert result["readiness"]["classification"] == "OFF"
    assert result["readiness"]["recommendation_allowed"] is False
    assert result["readiness"]["execution_allowed"] is False
    assert result["recommended_next_packet"] is None


def test_observe_mode_allows_read_only_inspection_only() -> None:
    result = build_readiness_result(_payload(requested_operator_mode="OBSERVE"))

    assert result["readiness"]["classification"] == "OBSERVE_ALLOWED"
    assert "OBSERVE_READ_ONLY" in result["allowed_operator_modes"]
    assert "SUPERVISED_RECOMMENDATION" in result["blocked_operator_modes"]
    assert result["recommended_next_packet"] is None


def test_supervised_recommendation_allowed_requires_clean_safety_state() -> None:
    result = build_readiness_result(_payload())

    assert result["readiness"]["classification"] == "SUPERVISED_RECOMMENDATION_ALLOWED"
    assert result["readiness"]["recommendation_allowed"] is True
    assert result["recommended_next_packet"] == NEXT_SAFE_PACKET
    assert result["safety"]["starts_runtime"] is False
    assert result["safety"]["launches_workers"] is False


def test_dirty_repo_outside_allowed_files_returns_blocked_by_dirty_repo() -> None:
    result = build_readiness_result(
        _payload(
            repo_state={
                "dirty": True,
                "fail_on_dirty_worktree": True,
                "dirty_allowed_for_day_night_readiness_validation": False,
            }
        )
    )

    assert result["readiness"]["classification"] == "BLOCKED_BY_DIRTY_REPO"
    assert "DIRTY_WORKTREE" in result["stop_conditions"]


def test_unsafe_validator_evidence_state_returns_blocked_by_validator_risk() -> None:
    result = build_readiness_result(
        _payload(
            validator_evidence_router_result=_validator_router(
                safety={"status": "BLOCKED", "protected_action_recommended": False},
                stop_conditions=["VALIDATOR_STOP"],
            )
        )
    )

    assert result["readiness"]["classification"] == "BLOCKED_BY_VALIDATOR_RISK"
    assert "VALIDATOR_EVIDENCE_ROUTER_NOT_PASS" in result["stop_conditions"]


def test_runtime_worker_scheduler_daemon_surfaces_return_blocked_by_runtime_risk() -> None:
    result = build_readiness_result(
        _payload(
            runtime_worker_state={
                "runtime_risk_detected": True,
                "worker_launch_detected": True,
                "scheduler_or_daemon_detected": True,
            }
        )
    )

    assert result["readiness"]["classification"] == "BLOCKED_BY_RUNTIME_RISK"


def test_approval_and_sos_states_return_blocked_or_hard_stop() -> None:
    approval = build_readiness_result(_payload(approval_inbox_summary={"pending_count": 1, "blocked_count": 0}))
    sos = build_readiness_result(
        _payload(action_recommendation={"relay_sos_anthony_required": True, "recommended_command": "No command recommended."})
    )

    assert approval["readiness"]["classification"] == "BLOCKED_BY_APPROVAL_STATE"
    assert sos["readiness"]["classification"] == "SOS_HARD_STOP"


def test_backup_repo_local_lock_or_interference_returns_blocked() -> None:
    result = build_readiness_result(
        _payload(
            backup_interference_state={
                "interference_detected": True,
                "repo_local_backup_lock_present": True,
            }
        )
    )

    assert result["readiness"]["classification"] == "BLOCKED_BY_BACKUP_INTERFERENCE"


def test_recommended_next_packet_only_when_safe() -> None:
    safe = build_readiness_result(_payload())
    blocked = build_readiness_result(_payload(requested_operator_mode="OFF"))

    assert safe["recommended_next_packet"] == "AIOS-GOVERNED-SELF-DEVELOPMENT-LOOP-APPLY-V1"
    assert blocked["recommended_next_packet"] is None


def test_command_sanitizer_blocks_protected_commands() -> None:
    command = sanitize_command_field("powershell -File x.ps1 -Mode APPLY; git push")

    assert command["safe_to_surface"] is False
    assert "git push" not in command["display_text"].lower()
