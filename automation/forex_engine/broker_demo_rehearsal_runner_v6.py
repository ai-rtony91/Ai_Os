"""Offline-default broker-demo rehearsal runner V6A."""

from __future__ import annotations

import time
from typing import Any, Mapping

from automation.forex_engine.broker_demo_review_packet_v5 import (
    BROKER_DEMO_REVIEW_PACKET_BLOCKED,
    BROKER_DEMO_REVIEW_PACKET_INVALID,
    BROKER_DEMO_REVIEW_PACKET_READY,
    BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED,
)

BROKER_DEMO_REHEARSAL_READY = "BROKER_DEMO_REHEARSAL_READY"
BROKER_DEMO_REHEARSAL_BLOCKED = "BROKER_DEMO_REHEARSAL_BLOCKED"
BROKER_DEMO_REHEARSAL_INVALID = "BROKER_DEMO_REHEARSAL_INVALID"
BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED = "BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED"

REQUIRED_OPERATOR_ACK_FIELDS = (
    "reviewed_by_human",
    "simulation_only_ack",
    "no_live_trading_ack",
    "no_order_execution_ack",
    "no_credentials_ack",
    "no_network_ack",
)


def run_broker_demo_rehearsal(
    review_packet: Mapping[str, Any] | None,
    operator_ack: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    packet_read_start = time.perf_counter()
    packet = dict(review_packet or {})
    packet_read_ms = _ms(packet_read_start, time.perf_counter())

    packet_schema = packet.get("packet_schema")
    packet_status = packet.get("packet_status")
    packet_ready = bool(packet.get("ready"))
    packet_blockers = tuple(_as_tuple(packet.get("blockers") or ()))
    packet_summary = {
        "packet_status": packet_status,
        "ready": packet_ready,
        "approval_required": bool(packet.get("approval_required", False)),
        "packet_schema": packet_schema,
    }
    packet_summary.update(_safe_copy_mapping(packet.get("evidence_summary") or {}))

    ack = dict(operator_ack or {})
    operator_ack_eval_start = time.perf_counter()
    operator_ack_ok = _ack_complete(ack)
    operator_ack_summary = {
        "operator_ack": ack,
        "required_fields_present": _required_fields_present(ack),
        "operator_ack_complete": operator_ack_ok,
    }
    operator_ack_eval_ms = _ms(operator_ack_eval_start, time.perf_counter())

    safety_gate_start = time.perf_counter()
    packet_safety = _extract_safety_summary(packet)
    operator_safety = _build_operator_safety(packet, operator_ack)
    safety_summary = {
        "live_trading": bool(packet_safety.get("live_trading", False)),
        "order_execution": bool(packet_safety.get("order_execution", False)),
        "credentials_read": bool(packet_safety.get("credentials_read", False)),
        "env_read": bool(packet_safety.get("env_read", False)),
        "network_calls": bool(packet_safety.get("network_calls", False)),
        "scheduler_daemon_webhook": bool(packet_safety.get("scheduler_daemon_webhook", False)),
        "raw_broker_payload_persisted": bool(packet_safety.get("raw_broker_payload_persisted", False)),
        "account_id_present": bool(packet_safety.get("account_id_present", False)),
        "operator_ack_matches_safety_constraints": operator_safety,
    }
    safety_gate_eval_ms = _ms(safety_gate_start, time.perf_counter())

    rehearsal_mapping_start = time.perf_counter()
    blocked_due_to_schema = not bool(packet_schema and packet_status)

    if not review_packet:
        rehearsal_status = BROKER_DEMO_REHEARSAL_INVALID
    elif blocked_due_to_schema:
        rehearsal_status = BROKER_DEMO_REHEARSAL_INVALID
    elif packet_status == BROKER_DEMO_REVIEW_PACKET_BLOCKED:
        rehearsal_status = BROKER_DEMO_REHEARSAL_BLOCKED
    elif operator_safety:
        rehearsal_status = BROKER_DEMO_REHEARSAL_BLOCKED
    elif not operator_ack_ok and bool(packet.get("approval_required", False)):
        rehearsal_status = BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED
    elif packet_status == BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED:
        rehearsal_status = BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED
    elif (
        packet_status == BROKER_DEMO_REVIEW_PACKET_READY
        and packet_ready
        and bool(packet.get("approval_required", False))
        and operator_ack_ok
    ):
        rehearsal_status = BROKER_DEMO_REHEARSAL_READY
    elif packet_status == BROKER_DEMO_REVIEW_PACKET_INVALID:
        rehearsal_status = BROKER_DEMO_REHEARSAL_INVALID
    elif packet_status == BROKER_DEMO_REVIEW_PACKET_BLOCKED:
        rehearsal_status = BROKER_DEMO_REHEARSAL_BLOCKED
    else:
        rehearsal_status = BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED

    rehearsal_mapping_ms = _ms(rehearsal_mapping_start, time.perf_counter())

    return {
        "rehearsal_schema": "AIOS_BROKER_DEMO_REHEARSAL_RUNNER_V6A.v1",
        "rehearsal_status": rehearsal_status,
        "ready": rehearsal_status == BROKER_DEMO_REHEARSAL_READY,
        "blockers": _blocked_flags(
            packet_blockers,
            packet_status,
            packet_schema=packet_schema,
            packet_status_present=packet_status,
            packet_ready=packet_ready,
            operator_ack=ack,
        ),
        "packet_summary": packet_summary,
        "operator_ack_summary": operator_ack_summary,
        "safety_summary": safety_summary,
        "next_safe_action": _next_safe_action(rehearsal_status),
        "latency_budget": {
            "packet_read_ms": packet_read_ms,
            "operator_ack_eval_ms": operator_ack_eval_ms,
            "safety_gate_eval_ms": safety_gate_eval_ms,
            "rehearsal_mapping_ms": rehearsal_mapping_ms,
            "network_latency_ms": "excluded_offline_default",
        },
    }


def _ack_complete(operator_ack: Mapping[str, Any] | None) -> bool:
    if not operator_ack:
        return False
    return all(bool(operator_ack.get(field, False)) for field in REQUIRED_OPERATOR_ACK_FIELDS)


def _required_fields_present(operator_ack: Mapping[str, Any] | None) -> dict[str, bool]:
    present: dict[str, bool] = {}
    payload = dict(operator_ack or {})
    for field in REQUIRED_OPERATOR_ACK_FIELDS:
        present[field] = field in payload
    return present


def _extract_safety_summary(packet: Mapping[str, Any]) -> dict[str, bool]:
    safety_summary = {}
    if not isinstance(packet, Mapping):
        return safety_summary

    packet_safety = _coerce_mapping(packet.get("safety_summary"))
    decision = _coerce_mapping(packet.get("decision"))
    evidence = _coerce_mapping(packet.get("evidence_summary"))
    safety = _coerce_mapping(packet_safety.get("unsafe_flags"))

    for key in (
        "live_trading",
        "order_execution",
        "credentials_read",
        "env_read",
        "network_calls",
        "scheduler_daemon_webhook",
    ):
        if key in safety:
            safety_summary[key] = bool(safety.get(key, False))
        elif key in packet_safety:
            safety_summary[key] = bool(packet_safety.get(key, False))
        elif key in decision.get("safety_summary", {}):
            safety_summary[key] = bool(decision["safety_summary"].get(key, False))
        else:
            safety_summary[key] = False

    # review packet may expose these through evidence or direct payload
    safety_summary["raw_broker_payload_persisted"] = bool(
        evidence.get("raw_broker_payload_persisted", False)
        or packet_safety.get("raw_broker_payload_persisted", False)
        or decision.get("raw_broker_payload_persisted", False)
    )
    safety_summary["account_id_present"] = bool(
        evidence.get("account_id_present", False)
        or packet_safety.get("account_id_present", False)
        or decision.get("account_id_present", False)
    )
    return safety_summary


def _build_operator_safety(packet: Mapping[str, Any], operator_ack: Mapping[str, Any] | None) -> bool:
    safety = _extract_safety_summary(packet)
    return any(safety.get(key, False) for key in safety)


def _blocked_flags(
    packet_blockers: tuple[str, ...],
    packet_status: Any,
    *,
    packet_schema: Any,
    packet_status_present: Any,
    packet_ready: Any,
    operator_ack: Mapping[str, Any],
) -> tuple[str, ...]:
    blockers: list[str] = list(packet_blockers)
    if not packet_schema:
        blockers.append("review_packet_schema_missing")
    if not packet_status_present:
        blockers.append("review_packet_status_missing")
    if packet_status == BROKER_DEMO_REVIEW_PACKET_BLOCKED:
        blockers.append("review_packet_blocked")
    if not bool(packet_ready) and packet_status == BROKER_DEMO_REVIEW_PACKET_READY:
        blockers.append("review_packet_ready_flag_false")
    if not _ack_complete(operator_ack):
        blockers.append("operator_ack_incomplete")
    return tuple(_unique(blockers))


def _coerce_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safe_copy_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return tuple()
    if isinstance(value, tuple):
        return tuple(str(item) for item in value)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def _unique(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return tuple(output)


def _ms(start: float, end: float) -> float:
    return (end - start) * 1000.0


def _next_safe_action(rehearsal_status: str) -> str:
    return {
        BROKER_DEMO_REHEARSAL_READY: "prepare_protected_demo_connection_preflight",
        BROKER_DEMO_REHEARSAL_BLOCKED: "resolve_rehearsal_blockers",
        BROKER_DEMO_REHEARSAL_INVALID: "repair_review_packet",
        BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED: "complete_human_rehearsal_acknowledgement",
    }.get(rehearsal_status, "complete_human_rehearsal_acknowledgement")
