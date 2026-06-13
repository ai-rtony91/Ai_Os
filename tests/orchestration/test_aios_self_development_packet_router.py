from __future__ import annotations

import json
import sys

sys.dont_write_bytecode = True

from automation.orchestration.self_audit.aios_self_development_packet_router import (
    SCHEMA,
    build_router_result,
    classify_candidate_packet,
    rank_candidate_packets,
    sanitize_command_field,
)


def _source_marker() -> str:
    return "CODEX" + "-ONLY PROMPT"


def _token_marker() -> str:
    return "AI_OS " + "EXECUTION TOKEN"


def _self_audit_result() -> dict:
    return {
        "schema": "AIOS_SELF_AUDIT_LOOP_RESULT.v1",
        "mode": "DRY_RUN_READ_ONLY",
        "safety": {
            "status": "PASS",
        },
        "candidate_packets": [
            {
                "packet_id": "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1",
            },
            {
                "packet_id": "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1",
            },
        ],
        "recommended_next_packet": {
            "packet_id": "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1",
        },
    }


def _payload(**overrides: object) -> dict:
    payload = {
        "generated_utc": "2026-06-13T00:00:00Z",
        "repo_state": {
            "branch": "feature/self-development-packet-router-v1",
            "expected_branch": "main",
            "branch_matches_expected": False,
            "dirty": False,
        },
        "self_audit_result": _self_audit_result(),
        "campaign_no_ready": {
            "schema": "AIOS_CAMPAIGN_NO_READY_STAGE_DISCOVERY.v1",
            "overall_readiness": "NO_READY_STAGE",
            "no_ready_stage_classification": "COMPLETE_IDLE",
            "registry_inconsistency_detected": False,
        },
        "campaign_next_task": {
            "schema": "AIOS_CAMPAIGN_NEXT_TASK_RECOMMENDATION.v1",
            "overall_readiness": "NO_READY_STAGE",
            "next_packet_candidate": None,
        },
        "action_recommendation": {
            "packet_status": "no_active_packet",
            "recommended_command": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1 -OutputJson",
        },
        "no_write_proof": {
            "changed": False,
            "git_state_changed": False,
            "forbidden_surface_changed": False,
        },
        "max_candidate_packets": 5,
    }
    payload.update(overrides)
    return payload


def test_python_logic_emits_router_schema() -> None:
    result = build_router_result(_payload())

    assert result["schema"] == SCHEMA
    assert result["mode"] == "DRY_RUN_READ_ONLY"
    assert result["safety"]["status"] == "PASS"


def test_router_consumes_self_audit_result_schema() -> None:
    result = build_router_result(_payload())

    assert result["source_self_audit_schema"] == "AIOS_SELF_AUDIT_LOOP_RESULT.v1"
    assert result["input_summary"]["self_audit_status"] == "PASS"


def test_router_ranks_validator_evidence_before_dashboard_packets() -> None:
    result = build_router_result(_payload())

    assert result["recommended_packet"]["packet_id"] == "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1"
    ranked_ids = [item["packet_id"] for item in result["candidate_packets"]]
    assert ranked_ids.index("AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1") < ranked_ids.index(
        "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1"
    )


def test_router_blocks_apply_execution_recommendation() -> None:
    result = build_router_result(
        _payload(
            action_recommendation={
                "packet_status": "ready",
                "recommended_command": "powershell -NoProfile -ExecutionPolicy Bypass -File worker.ps1 -Mode APPLY",
            }
        )
    )

    command = result["input_summary"]["action_recommendation_command"]
    assert command["safe_to_surface"] is False
    assert "APPLY" not in command["display_text"]


def test_router_blocks_packet_write_candidates() -> None:
    candidate = classify_candidate_packet("AIOS-PACKET-DRAFT-WRITER-DRYRUN-V1")

    assert candidate["blocked"] is True
    assert candidate["classification"] == "BLOCKED_WRITES_PACKET"


def test_router_blocks_ready_stage_mutation_candidates() -> None:
    candidate = classify_candidate_packet("AIOS-CREATE-READY-STAGE-DRYRUN-V1")

    assert candidate["blocked"] is True
    assert candidate["classification"] == "BLOCKED_READY_STAGE_MUTATION"


def test_router_blocks_protected_runtime_broker_secret_candidates() -> None:
    candidates = [
        ("AIOS-GIT-ADD-COMMIT-DRYRUN-V1", "BLOCKED_PROTECTED_ACTION"),
        ("AIOS-WORKER-LAUNCH-SCHEDULER-DRYRUN-V1", "BLOCKED_RUNTIME_OR_WORKER"),
        ("AIOS-BROKER-OANDA-WEBHOOK-ORDER-LIVE-TRADING-DRYRUN-V1", "BLOCKED_LIVE_TRADING_OR_BROKER"),
        ("AIOS-SECRET-ENV-DRYRUN-V1", "BLOCKED_SECRET_OR_ENV"),
    ]

    for packet_id, classification in candidates:
        candidate = classify_candidate_packet(packet_id)
        assert candidate["blocked"] is True
        assert candidate["classification"] == classification


def test_router_sanitizes_command_fields() -> None:
    sanitized = sanitize_command_field("git add -- file && git commit -m unsafe")

    assert sanitized["safe_to_surface"] is False
    assert "git add" not in sanitized["display_text"].lower()
    assert "git commit" not in sanitized["display_text"].lower()


def test_router_does_not_output_forbidden_markers() -> None:
    result = build_router_result(
        _payload(
            self_audit_result={
                **_self_audit_result(),
                "candidate_packets": [{"packet_id": _source_marker()}, {"packet_id": _token_marker()}],
            },
            action_recommendation={
                "packet_status": "unsafe",
                "recommended_command": _source_marker() + "\n" + _token_marker(),
            },
        )
    )
    encoded = json.dumps(result)

    assert _source_marker() not in encoded
    assert _token_marker() not in encoded


def test_no_write_proof_blocks_forbidden_delta() -> None:
    result = build_router_result(
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


def test_confidence_insufficient_stops_when_no_safe_candidate() -> None:
    safe, blocked = rank_candidate_packets(["AIOS-BROKER-LIVE-ORDER-APPLY-V1"])

    assert safe == []
    assert blocked[0]["blocked"] is True
