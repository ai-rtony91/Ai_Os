"""Offline-default broker-demo human review packet builder V5A."""

from __future__ import annotations

import time
from typing import Any, Mapping


BROKER_DEMO_REVIEW_PACKET_READY = "BROKER_DEMO_REVIEW_PACKET_READY"
BROKER_DEMO_REVIEW_PACKET_BLOCKED = "BROKER_DEMO_REVIEW_PACKET_BLOCKED"
BROKER_DEMO_REVIEW_PACKET_INVALID = "BROKER_DEMO_REVIEW_PACKET_INVALID"
BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED = "BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED"

BROKER_DEMO_DECISION_READY = "BROKER_DEMO_DECISION_READY"
BROKER_DEMO_DECISION_BLOCKED = "BROKER_DEMO_DECISION_BLOCKED"
BROKER_DEMO_DECISION_INVALID = "BROKER_DEMO_DECISION_INVALID"
BROKER_DEMO_DECISION_REVIEW_REQUIRED = "BROKER_DEMO_DECISION_REVIEW_REQUIRED"

SENSITIVE_METADATA_KEYS = {
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "credential",
    "credentials",
    "account_id",
    "account_number",
    "live_account_id",
    "broker_order_id",
    "raw_payload",
    "raw_request",
    "raw_response",
    "raw_endpoint",
    "live_account",
}


