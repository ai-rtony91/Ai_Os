from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True

from automation.orchestration.self_development.aios_governed_self_development_loop import (
    NEXT_SAFE_PACKET,
    SCHEMA,
    build_governed_self_development_result,
    sanitize_command_field,
)


def _source_marker() -> str:
    return "CODEX" + "-ONLY PROMPT"


def _token_marker() -> str:
    return "AI_OS " + "EXECUTION TOKEN"


def _self_audit(**overrides: object) -> dict:
    payload = {
        "schema": "AIOS_SELF_AUDIT_LOOP_RESULT.v1",
        "mode": "DRY_RUN_READ_ONLY",
        "safety": {"status": "PASS"},
        "stop_conditions": [],
    }
    payload.update(overrides)
    return payload


def _packet_router(**overrides: object) -> dict:
    payload = {
        "schema": "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1",
        "mode": "DRY_RUN_READ_ONLY",
        "safety": {"status": "PASS"},
        "recommended_packet": {"packet_id": "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1"},
        "stop_conditions": [],
    }
    payload.update(overrides)
    return payload


def _validator_router(**overrides: object) -> dict:
    payload = {
        "schema": "AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1",
        "mode": "DRY_RUN_READ_ONLY",
        "safety": {
            "status": "PASS",
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "outputs_packet_body": False,
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
        "recommended_chains": [],
        "stop_conditions": [],
    }
    payload.update(overrides)
    return payload


def _day_night(**overrides: object) -> dict:
    payload = {
        "schema": "AIOS_DAY_NIGHT_READINESS_RESULT.v1",
        "mode": "DRY_RUN_READ_ONLY",
        "readiness": {
            "classification": "SUPERVISED_RECOMMENDATION_ALLOWED",
            "recommendation_allowed": True,
            "execution_allowed": False,
        },
        "approval_state": {
            "status": "CLEAR",
            "approval_required": False,
            "sos_hard_stop": False,
        },
        "runtime_worker_state": {
            "status": "CLEAR",
            "runtime_risk_detected": False,
            "worker_launch_detected": False,
            "scheduler_or_daemon_detected": False,
        },
        "backup_interference_state": {
            "status": "CLEAR",
            "interference_detected": False,
            "repo_local_backup_lock_present": False,
            "backup_in_progress": False,
            "snapshot_restore_candidate_present": False,
        },
        "safety": {
            "status": "PASS",
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "outputs_packet_body": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_relay": False,
            "starts_runtime": False,
            "launches_workers": False,
            "scheduler_or_daemon": False,
            "protected_action_recommended": False,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
        },
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
            "dirty_allowed_for_governed_loop_validation": False,
            "fail_on_dirty_worktree": True,
        },
        "self_audit_result": _self_audit(),
        "packet_router_result": _packet_router(),
        "validator_evidence_router_result": _validator_router(),
        "day_night_readiness_result": _day_night(),
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
        },
        "safe_surfaces_used": [],
        "blocked_surfaces": [],
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
    }
    payload.update(overrides)
    return payload


def test_python_logic_emits_governed_loop_schema() -> None:
    result = build_governed_self_development_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["safety"]["status"] == "PASS"


