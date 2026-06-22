"""Protected demo readiness threshold pipeline V7-V9."""

from __future__ import annotations

import time
from typing import Any, Mapping

from automation.forex_engine.broker_demo_rehearsal_runner_v6 import (
    BROKER_DEMO_REHEARSAL_BLOCKED,
    BROKER_DEMO_REHEARSAL_INVALID,
    BROKER_DEMO_REHEARSAL_READY,
    BROKER_DEMO_REHEARSAL_REVIEW_REQUIRED,
)

PROTECTED_DEMO_PREFLIGHT_READY = "PROTECTED_DEMO_PREFLIGHT_READY"
PROTECTED_DEMO_PREFLIGHT_BLOCKED = "PROTECTED_DEMO_PREFLIGHT_BLOCKED"
PROTECTED_DEMO_PREFLIGHT_INVALID = "PROTECTED_DEMO_PREFLIGHT_INVALID"
PROTECTED_DEMO_PREFLIGHT_REVIEW_REQUIRED = "PROTECTED_DEMO_PREFLIGHT_REVIEW_REQUIRED"

PROTECTED_DEMO_READONLY_CONTROLLER_READY = "PROTECTED_DEMO_READONLY_CONTROLLER_READY"
PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED = "PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED"
PROTECTED_DEMO_READONLY_CONTROLLER_INVALID = "PROTECTED_DEMO_READONLY_CONTROLLER_INVALID"
PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED = (
    "PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED"
)

DEMO_MICRO_TRADE_PACKET_READY = "DEMO_MICRO_TRADE_PACKET_READY"
DEMO_MICRO_TRADE_PACKET_BLOCKED = "DEMO_MICRO_TRADE_PACKET_BLOCKED"
DEMO_MICRO_TRADE_PACKET_INVALID = "DEMO_MICRO_TRADE_PACKET_INVALID"
DEMO_MICRO_TRADE_PACKET_REVIEW_REQUIRED = "DEMO_MICRO_TRADE_PACKET_REVIEW_REQUIRED"

REQUIRED_CONNECTION_FIELDS = (
    "operator_approved",
    "demo_only",
    "simulation_or_preflight_only",
    "network_requested",
    "credentials_supplied_runtime_only",
    "credentials_persisted",
    "account_id_persisted",
    "endpoint_classification",
    "order_execution_requested",
    "read_only_requested",
)

REQUIRED_RUNTIME_AUTH_FIELDS = (
    "explicit_operator_runtime_approval",
    "allow_demo_network_once",
    "read_only_scope_only",
    "no_order_scope_ack",
    "credentials_runtime_only_ack",
    "no_secret_persistence_ack",
)

REQUIRED_APPROVAL_FIELDS = (
    "human_approved_demo_micro_trade",
    "single_trade_only",
    "micro_size_ack",
    "no_live_trade_ack",
    "demo_only_ack",
)