def build_broker_demo_review_packet(
    decision: Mapping[str, Any] | None,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    packet_read_start = time.perf_counter()
    v4_decision = dict(decision or {})
    decision_read_ms = _ms(packet_read_start, time.perf_counter())

    decision_value = str(v4_decision.get("decision", "")).upper()
    ready_value = bool(v4_decision.get("ready"))
    blockers = _as_tuple(v4_decision.get("blockers") or tuple())
    evidence_summary = dict(v4_decision.get("evidence_summary", {}))

    safe_summary_source = v4_decision.get("safety_summary", {})
    unsafe_flags = _extract_unsafe_flags(
        safe_summary_source.get("unsafe_flags", v4_decision.get("unsafe_flags", {}))
    )

    integration_present = bool(evidence_summary.get("integration"))
    connector_present = bool(evidence_summary.get("connector"))
    demo_data_present = bool(evidence_summary.get("demo_data"))

    checklist_eval_start = time.perf_counter()
    checklist = {
        "integration_contract_present": integration_present,
        "connector_probe_present": connector_present,
        "demo_data_present": demo_data_present,
        "safety_gates_clear": not any((v4_decision.get("blockers") or ())),
        "no_live_trading": not bool(unsafe_flags.get("live_trading", False)),
        "no_order_execution": not bool(unsafe_flags.get("order_execution", False)),
        "no_credentials": not (
            bool(unsafe_flags.get("credentials_read", False))
            or bool(evidence_summary.get("credentials_read"))
            or bool(v4_decision.get("credentials_read", False))
        ),
        "no_network_calls": not (
            bool(unsafe_flags.get("network_calls", False))
            or bool(evidence_summary.get("network_calls", False))
            or bool(v4_decision.get("network_calls", False))
        ),
        "no_env_reads": not (
            bool(unsafe_flags.get("env_read", False))
            or bool(evidence_summary.get("env_read", False))
            or bool(v4_decision.get("env_read", False))
        ),
        "human_approval_required": True,
    }
    checklist_eval_ms = _ms(checklist_eval_start, time.perf_counter())

    review_check_flags = (
        checklist["integration_contract_present"],
        checklist["connector_probe_present"],
        checklist["demo_data_present"],
        checklist["safety_gates_clear"],
        checklist["no_live_trading"],
        checklist["no_order_execution"],
        checklist["no_credentials"],
        checklist["no_network_calls"],
        checklist["no_env_reads"],
        checklist["human_approval_required"],
    )

    safety_summary_start = time.perf_counter()
    safety_summary = {
        "live_trading": bool(unsafe_flags.get("live_trading", False)),
        "order_execution": bool(unsafe_flags.get("order_execution", False)),
        "credentials_read": bool(unsafe_flags.get("credentials_read", False)),
        "env_read": bool(unsafe_flags.get("env_read", False)),
        "network_calls": bool(unsafe_flags.get("network_calls", False)),
        "scheduler_daemon_webhook": bool(
            unsafe_flags.get("scheduler_daemon_webhook", False)
        ),
    }
    safety_summary_ms = _ms(safety_summary_start, time.perf_counter())

    if not decision:
        packet_status = BROKER_DEMO_REVIEW_PACKET_INVALID
    elif decision_value == BROKER_DEMO_DECISION_BLOCKED:
        packet_status = BROKER_DEMO_REVIEW_PACKET_BLOCKED
    elif decision_value == BROKER_DEMO_DECISION_REVIEW_REQUIRED:
        packet_status = BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED
    elif decision_value == BROKER_DEMO_DECISION_READY and ready_value and not any(unsafe_flags.values()):
        packet_status = BROKER_DEMO_REVIEW_PACKET_READY
    elif decision_value == BROKER_DEMO_DECISION_INVALID or not decision_value:
        packet_status = BROKER_DEMO_REVIEW_PACKET_INVALID
    elif any(unsafe_flags.values()):
        packet_status = BROKER_DEMO_REVIEW_PACKET_BLOCKED
    elif any(not flag for flag in review_check_flags):
        packet_status = BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED
    else:
        packet_status = BROKER_DEMO_REVIEW_PACKET_BLOCKED

    packet_build_ms = _ms(start, time.perf_counter())

    return {
        "packet_schema": "AIOS_BROKER_DEMO_REVIEW_PACKET_V5A.v1",
        "packet_status": packet_status,
        "decision": v4_decision,
        "ready": packet_status == BROKER_DEMO_REVIEW_PACKET_READY,
        "blockers": blockers,
        "evidence_summary": evidence_summary,
        "safety_summary": safety_summary,
        "approval_required": True,
        "next_safe_action": _next_safe_action(packet_status),
        "review_checklist": checklist,
        "sanitized_metadata": _sanitize_metadata(dict(metadata or {})),
        "latency_budget": {
                "decision_read_ms": decision_read_ms,
            "packet_build_ms": packet_build_ms,
            "checklist_eval_ms": checklist_eval_ms,
            "safety_summary_ms": safety_summary_ms,
            "network_latency_ms": "excluded_offline_default",
        },
    }


def _extract_unsafe_flags(value: Any) -> dict[str, bool]:
    if not isinstance(value, Mapping):
        return {
            "live_trading": False,
            "order_execution": False,
            "credentials_read": False,
            "env_read": False,
            "network_calls": False,
            "scheduler_daemon_webhook": False,
        }
    return {
        "live_trading": bool(value.get("live_trading", False)),
        "order_execution": bool(value.get("order_execution", False)),
        "credentials_read": bool(value.get("credentials_read", False)),
        "env_read": bool(value.get("env_read", False)),
        "network_calls": bool(value.get("network_calls", False)),
        "scheduler_daemon_webhook": bool(
            value.get("scheduler_daemon_webhook", False)
        ),
    }


def _sanitize_metadata(metadata: Mapping[str, Any] | dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in metadata.items():
        if str(key).strip().lower() in SENSITIVE_METADATA_KEYS:
            continue
        if isinstance(value, Mapping):
            nested = _sanitize_metadata(value)
            if nested:
                sanitized[str(key)] = nested
            continue
        if isinstance(value, list | tuple):
            sanitized[str(key)] = [
                _sanitize_metadata(item)
                if isinstance(item, Mapping)
                else _sanitize_value(item)
                for item in value
            ]
            continue
        sanitized[str(key)] = _sanitize_value(value)
    return sanitized


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, str) and _contains_sensitive_value(value):
        return "[REDACTED]"
    return value


def _contains_sensitive_value(value: str) -> bool:
    lowered = value.lower()
    if "bearer " in lowered:
        return True
    sensitive_markers = (
        "secret",
        "token=",
        "apikey",
        "api_key",
        "refresh_token",
        "access_token",
        "password",
    )
    return any(marker in lowered for marker in sensitive_markers)


def _as_tuple(value: Any) -> tuple[str, ...] | None:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(item) for item in value)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def _ms(start: float, end: float) -> float:
    return (end - start) * 1000.0


def _next_safe_action(packet_status: str) -> str:
    return {
        BROKER_DEMO_REVIEW_PACKET_READY: "human_review_and_approve_protected_demo_progression",
        BROKER_DEMO_REVIEW_PACKET_BLOCKED: "resolve_blockers_before_protected_demo_review",
        BROKER_DEMO_REVIEW_PACKET_INVALID: "repair_missing_or_invalid_broker_demo_decision",
        BROKER_DEMO_REVIEW_PACKET_REVIEW_REQUIRED: "complete_operator_review_and_approve",
    }.get(packet_status, "complete_operator_review_and_approve")