def test_loop_requires_self_audit_pass() -> None:
    result = build_governed_self_development_result(
        _payload(self_audit_result=_self_audit(safety={"status": "BLOCKED"}))
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "SELF_AUDIT_NOT_PASS" in result["stop_conditions"]
    assert result["recommended_next_packet"] is None


def test_loop_requires_validator_evidence_router_pass() -> None:
    result = build_governed_self_development_result(
        _payload(validator_evidence_router_result=_validator_router(safety={"status": "BLOCKED"}))
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "VALIDATOR_EVIDENCE_ROUTER_NOT_PASS" in result["stop_conditions"]


def test_loop_requires_day_night_supervised_recommendation_allowed() -> None:
    result = build_governed_self_development_result(
        _payload(
            day_night_readiness_result=_day_night(
                readiness={
                    "classification": "OBSERVE_ALLOWED",
                    "recommendation_allowed": False,
                    "execution_allowed": False,
                }
            )
        )
    )

    assert result["recommended_next_packet"] is None
    assert "DAY_NIGHT_SUPERVISED_RECOMMENDATION_NOT_ALLOWED" in result["stop_conditions"]


def test_loop_blocks_if_approval_sos_or_readiness_stop_condition_exists() -> None:
    result = build_governed_self_development_result(
        _payload(
            day_night_readiness_result=_day_night(
                approval_state={
                    "status": "SOS_HARD_STOP",
                    "approval_required": True,
                    "sos_hard_stop": True,
                },
                stop_conditions=["SOS_HARD_STOP"],
            )
        )
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "APPROVAL_OR_SOS_STOP_CONDITION" in result["stop_conditions"]
    assert "DAY_NIGHT_READINESS_STOP_SOS_HARD_STOP" in result["stop_conditions"]


def test_loop_blocks_if_backup_interference_exists() -> None:
    result = build_governed_self_development_result(
        _payload(
            day_night_readiness_result=_day_night(
                backup_interference_state={
                    "status": "BLOCKED_BY_BACKUP_INTERFERENCE",
                    "interference_detected": True,
                    "repo_local_backup_lock_present": True,
                }
            )
        )
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "BACKUP_INTERFERENCE" in result["stop_conditions"]


def test_loop_blocks_if_runtime_worker_or_protected_action_appears() -> None:
    result = build_governed_self_development_result(
        _payload(
            validator_evidence_router_result=_validator_router(
                safety={"status": "PASS", "protected_action_recommended": True}
            ),
            day_night_readiness_result=_day_night(
                runtime_worker_state={
                    "status": "BLOCKED_BY_RUNTIME_RISK",
                    "runtime_risk_detected": True,
                    "worker_launch_detected": True,
                }
            ),
            action_recommendation={"recommended_command": "git push origin main"},
        )
    )

    assert result["safety"]["status"] == "BLOCKED"
    assert "VALIDATOR_EVIDENCE_ROUTER_UNSAFE_FLAG_PROTECTED_ACTION_RECOMMENDED" in result["stop_conditions"]
    assert "RUNTIME_OR_WORKER_STOP_CONDITION" in result["stop_conditions"]
    assert "ACTION_RECOMMENDATION_COMMAND_UNSAFE" in result["stop_conditions"]


def test_loop_sanitizes_action_recommendation_command_fields() -> None:
    result = build_governed_self_development_result(
        _payload(action_recommendation={"recommended_command": "git add -- unsafe && git commit -m unsafe"})
    )
    encoded = json.dumps(result).lower()

    assert result["safety"]["action_recommendation_command"]["safe_to_surface"] is False
    assert "git add" not in encoded
    assert "git commit" not in encoded


def test_loop_outputs_recommended_next_packet_only_when_safe() -> None:
    safe = build_governed_self_development_result(_payload())
    blocked = build_governed_self_development_result(
        _payload(packet_router_result=_packet_router(safety={"status": "BLOCKED"}))
    )

    assert safe["recommended_next_packet"]["packet_id"] == NEXT_SAFE_PACKET
    assert blocked["recommended_next_packet"] is None


def test_loop_never_outputs_packet_body_text() -> None:
    result = build_governed_self_development_result(
        _payload(
            action_recommendation={
                "recommended_command": _source_marker() + "\n" + _token_marker(),
            }
        )
    )
    encoded = json.dumps(result)

    assert _source_marker() not in encoded
    assert _token_marker() not in encoded
    assert result["safety"]["outputs_packet_body"] is False


def test_loop_never_recommends_protected_or_runtime_commands() -> None:
    result = build_governed_self_development_result(_payload())
    action = result["next_safe_action"].lower()

    assert "git add" not in action
    assert "git commit" not in action
    assert "git push" not in action
    assert "git merge" not in action
    assert "start-aios" not in action
    assert "open-aiosworker" not in action


def test_no_write_proof_blocks_forbidden_delta() -> None:
    result = build_governed_self_development_result(
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


def test_command_sanitizer_withholds_safe_command_text_too() -> None:
    command = sanitize_command_field(
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1 -OutputJson"
    )

    assert command["safe_to_surface"] is True
    assert "powershell" not in command["display_text"].lower()
