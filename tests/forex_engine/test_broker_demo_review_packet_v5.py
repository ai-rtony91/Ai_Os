from __future__ import annotations

from automation.forex_engine.broker_demo_review_packet_v5 import (
    BROKER_DEMO_REVIEW_PACKET_BLOCKED,
    BROKER_DEMO_REVIEW_PACKET_INVALID,
    BROKER_DEMO_REVIEW_PACKET_READY,
    BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED,
    BROKER_DEMO_DECISION_BLOCKED,
    BROKER_DEMO_DECISION_READY,
    BROKER_DEMO_DECISION_REVIEW_REQUIRED,
    build_broker_demo_review_packet,
)


def _base_decision() -> dict:
    return {
        "decision": BROKER_DEMO_DECISION_READY,
        "ready": True,
        "blockers": tuple(),
        "evidence_summary": {
            "integration": {"ready": True},
            "connector": {"ready": True},
            "demo_data": {"ready": True},
        },
        "safety_summary": {
            "unsafe_flags": {
                "live_trading": False,
                "order_execution": False,
                "credentials_read": False,
                "env_read": False,
                "network_calls": False,
                "scheduler_daemon_webhook": False,
            }
        },
    }


def _unsafe_decision() -> dict:
    base = _base_decision()
    base["safety_summary"]["unsafe_flags"]["network_calls"] = True
    return base


def test_ready_v4_decision_produces_ready_review_packet():
    packet = build_broker_demo_review_packet(_base_decision())

    assert packet["packet_status"] == BROKER_DEMO_REVIEW_PACKET_READY
    assert packet["ready"] is True
    assert packet["approval_required"] is True
    assert "integration_contract_present" in packet["review_checklist"]
    assert packet["next_safe_action"] == "human_review_and_approve_protected_demo_progression"


def test_blocked_v4_decision_produces_blocked_review_packet():
    decision = _base_decision()
    decision["decision"] = BROKER_DEMO_DECISION_BLOCKED
    decision["ready"] = False

    packet = build_broker_demo_review_packet(decision)

    assert packet["packet_status"] == BROKER_DEMO_REVIEW_PACKET_BLOCKED
    assert packet["ready"] is False
    assert packet["next_safe_action"] == "resolve_blockers_before_protected_demo_review"


def test_missing_decision_produces_invalid_packet():
    packet = build_broker_demo_review_packet(None)

    assert packet["packet_status"] == BROKER_DEMO_REVIEW_PACKET_INVALID
    assert packet["ready"] is False
    assert packet["review_checklist"]["integration_contract_present"] is False


def test_review_required_v4_decision_maps_to_review_required_packet():
    decision = _base_decision()
    decision["decision"] = BROKER_DEMO_DECISION_REVIEW_REQUIRED
    decision["ready"] = False

    packet = build_broker_demo_review_packet(decision)

    assert packet["packet_status"] == BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED
    assert packet["ready"] is False
    assert packet["next_safe_action"] == "complete_operator_review_and_approve"


def test_unsafe_live_network_order_flags_block_review_packet():
    decision = _unsafe_decision()
    decision["decision"] = BROKER_DEMO_DECISION_READY
    decision["ready"] = True

    packet = build_broker_demo_review_packet(decision)

    assert packet["packet_status"] == BROKER_DEMO_REVIEW_PACKET_BLOCKED
    assert packet["safety_summary"]["network_calls"] is True
    assert packet["safety_summary"]["live_trading"] is False


def test_review_checklist_has_required_fields():
    packet = build_broker_demo_review_packet(_base_decision())

    required_fields = (
        "integration_contract_present",
        "connector_probe_present",
        "demo_data_present",
        "safety_gates_clear",
        "no_live_trading",
        "no_order_execution",
        "no_credentials",
        "no_network_calls",
        "no_env_reads",
        "human_approval_required",
    )
    assert all(field in packet["review_checklist"] for field in required_fields)
    assert packet["review_checklist"]["human_approval_required"] is True


def test_metadata_sanitization_removes_sensitive_fields():
    metadata = {
        "trace_id": "op-001",
        "api_key": "secret",
        "token": "abc",
        "nested": {"password": "p@ss", "safe_value": 42},
        "payload": [{"account_id": "123", "mode": "DEMO_DRYRUN"}],
    }

    packet = build_broker_demo_review_packet(_base_decision(), metadata=metadata)

    assert "api_key" not in packet["sanitized_metadata"]
    assert "token" not in packet["sanitized_metadata"]
    assert "password" not in packet["sanitized_metadata"]["nested"]
    assert "account_id" not in packet["sanitized_metadata"]["payload"][0]
    assert packet["sanitized_metadata"]["trace_id"] == "op-001"
    assert packet["sanitized_metadata"]["payload"][0]["mode"] == "DEMO_DRYRUN"


def test_latency_budget_marks_network_as_offline_default():
    packet = build_broker_demo_review_packet(_base_decision())

    assert packet["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert packet["latency_budget"]["decision_read_ms"] >= 0.0
    assert packet["latency_budget"]["packet_build_ms"] >= 0.0
    assert packet["latency_budget"]["checklist_eval_ms"] >= 0.0
    assert packet["latency_budget"]["safety_summary_ms"] >= 0.0
