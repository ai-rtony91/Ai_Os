from __future__ import annotations

from automation.forex_engine.broker_demo_rehearsal_runner_v6 import (
    BROKER_DEMO_REHEARSAL_BLOCKED,
    BROKER_DEMO_REHEARSAL_INVALID,
    BROKER_DEMO_REHEARSAL_READY,
    BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED,
    run_broker_demo_rehearsal,
)
from automation.forex_engine.broker_demo_review_packet_v5 import (
    BROKER_DEMO_REVIEW_PACKET_BLOCKED,
    BROKER_DEMO_REVIEW_PACKET_INVALID,
    BROKER_DEMO_REVIEW_PACKET_READY,
    BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED,
)


def _ready_packet() -> dict:
    return {
        "packet_schema": "AIOS_BROKER_DEMO_REVIEW_PACKET_V5A.v1",
        "packet_status": BROKER_DEMO_REVIEW_PACKET_READY,
        "ready": True,
        "blockers": (),
        "approval_required": True,
        "safety_summary": {
            "live_trading": False,
            "order_execution": False,
            "credentials_read": False,
            "env_read": False,
            "network_calls": False,
            "scheduler_daemon_webhook": False,
            "raw_broker_payload_persisted": False,
            "account_id_present": False,
        },
    }


def _blocked_packet() -> dict:
    packet = _ready_packet()
    packet["packet_status"] = BROKER_DEMO_REVIEW_PACKET_BLOCKED
    packet["ready"] = False
    return packet


def _review_required_packet() -> dict:
    packet = _ready_packet()
    packet["packet_status"] = BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED
    packet["ready"] = False
    return packet


def _invalid_packet() -> dict:
    packet = _ready_packet()
    packet["packet_status"] = BROKER_DEMO_REVIEW_PACKET_INVALID
    packet["ready"] = False
    return packet


def _valid_operator_ack() -> dict:
    return {
        "reviewed_by_human": True,
        "simulation_only_ack": True,
        "no_live_trading_ack": True,
        "no_order_execution_ack": True,
        "no_credentials_ack": True,
        "no_network_ack": True,
    }


def _unsafe_network_packet() -> dict:
    packet = _ready_packet()
    packet["safety_summary"]["network_calls"] = True
    return packet


def test_ready_packet_with_valid_operator_ack_is_rehearsal_ready():
    result = run_broker_demo_rehearsal(_ready_packet(), operator_ack=_valid_operator_ack())

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_READY
    assert result["ready"] is True
    assert result["next_safe_action"] == "prepare_protected_demo_connection_preflight"


def test_missing_packet_is_invalid():
    result = run_broker_demo_rehearsal(None)

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_INVALID
    assert result["ready"] is False
    assert "review_packet_schema_missing" in result["blockers"]


def test_blocked_packet_is_blocked():
    result = run_broker_demo_rehearsal(_blocked_packet(), operator_ack=_valid_operator_ack())

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_BLOCKED
    assert result["next_safe_action"] == "resolve_rehearsal_blockers"


def test_ready_packet_without_operator_ack_is_review_required():
    result = run_broker_demo_rehearsal(_ready_packet())

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED
    assert result["operator_ack_summary"]["operator_ack_complete"] is False
    assert result["next_safe_action"] == "complete_human_rehearsal_acknowledgement"


def test_unsafe_network_flag_blocks_rehearsal():
    result = run_broker_demo_rehearsal(_unsafe_network_packet(), operator_ack=_valid_operator_ack())

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_BLOCKED
    assert "network_calls" in result["safety_summary"]


def test_incomplete_operator_ack_is_review_required():
    ack = {"reviewed_by_human": True, "simulation_only_ack": True}
    result = run_broker_demo_rehearsal(_ready_packet(), operator_ack=ack)

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED
    assert result["operator_ack_summary"]["required_fields_present"]["no_live_trading_ack"] is False


def test_invalid_packet_missing_schema_or_status_is_invalid():
    bad = {"packet_status": BROKER_DEMO_REVIEW_PACKET_READY, "ready": True}
    result = run_broker_demo_rehearsal(bad, operator_ack=_valid_operator_ack())

    assert result["rehearsal_status"] == BROKER_DEMO_REHEARSAL_INVALID


def test_next_safe_action_mapping_for_review_required_and_invalid():
    assert (
        run_broker_demo_rehearsal(_review_required_packet(), operator_ack=_valid_operator_ack())
        ["rehearsal_status"]
        == BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED
    )
    assert (
        run_broker_demo_rehearsal(_review_required_packet(), operator_ack=_valid_operator_ack())
        ["next_safe_action"]
        == "complete_human_rehearsal_acknowledgement"
    )
    result_invalid = run_broker_demo_rehearsal(_invalid_packet(), operator_ack=_valid_operator_ack())
    assert result_invalid["next_safe_action"] == "repair_review_packet"


def test_latency_budget_excludes_network():
    result = run_broker_demo_rehearsal(_ready_packet(), operator_ack=_valid_operator_ack())

    assert result["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert result["latency_budget"]["packet_read_ms"] >= 0.0
    assert result["latency_budget"]["operator_ack_eval_ms"] >= 0.0
    assert result["latency_budget"]["safety_gate_eval_ms"] >= 0.0
    assert result["latency_budget"]["rehearsal_mapping_ms"] >= 0.0
