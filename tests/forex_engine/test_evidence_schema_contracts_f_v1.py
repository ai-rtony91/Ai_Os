"""Unit tests for Packet F evidence schema contracts."""

from __future__ import annotations

import pytest

from automation.forex_engine import evidence_schema_contracts_f_v1 as contracts


def valid_intent() -> dict:
    return {
        "timestamp": "2026-06-21T10:00:00+00:00",
        "correlation_id": "corr-intent-1",
        "strategy_id": "mean_reversion_v1",
        "candidate_id": "candidate-1",
        "risk_summary": {"max_loss_usd": 10.0},
        "governance_status": "UNDER_REVIEW",
        "approval_status": "PENDING",
        "endpoint_mode": "DEMO",
        "kill_switch_state": True,
        "evidence_references": ["evidence://intent/1"],
        "replay_references": ["replay://intent/1"],
        "execution_authority_granted": False,
    }


def valid_approval() -> dict:
    return {
        "timestamp": "2026-06-21T10:01:00+00:00",
        "correlation_id": "corr-approval-1",
        "strategy_id": "mean_reversion_v1",
        "candidate_id": "candidate-1",
        "governance_status": "REVIEWED",
        "risk_summary": {"max_loss_usd": 10.0},
        "approval_status": "APPROVED",
        "endpoint_mode": "DEMO",
        "kill_switch_state": True,
        "evidence_references": ["evidence://approval/1"],
        "replay_references": ["replay://approval/1"],
        "approval_scope": "demo-micro-order",
        "approval_window_expires_at": "2026-06-21T10:20:00+00:00",
        "manual_arming_required": True,
        "timeout_seconds": 600,
        "execution_authority_granted": False,
    }


def valid_blocked_attempt() -> dict:
    return {
        "timestamp": "2026-06-21T10:02:00+00:00",
        "correlation_id": "corr-attempt-1",
        "strategy_id": "mean_reversion_v1",
        "candidate_id": "candidate-1",
        "governance_status": "BLOCKED",
        "risk_summary": {"max_loss_usd": 10.0},
        "approval_status": "REJECTED",
        "endpoint_mode": "DEMO",
        "kill_switch_state": True,
        "evidence_references": ["evidence://attempt/1"],
        "replay_references": ["replay://attempt/1"],
        "blockers": ["broker_connection_detected", "network_access_detected"],
        "blocker_reason": "unsafe runtime path detected",
        "halt_type": "HARD_GATE_FAIL",
        "replay_summary_ref": "replay://attempt/1/summary",
        "execution_authority_granted": False,
    }


def valid_rejected_attempt() -> dict:
    return {
        "timestamp": "2026-06-21T10:03:00+00:00",
        "correlation_id": "corr-attempt-1",
        "strategy_id": "mean_reversion_v1",
        "candidate_id": "candidate-1",
        "governance_status": "REJECTED",
        "risk_summary": {"max_loss_usd": 10.0},
        "approval_status": "REJECTED",
        "endpoint_mode": "DEMO",
        "kill_switch_state": True,
        "evidence_references": ["evidence://attempt/2"],
        "replay_references": ["replay://attempt/2"],
        "rejection_reason": "risk_gate_timeout",
        "rejection_code": "RISK_TIMEOUT",
        "upstream_status_ref": "status://approval-rejected",
        "reapproval_path": ["request_manual_review", "renew_credentials_boundary"],
        "execution_authority_granted": False,
    }


def valid_execution_attempt() -> dict:
    return {
        "timestamp": "2026-06-21T10:04:00+00:00",
        "correlation_id": "corr-attempt-2",
        "strategy_id": "mean_reversion_v1",
        "candidate_id": "candidate-1",
        "governance_status": "UNDER_REVIEW",
        "risk_summary": {"max_loss_usd": 10.0},
        "approval_status": "DEFERRED",
        "endpoint_mode": "DEMO",
        "kill_switch_state": True,
        "evidence_references": ["evidence://attempt/3"],
        "replay_references": ["replay://attempt/3"],
        "attempt_outcome": "BLOCKED",
        "attempt_status": "NOT_EXECUTED",
        "next_safe_action": "repair_halts_before_next_packet",
        "final_disarm_required": True,
        "terminal_disposition": "BLOCKED",
        "execution_authority_granted": False,
    }


def test_validate_intent_record_required_fields() -> None:
    base = valid_intent()
    assert contracts.validate_intent_record(base) is True

    missing = dict(base)
    missing.pop("strategy_id")
    with pytest.raises(ValueError, match="missing required"):
        contracts.validate_intent_record(missing)


def test_validate_intent_record_forbidden_fields_blocked() -> None:
    with_credentials = valid_intent()
    with_credentials["network_access"] = True
    with pytest.raises(ValueError, match="forbidden unsafe"):
        contracts.validate_intent_record(with_credentials)


def test_validate_approval_record_requires_ttl_window_when_approved() -> None:
    base = valid_approval()
    assert contracts.validate_approval_record(base) is True

    missing = dict(base)
    missing["approval_window_expires_at"] = ""
    with pytest.raises(ValueError, match="missing required fields"):
        contracts.validate_approval_record(missing)


def test_validate_approval_record_blocks_account_identifier() -> None:
    blocked = valid_approval()
    blocked["account_id"] = "acct-123"
    with pytest.raises(ValueError, match="account_id"):
        contracts.validate_approval_record(blocked)


def test_validate_attempt_record_endpoint_mode_only_demo() -> None:
    base = valid_blocked_attempt()
    base["endpoint_mode"] = "LIVE"
    with pytest.raises(ValueError, match="endpoint_mode must be one of"):
        contracts.validate_blocked_attempt_record(base)


def test_validate_blocked_attempt_record_required_state_and_fields() -> None:
    assert contracts.validate_blocked_attempt_record(valid_blocked_attempt()) is True

    bad = valid_blocked_attempt()
    bad["halt_type"] = "UNKNOWN"
    with pytest.raises(ValueError, match="must be one of"):
        contracts.validate_blocked_attempt_record(bad)


def test_validate_rejected_attempt_record_references_required() -> None:
    assert contracts.validate_rejected_attempt_record(valid_rejected_attempt()) is True

    bad = valid_rejected_attempt()
    bad["upstream_status_ref"] = ""
    with pytest.raises(ValueError, match="missing required fields"):
        contracts.validate_rejected_attempt_record(bad)


def test_validate_execution_attempt_record_is_not_executed_only() -> None:
    assert contracts.validate_execution_attempt_record(valid_execution_attempt()) is True

    bad = valid_execution_attempt()
    bad["attempt_status"] = "EXECUTED"
    with pytest.raises(ValueError, match="NOT_EXECUTED"):
        contracts.validate_execution_attempt_record(bad)


def test_validate_execution_attempt_forbids_unsafe_execution_flags() -> None:
    bad = valid_execution_attempt()
    bad["execution_authority_granted"] = True
    with pytest.raises(ValueError, match="execution_authority_granted must be false"):
        contracts.validate_execution_attempt_record(bad)


def test_build_contract_summary_contains_local_only_safety() -> None:
    summary = contracts.build_evidence_schema_contract_summary()
    assert summary["no_broker_connectivity"] is True
    assert summary["no_credentials"] is True
    assert summary["no_account_identifiers"] is True
    assert summary["no_network_access"] is True
    assert "timestamp" in summary["required_common_fields"]