def evaluate_protected_demo_connection_preflight(
    rehearsal_result: Mapping[str, Any] | None,
    connection_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    packet_start = time.perf_counter()
    result = dict(rehearsal_result or {})
    packet_read_ms = _ms(packet_start, time.perf_counter())

    request = dict(connection_request or {})
    request_eval_start = time.perf_counter()
    request_flags = {
        key: bool(request.get(key, False))
        for key in REQUIRED_CONNECTION_FIELDS
        if key != "endpoint_classification"
    }
    request_eval_ms = _ms(request_eval_start, time.perf_counter())

    endpoint_classification = str(request.get("endpoint_classification", "")).upper()
    request_flags["endpoint_is_practice_demo"] = endpoint_classification == "PRACTICE_DEMO"
    request_flags["endpoint_is_live"] = endpoint_classification == "LIVE"
    request_flags["endpoint_is_unknown"] = endpoint_classification == "UNKNOWN"

    rehearsal_status = str(result.get("rehearsal_status", ""))
    rehearsal_ready = bool(result.get("ready", False))
    rehearsal_schema = result.get("rehearsal_schema")
    safety_gate_start = time.perf_counter()
    safety_summary = {
        "live_trading": False,
        "order_execution": False,
        "credentials_read": bool(result.get("safety_summary", {}).get("credentials_read", False)),
        "env_read": False,
        "network_calls": bool(request.get("network_requested", False)),
        "scheduler_daemon_webhook": False,
        "raw_broker_payload_persisted": False,
        "account_id_present": bool(request.get("account_id_persisted", False)),
    }
    safety_gate_eval_ms = _ms(safety_gate_start, time.perf_counter())

    mapping_start = time.perf_counter()
    blockers: list[str] = []

    if not rehearsal_result:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_INVALID
    elif not rehearsal_schema:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_INVALID
        blockers.append("rehearsal_schema_missing")
    elif rehearsal_status == BROKER_DEMO_REHEARSAL_INVALID:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_INVALID
    elif not rehearsal_ready:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_INVALID
    elif not request.get("operator_approved", False):
        preflight_status = PROTECTED_DEMO_PREFLIGHT_REVIEW_REQUIRED
        blockers.append("operator_approval_missing")
    elif request_flags["demo_only"] is not True:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("demo_only_required")
    elif request_flags["simulation_or_preflight_only"] is not True:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("simulation_or_preflight_only_required")
    elif request.get("credentials_persisted") is True:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("credentials_persisted_blocked")
    elif request.get("account_id_persisted") is True:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("account_id_persisted_blocked")
    elif request.get("order_execution_requested") is True:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("order_execution_requested_blocked")
    elif request_flags["endpoint_is_live"] or request_flags["endpoint_is_unknown"]:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("endpoint_not_practice_demo")
    elif request.get("network_requested") is True and not request.get("operator_approved", False):
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("network_requested_without_operator_approval")
    elif request_flags["read_only_requested"] is not True:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_BLOCKED
        blockers.append("read_only_scope_required")
    else:
        preflight_status = PROTECTED_DEMO_PREFLIGHT_READY
    preflight_mapping_ms = _ms(mapping_start, time.perf_counter())

    return {
        "preflight_schema": "AIOS_BROKER_DEMO_PREFLIGHT_V7_V9.v1",
        "preflight_status": preflight_status,
        "ready": preflight_status == PROTECTED_DEMO_PREFLIGHT_READY,
        "blockers": tuple(blockers),
        "request_evaluation": {
            "operator_approved": bool(request.get("operator_approved", False)),
            "demo_only": bool(request.get("demo_only", False)),
            "simulation_or_preflight_only": bool(
                request.get("simulation_or_preflight_only", False)
            ),
            "network_requested": bool(request.get("network_requested", False)),
            "endpoint_classification": endpoint_classification,
            "read_only_requested": bool(request.get("read_only_requested", False)),
            "credentials_supplied_runtime_only": bool(
                request.get("credentials_supplied_runtime_only", False)
            ),
            "credentials_persisted": bool(request.get("credentials_persisted", False)),
            "account_id_persisted": bool(request.get("account_id_persisted", False)),
            "order_execution_requested": bool(request.get("order_execution_requested", False)),
        },
        "safety_summary": safety_summary,
        "next_safe_action": _preflight_next_safe_action(preflight_status),
        "latency_budget": {
            "rehearsal_read_ms": packet_read_ms,
            "request_eval_ms": request_eval_ms,
            "safety_gate_eval_ms": safety_gate_eval_ms,
            "preflight_mapping_ms": preflight_mapping_ms,
            "network_latency_ms": "excluded_offline_default",
        },
    }


def build_protected_demo_readonly_attempt_controller(
    preflight: Mapping[str, Any] | None,
    runtime_authorization: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    preflight_start = time.perf_counter()
    preflight_payload = dict(preflight or {})
    preflight_read_ms = _ms(preflight_start, time.perf_counter())

    auth = dict(runtime_authorization or {})
    auth_eval_start = time.perf_counter()
    auth_flags = {key: bool(auth.get(key, False)) for key in REQUIRED_RUNTIME_AUTH_FIELDS}
    auth_eval_ms = _ms(auth_eval_start, time.perf_counter())

    safety_gate_start = time.perf_counter()
    safety_summary = {
        "live_trading": False,
        "order_execution": False,
        "credentials_read": False,
        "env_read": False,
        "network_calls": False,
        "scheduler_daemon_webhook": False,
        "raw_broker_payload_persisted": False,
        "account_id_present": False,
    }
    safety_gate_eval_ms = _ms(safety_gate_start, time.perf_counter())

    mapping_start = time.perf_counter()
    preflight_ready = bool(preflight_payload.get("ready", False))
    preflight_status = str(preflight_payload.get("preflight_status", ""))
    blockers: list[str] = []

    if not preflight:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_INVALID
    elif preflight_status not in {PROTECTED_DEMO_PREFLIGHT_READY} or not preflight_ready:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_INVALID
        blockers.append("preflight_not_ready")
    elif not runtime_authorization:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED
        blockers.append("runtime_authorization_missing")
    elif not auth_flags["allow_demo_network_once"]:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
        blockers.append("demo_network_once_not_authorized")
    elif not auth_flags["read_only_scope_only"]:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
        blockers.append("read_only_scope_not_authorized")
    elif not auth_flags["no_order_scope_ack"]:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
        blockers.append("no_order_scope_not_acknowledged")
    elif not auth_flags["credentials_runtime_only_ack"]:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
        blockers.append("runtime_credentials_ack_missing")
    elif not auth_flags["no_secret_persistence_ack"]:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED
        blockers.append("secret_persistence_ack_missing")
    elif not auth_flags["explicit_operator_runtime_approval"]:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED
        blockers.append("explicit_operator_runtime_approval_missing")
    else:
        controller_status = PROTECTED_DEMO_READONLY_CONTROLLER_READY
    controller_mapping_ms = _ms(mapping_start, time.perf_counter())

    sanitized_connection_plan = {
        "plan_schema": "AIOS_BROKER_DEMO_READONLY_CONTROLLER_PLAN_V8.v1",
        "broker_scope": "OANDA_DEMO_PROTECTED_READONLY",
        "endpoint_classification": str(preflight_payload.get("request_evaluation", {}).get("endpoint_classification", "PRACTICE_DEMO")),
        "approval_required": True,
        "allow_demo_network_once": auth_flags["allow_demo_network_once"],
        "read_only_scope_only": auth_flags["read_only_scope_only"],
        "no_order_scope_ack": auth_flags["no_order_scope_ack"],
        "credentials_runtime_only_ack": auth_flags["credentials_runtime_only_ack"],
        "no_secret_persistence_ack": auth_flags["no_secret_persistence_ack"],
        "explicit_operator_runtime_approval": auth_flags["explicit_operator_runtime_approval"],
        "will_execute_network": auth_flags["allow_demo_network_once"] and auth_flags["explicit_operator_runtime_approval"],
        "will_execute_order": False,
        "will_read_credentials": False,
        "will_persist_account_id": False,
    }

    return {
        "controller_schema": "AIOS_BROKER_DEMO_READONLY_CONTROLLER_V8.v1",
        "controller_status": controller_status,
        "ready": controller_status == PROTECTED_DEMO_READONLY_CONTROLLER_READY,
        "blockers": tuple(blockers),
        "sanitized_connection_plan": sanitized_connection_plan,
        "safety_summary": safety_summary,
        "next_safe_action": _controller_next_safe_action(controller_status),
        "latency_budget": {
            "preflight_read_ms": preflight_read_ms,
            "runtime_auth_eval_ms": auth_eval_ms,
            "safety_gate_eval_ms": safety_gate_eval_ms,
            "controller_mapping_ms": controller_mapping_ms,
            "network_latency_ms": "excluded_offline_default",
        },
        "total_ms": _ms(start, time.perf_counter()),
    }


def build_demo_micro_trade_approval_packet(
    controller: Mapping[str, Any] | None,
    trade_candidate: Mapping[str, Any] | None = None,
    approval: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    controller_start = time.perf_counter()
    controller_payload = dict(controller or {})
    controller_read_ms = _ms(controller_start, time.perf_counter())

    trade = dict(trade_candidate or {})
    approval_payload = dict(approval or {})
    trade_eval_start = time.perf_counter()
    trade_snapshot = {
        "instrument": trade.get("instrument", ""),
        "side": trade.get("side", ""),
        "units": trade.get("units", 0),
        "risk_cap": trade.get("risk_cap", 0),
        "stop_loss_placeholder": trade.get("stop_loss_placeholder", None),
        "take_profit_placeholder": trade.get("take_profit_placeholder", None),
        "max_loss_gate_clear": bool(trade.get("max_loss_gate_clear", False)),
        "daily_stop_clear": bool(trade.get("daily_stop_clear", False)),
        "kill_switch_enabled": bool(trade.get("kill_switch_enabled", False)),
        "simulation_only": bool(trade.get("simulation_only", False)),
        "broker_demo_only": bool(trade.get("broker_demo_only", False)),
    }
    approval_flags = {key: bool(approval_payload.get(key, False)) for key in REQUIRED_APPROVAL_FIELDS}
    trade_eval_ms = _ms(trade_eval_start, time.perf_counter())

    safety_gate_start = time.perf_counter()
    safety_summary = {
        "live_trading": False,
        "order_execution": False,
        "credentials_read": False,
        "env_read": False,
        "network_calls": False,
        "scheduler_daemon_webhook": False,
    }
    safety_gate_eval_ms = _ms(safety_gate_start, time.perf_counter())

    mapping_start = time.perf_counter()
    controller_ready = bool(controller_payload.get("ready", False))
    controller_status = str(controller_payload.get("controller_status", ""))
    blockers: list[str] = []

    if not controller or controller_status not in {PROTECTED_DEMO_READONLY_CONTROLLER_READY} or not controller_ready:
        packet_status = DEMO_MICRO_TRADE_PACKET_INVALID
        blockers.append("controller_not_ready")
    elif not approval_payload:
        packet_status = DEMO_MICRO_TRADE_PACKET_REVIEW_REQUIRED
        blockers.append("approval_missing")
    elif trade_snapshot["kill_switch_enabled"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("kill_switch_enabled")
    elif not trade_snapshot["max_loss_gate_clear"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("max_loss_gate_blocked")
    elif not trade_snapshot["daily_stop_clear"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("daily_stop_blocked")
    elif not trade_snapshot["simulation_only"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("simulation_only_required")
    elif not trade_snapshot["broker_demo_only"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("broker_demo_only_required")
    elif not approval_flags["human_approved_demo_micro_trade"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("human_demo_micro_trade_not_approved")
    elif not approval_flags["single_trade_only"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("single_trade_scope_required")
    elif not approval_flags["micro_size_ack"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("micro_size_not_acknowledged")
    elif not approval_flags["no_live_trade_ack"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("no_live_trade_not_acknowledged")
    elif not approval_flags["demo_only_ack"]:
        packet_status = DEMO_MICRO_TRADE_PACKET_BLOCKED
        blockers.append("demo_only_ack_required")
    else:
        packet_status = DEMO_MICRO_TRADE_PACKET_READY
    packet_mapping_ms = _ms(mapping_start, time.perf_counter())

    sanitized_trade_intent = _sanitize_trade_intent(trade)

    return {
        "packet_schema": "AIOS_BROKER_DEMO_MICRO_TRADE_PACKET_V9.v1",
        "packet_status": packet_status,
        "ready": packet_status == DEMO_MICRO_TRADE_PACKET_READY,
        "blockers": tuple(blockers),
        "sanitized_trade_intent": sanitized_trade_intent,
        "approval_summary": {
            "human_approved_demo_micro_trade": approval_flags["human_approved_demo_micro_trade"],
            "single_trade_only": approval_flags["single_trade_only"],
            "micro_size_ack": approval_flags["micro_size_ack"],
            "no_live_trade_ack": approval_flags["no_live_trade_ack"],
            "demo_only_ack": approval_flags["demo_only_ack"],
        },
        "safety_summary": safety_summary,
        "next_safe_action": _trade_packet_next_safe_action(packet_status),
        "latency_budget": {
            "controller_read_ms": controller_read_ms,
            "trade_eval_ms": trade_eval_ms,
            "safety_gate_eval_ms": safety_gate_eval_ms,
            "packet_mapping_ms": packet_mapping_ms,
            "network_latency_ms": "excluded_offline_default",
        },
        "total_ms": _ms(start, time.perf_counter()),
    }


def _sanitize_trade_intent(trade_candidate: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(trade_candidate, Mapping):
        return {}

    prohibited = {
        "access_token",
        "api_key",
        "apikey",
        "token",
        "secret",
        "password",
        "credential",
        "account_id",
        "account_number",
        "broker_order_id",
        "raw_payload",
        "raw_request",
        "raw_response",
        "environment",
        "endpoint_url",
        "live_route",
    }
    sanitized: dict[str, Any] = {}
    for key, value in trade_candidate.items():
        if str(key).strip().lower() in prohibited:
            continue
        sanitized[str(key)] = value
    return sanitized


def _preflight_next_safe_action(status: str) -> str:
    return {
        PROTECTED_DEMO_PREFLIGHT_READY: "prepare_protected_readonly_attempt_controller",
        PROTECTED_DEMO_PREFLIGHT_BLOCKED: "resolve_connection_preflight_blockers",
        PROTECTED_DEMO_PREFLIGHT_INVALID: "repair_rehearsal_result",
        PROTECTED_DEMO_PREFLIGHT_REVIEW_REQUIRED: "obtain_operator_preflight_approval",
    }.get(status, "obtain_operator_preflight_approval")


def _controller_next_safe_action(status: str) -> str:
    return {
        PROTECTED_DEMO_READONLY_CONTROLLER_READY: "execute_explicit_readonly_demo_connection_in_separate_authorized_runtime",
        PROTECTED_DEMO_READONLY_CONTROLLER_BLOCKED: "resolve_readonly_controller_blockers",
        PROTECTED_DEMO_READONLY_CONTROLLER_INVALID: "repair_preflight",
        PROTECTED_DEMO_READONLY_CONTROLLER_REVIEW_REQUIRED: "obtain_runtime_authorization",
    }.get(status, "obtain_runtime_authorization")


def _trade_packet_next_safe_action(status: str) -> str:
    return {
        DEMO_MICRO_TRADE_PACKET_READY: "await_explicit_operator_command_for_demo_micro_trade_execution",
        DEMO_MICRO_TRADE_PACKET_BLOCKED: "resolve_demo_micro_trade_packet_blockers",
        DEMO_MICRO_TRADE_PACKET_INVALID: "repair_controller_or_trade_candidate",
        DEMO_MICRO_TRADE_PACKET_REVIEW_REQUIRED: "obtain_demo_micro_trade_human_approval",
    }.get(status, "obtain_demo_micro_trade_human_approval")


def _ms(start: float, end: float) -> float:
    return (end - start) * 1000.0

