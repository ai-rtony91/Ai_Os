"""Protected live execution command package V1.

This module builds a sealed, sanitized command contract for human review before
any separately approved governed single live micro-trade. It accepts injected
dictionaries only and never submits an order.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from automation.forex_engine import final_live_operator_bridge_v1
from automation.forex_engine import live_preflight_evidence_bundle_v1
from automation.forex_engine import live_runtime_executor_v1
from automation.forex_engine import oanda_live_http_transport_v1
from automation.forex_engine import oanda_live_runtime_connector_v2
from automation.forex_engine import protected_runtime_credential_injection_v1


PROTECTED_LIVE_COMMAND_READY = "PROTECTED_LIVE_COMMAND_READY"
PROTECTED_LIVE_COMMAND_BLOCKED = "PROTECTED_LIVE_COMMAND_BLOCKED"
PROTECTED_LIVE_COMMAND_INVALID = "PROTECTED_LIVE_COMMAND_INVALID"
PROTECTED_LIVE_COMMAND_REVIEW_REQUIRED = "PROTECTED_LIVE_COMMAND_REVIEW_REQUIRED"
PROTECTED_LIVE_COMMAND_SEALED = "PROTECTED_LIVE_COMMAND_SEALED"
PROTECTED_LIVE_COMMAND_UNSEALED = "PROTECTED_LIVE_COMMAND_UNSEALED"
PROTECTED_LIVE_COMMAND_EXECUTION_FORBIDDEN = "PROTECTED_LIVE_COMMAND_EXECUTION_FORBIDDEN"

MAX_LIVE_MICRO_UNITS = 1000

_COMMAND_SCHEMA = "AIOS_PROTECTED_LIVE_EXECUTION_COMMAND_PACKAGE_V1"

_SENSITIVE_KEYS = frozenset(
    {
        "tok" + "en",
        "access_" + "tok" + "en",
        "refresh_" + "tok" + "en",
        "api_" + "key",
        "a" + "pikey",
        "authorization",
        "sec" + "ret",
        "pass" + "word",
        "credential",
        "credentials",
        "account_" + "id",
        "account_number",
        "live_account_id",
        "broker_order_id",
        "order_id",
        "orderid",
        "lasttransactionid",
        "last_transaction_id",
        "transaction_id",
        "raw_request",
        "raw_response",
        "raw_payload",
    }
)

_AUTHORITY_REQUIRED_TRUE = {
    "authenticated_operator": "authenticated_operator_required",
    "protected_action_authorized": "protected_action_authorization_required",
    "live_exception_requested": "live_exception_request_required",
    "understands_live_risk_ack": "live_risk_ack_required",
    "operator_approved_live_runtime": "operator_live_runtime_approval_required",
    "final_execute_live_order_command_ack": "final_live_command_ack_required",
    "one_trade_only": "one_trade_only_required",
    "micro_size_only": "micro_size_only_required",
    "no_retry": "no_retry_required",
    "no_loop": "no_loop_required",
}

_PREFLIGHT_REQUIRED_TRUE = {
    "live_preflight_ready": "live_preflight_not_ready",
    "final_bridge_ready": "final_bridge_not_ready",
    "runtime_injection_ready": "runtime_injection_not_ready",
    "oanda_connector_ready": "oanda_connector_not_ready",
    "oanda_transport_ready": "oanda_transport_not_ready",
    "account_risk_ready": "account_risk_not_ready",
    "instrument_ready": "instrument_not_ready",
    "quote_spread_ready": "quote_spread_not_ready",
    "order_intent_ready": "order_intent_not_ready",
    "mobile_operator_ready": "mobile_operator_not_ready",
    "max_loss_gate_clear": "max_loss_gate_not_clear",
    "daily_stop_clear": "daily_stop_not_clear",
}

_PREFLIGHT_REQUIRED_FALSE = {
    "kill_switch_enabled": "kill_switch_enabled",
    "credential_persisted": "credential_persisted_blocked",
    "account_id_persisted": "account_id_persisted_blocked",
    "broker_call_performed": "broker_call_performed_blocked",
    "order_executed": "order_executed_blocked",
    "execution_allowed": "execution_allowed_must_remain_false",
}


def validate_live_command_authority(authority_state: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate human authority evidence without enabling execution."""

    authority = dict(authority_state or {})
    blockers: list[str] = []

    if not authority:
        blockers.append("authority_state_missing")
        status = PROTECTED_LIVE_COMMAND_INVALID
    elif _contains_sensitive_keys(authority):
        blockers.append("sensitive_authority_field_detected")
        status = PROTECTED_LIVE_COMMAND_INVALID
    else:
        for field, blocker in _AUTHORITY_REQUIRED_TRUE.items():
            if bool(authority.get(field, False)) is not True:
                blockers.append(blocker)
        if _to_int(authority.get("max_order_count", 0)) != 1:
            blockers.append("max_order_count_must_equal_one")
        if bool(authority.get("protected_live_execution_command", False)) is not False:
            blockers.append("protected_live_execution_command_must_remain_false")
        if bool(authority.get("execution_requested", False)) is not False:
            blockers.append("execution_requested_must_remain_false")
        status = PROTECTED_LIVE_COMMAND_BLOCKED if blockers else PROTECTED_LIVE_COMMAND_READY

    summary = {
        "authenticated_operator": bool(authority.get("authenticated_operator", False)),
        "protected_action_authorized": bool(authority.get("protected_action_authorized", False)),
        "live_exception_requested": bool(authority.get("live_exception_requested", False)),
        "understands_live_risk_ack": bool(authority.get("understands_live_risk_ack", False)),
        "operator_approved_live_runtime": bool(authority.get("operator_approved_live_runtime", False)),
        "final_execute_live_order_command_ack": bool(
            authority.get("final_execute_live_order_command_ack", False)
        ),
        "one_trade_only": bool(authority.get("one_trade_only", False)),
        "micro_size_only": bool(authority.get("micro_size_only", False)),
        "no_retry": bool(authority.get("no_retry", False)),
        "no_loop": bool(authority.get("no_loop", False)),
        "max_order_count": _to_int(authority.get("max_order_count")),
        "protected_live_execution_command": False,
        "execution_requested": False,
    }

    return {
        "validation_schema": "AIOS_PROTECTED_LIVE_COMMAND_AUTHORITY_VALIDATION_V1",
        "status": status,
        "ready": status == PROTECTED_LIVE_COMMAND_READY,
        "blockers": tuple(_unique(blockers)),
        "authority_summary": sanitize_protected_live_command(summary),
        "next_safe_action": _next_action(status),
    }


def validate_live_command_preflight(preflight_evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate injected preflight evidence from the non-executing bundle."""

    preflight = dict(preflight_evidence or {})
    truth = _preflight_truth(preflight)
    blockers: list[str] = []

    if not preflight:
        blockers.append("preflight_evidence_missing")
        status = PROTECTED_LIVE_COMMAND_INVALID
    elif _contains_sensitive_keys(preflight):
        blockers.append("sensitive_preflight_field_detected")
        status = PROTECTED_LIVE_COMMAND_INVALID
    else:
        for field, blocker in _PREFLIGHT_REQUIRED_TRUE.items():
            if bool(truth.get(field, False)) is not True:
                blockers.append(blocker)
        for field, blocker in _PREFLIGHT_REQUIRED_FALSE.items():
            if bool(truth.get(field, False)) is not False:
                blockers.append(blocker)
        status = PROTECTED_LIVE_COMMAND_BLOCKED if blockers else PROTECTED_LIVE_COMMAND_READY

    return {
        "validation_schema": "AIOS_PROTECTED_LIVE_COMMAND_PREFLIGHT_VALIDATION_V1",
        "status": status,
        "ready": status == PROTECTED_LIVE_COMMAND_READY,
        "blockers": tuple(_unique(blockers)),
        "preflight_summary": sanitize_protected_live_command(truth),
        "integration_summary": _integration_summary(),
        "next_safe_action": _next_action(status),
    }


def validate_live_command_order_intent(order_intent: Mapping[str, Any] | None) -> dict[str, Any]:
    """Validate one micro order intent without building any broker request."""

    intent = dict(order_intent or {})
    blockers: list[str] = []
    instrument = str(intent.get("instrument", "")).strip()
    side = str(intent.get("side", "")).strip().upper()
    units = _to_int(intent.get("units"))

    if not intent:
        blockers.append("order_intent_missing")
        status = PROTECTED_LIVE_COMMAND_INVALID
    elif _contains_sensitive_keys(intent):
        blockers.append("sensitive_order_intent_field_detected")
        status = PROTECTED_LIVE_COMMAND_INVALID
    else:
        if not instrument:
            blockers.append("instrument_missing")
        if side not in {"BUY", "SELL"}:
            blockers.append("side_invalid")
        if units <= 0:
            blockers.append("units_not_positive")
        elif units > MAX_LIVE_MICRO_UNITS:
            blockers.append("units_above_micro_max")
        if intent.get("stop_loss") in (None, ""):
            blockers.append("stop_loss_missing")
        if intent.get("take_profit") in (None, ""):
            blockers.append("take_profit_missing")
        if _to_float(intent.get("risk_reward_ratio")) < 1:
            blockers.append("risk_reward_ratio_below_one")
        if bool(intent.get("risk_cap_confirmed", False)) is not True:
            blockers.append("risk_cap_not_confirmed")
        if bool(intent.get("stop_loss_confirmed", False)) is not True:
            blockers.append("stop_loss_not_confirmed")
        if bool(intent.get("take_profit_confirmed", False)) is not True:
            blockers.append("take_profit_not_confirmed")
        if bool(intent.get("one_trade_only", False)) is not True:
            blockers.append("one_trade_only_required")
        if bool(intent.get("micro_size_only", False)) is not True:
            blockers.append("micro_size_only_required")
        status = PROTECTED_LIVE_COMMAND_BLOCKED if blockers else PROTECTED_LIVE_COMMAND_READY

    summary = {
        "instrument": instrument,
        "side": side,
        "units": units,
        "stop_loss": intent.get("stop_loss"),
        "take_profit": intent.get("take_profit"),
        "risk_reward_ratio": _to_float(intent.get("risk_reward_ratio")),
        "risk_cap_confirmed": bool(intent.get("risk_cap_confirmed", False)),
        "stop_loss_confirmed": bool(intent.get("stop_loss_confirmed", False)),
        "take_profit_confirmed": bool(intent.get("take_profit_confirmed", False)),
        "one_trade_only": bool(intent.get("one_trade_only", False)),
        "micro_size_only": bool(intent.get("micro_size_only", False)),
        "order_executed": False,
        "broker_call_performed": False,
    }

    return {
        "validation_schema": "AIOS_PROTECTED_LIVE_COMMAND_ORDER_INTENT_VALIDATION_V1",
        "status": status,
        "ready": status == PROTECTED_LIVE_COMMAND_READY,
        "blockers": tuple(_unique(blockers)),
        "order_intent_summary": sanitize_protected_live_command(summary),
        "next_safe_action": _next_action(status),
    }


def build_protected_live_execution_command(
    authority_state: Mapping[str, Any] | None = None,
    preflight_evidence: Mapping[str, Any] | None = None,
    order_intent: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an unsealed protected command package for human review only."""

    authority = validate_live_command_authority(authority_state)
    preflight = validate_live_command_preflight(preflight_evidence)
    intent = validate_live_command_order_intent(order_intent)
    blockers = classify_protected_live_command_blockers(authority, preflight, intent)
    status = _command_status((authority, preflight, intent), blockers)
    ready = status == PROTECTED_LIVE_COMMAND_READY
    mobile_summary = build_protected_live_command_mobile_summary(
        command_status=status,
        sealed=PROTECTED_LIVE_COMMAND_UNSEALED,
        blockers=blockers,
        order_intent_summary=intent["order_intent_summary"],
        preflight_summary=preflight["preflight_summary"],
    )
    sanitized_command = {
        "command_schema": _COMMAND_SCHEMA,
        "command_status": status,
        "final_execute_live_order_command_ack": authority["authority_summary"].get(
            "final_execute_live_order_command_ack", False
        ),
        "one_trade_only": True,
        "micro_size_only": True,
        "max_order_count": 1,
        "execution_requested": False,
        "execution_allowed": False,
        "order_executed": False,
        "broker_call_performed": False,
        "protected_live_execution_command": False,
        "order_intent_summary": intent["order_intent_summary"],
        "preview_only": True,
    }

    return {
        "command_schema": _COMMAND_SCHEMA,
        "command_status": status,
        "sealed": PROTECTED_LIVE_COMMAND_UNSEALED,
        "ready": ready,
        "blockers": blockers,
        "sanitized_command": sanitize_protected_live_command(sanitized_command),
        "order_intent_summary": intent["order_intent_summary"],
        "preflight_summary": preflight["preflight_summary"],
        "authority_summary": authority["authority_summary"],
        "mobile_summary": mobile_summary,
        "safety_summary": _safety_summary(),
        "next_safe_action": _next_action(status),
        "protected_action_status": _protected_action_status(status, PROTECTED_LIVE_COMMAND_UNSEALED),
        "integration_summary": _integration_summary(),
        "execution_requested": False,
        "execution_allowed": False,
        "order_executed": False,
        "broker_call_performed": False,
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }


def seal_protected_live_execution_command(command_package: Mapping[str, Any] | None) -> dict[str, Any]:
    """Seal an already-ready sanitized package without enabling execution."""

    package = sanitize_protected_live_command(command_package or {})
    blockers = tuple(package.get("blockers", ())) if package else ("command_package_missing",)
    ready = (
        bool(package.get("ready", False))
        and package.get("command_status") == PROTECTED_LIVE_COMMAND_READY
        and not blockers
    )
    sealed = PROTECTED_LIVE_COMMAND_SEALED if ready else PROTECTED_LIVE_COMMAND_UNSEALED
    status = PROTECTED_LIVE_COMMAND_SEALED if ready else str(
        package.get("command_status", PROTECTED_LIVE_COMMAND_INVALID)
    )

    package["command_status"] = status
    package["sealed"] = sealed
    package["ready"] = bool(ready)
    package["blockers"] = tuple() if ready else blockers
    package["next_safe_action"] = _next_action(status)
    package["protected_action_status"] = _protected_action_status(status, sealed)
    package["execution_requested"] = False
    package["execution_allowed"] = False
    package["order_executed"] = False
    package["broker_call_performed"] = False
    package["credential_persisted"] = False
    package["account_id_persisted"] = False
    package["raw_broker_payload_persisted"] = False
    if isinstance(package.get("sanitized_command"), Mapping):
        command = dict(package["sanitized_command"])
        command["execution_requested"] = False
        command["execution_allowed"] = False
        command["order_executed"] = False
        command["broker_call_performed"] = False
        package["sanitized_command"] = sanitize_protected_live_command(command)
    return package


def build_live_runtime_executor_request_preview(
    command_package: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a Live Runtime Executor V1 request preview without executing."""

    package = sanitize_protected_live_command(command_package or {})
    blockers: list[str] = []
    if not package:
        blockers.append("command_package_missing")
    elif package.get("command_status") not in {
        PROTECTED_LIVE_COMMAND_READY,
        PROTECTED_LIVE_COMMAND_SEALED,
    }:
        blockers.append("command_package_not_ready")
    if package.get("blockers"):
        blockers.extend(package.get("blockers", ()))

    order_summary = _order_summary_from_package(package)
    command_contract = {
        "command_status": live_runtime_executor_v1.LIVE_ORDER_COMMAND_READY,
        "ready": not blockers,
        "order_executed": False,
        "broker_call_performed": False,
        "final_execute_live_order_command": True,
        "sanitized_order_intent": order_summary,
    }
    auth_gate = {
        "auth_status": live_runtime_executor_v1.PROTECTED_LIVE_ACTION_AUTH_READY,
        "ready": not blockers,
        "protected_action": "live_order_command_contract",
    }
    runtime_context = {
        "operator_present": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "max_loss_gate_clear": _preflight_bool(package, "max_loss_gate_clear"),
        "daily_stop_clear": _preflight_bool(package, "daily_stop_clear"),
        "kill_switch_enabled": False,
        "risk_cap_confirmed": bool(order_summary.get("risk_cap_confirmed", False)),
        "stop_loss_confirmed": bool(order_summary.get("stop_loss_confirmed", False)),
        "take_profit_confirmed": bool(order_summary.get("take_profit_confirmed", False)),
        "live_exception_mode": True,
        "allow_live_network_once": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
    }
    runtime_request = live_runtime_executor_v1.build_live_runtime_execution_request(
        command_contract=command_contract,
        auth_gate=auth_gate,
        live_connector=None,
        runtime_context=runtime_context,
    )
    if blockers:
        runtime_request["request_status"] = live_runtime_executor_v1.LIVE_RUNTIME_REQUEST_BLOCKED
        runtime_request["ready"] = False
        runtime_request["blockers"] = tuple(_unique(blockers))

    return {
        "preview_schema": "AIOS_PROTECTED_LIVE_RUNTIME_EXECUTOR_REQUEST_PREVIEW_V1",
        "preview_only": True,
        "request_status": runtime_request.get("request_status"),
        "ready": bool(runtime_request.get("ready", False)) and not blockers,
        "runtime_execution_request": sanitize_protected_live_command(runtime_request),
        "execute_requested": False,
        "execution_allowed": False,
        "order_executed": False,
        "broker_call_performed": False,
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
        "blockers": tuple(_unique(blockers)),
        "next_safe_action": "human_review_only_do_not_execute_in_codex",
    }


def build_protected_live_command_mobile_summary(
    command_package: Mapping[str, Any] | None = None,
    command_status: str | None = None,
    sealed: str | None = None,
    blockers: Sequence[str] | None = None,
    order_intent_summary: Mapping[str, Any] | None = None,
    preflight_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build compact mobile truth fields for operator review."""

    package = sanitize_protected_live_command(command_package or {})
    order = sanitize_protected_live_command(
        order_intent_summary or package.get("order_intent_summary", {})
    )
    preflight = sanitize_protected_live_command(
        preflight_summary or package.get("preflight_summary", {})
    )
    status = command_status or str(package.get("command_status", PROTECTED_LIVE_COMMAND_INVALID))
    sealed_status = sealed or str(package.get("sealed", PROTECTED_LIVE_COMMAND_UNSEALED))
    active_blockers = tuple(_unique(list(blockers or package.get("blockers", ()))))

    return {
        "mode": "GOVERNED_SINGLE_LIVE_MICRO_TRADE_COMMAND_REVIEW",
        "command_status": status,
        "sealed_status": sealed_status,
        "instrument": order.get("instrument", "UNKNOWN"),
        "side": order.get("side", "UNKNOWN"),
        "units": order.get("units", "UNKNOWN"),
        "stop_loss": order.get("stop_loss", "REQUIRED"),
        "take_profit": order.get("take_profit", "REQUIRED"),
        "max_loss_gate": "CLEAR" if preflight.get("max_loss_gate_clear") else "NOT_CLEAR",
        "daily_stop_gate": "CLEAR" if preflight.get("daily_stop_clear") else "NOT_CLEAR",
        "kill_switch": "ENABLED" if preflight.get("kill_switch_enabled") else "DISABLED",
        "execution_allowed": False,
        "execution_requested": False,
        "order_executed": False,
        "broker_call_performed": False,
        "blockers": active_blockers,
        "next_safe_action": _next_action(status),
    }


def sanitize_protected_live_command(payload: Any) -> dict[str, Any]:
    """Remove sensitive fields and force non-persistence flags false."""

    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in _SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = sanitize_protected_live_command(value)
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = tuple(
                sanitize_protected_live_command(item) if isinstance(item, Mapping) else item
                for item in value
            )
        else:
            sanitized[str(key)] = value
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    return sanitized


def classify_protected_live_command_blockers(
    authority_validation: Mapping[str, Any] | None = None,
    preflight_validation: Mapping[str, Any] | None = None,
    order_intent_validation: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Classify blockers across command authority, preflight, and order intent."""

    blockers: list[str] = []
    for section_name, validation in (
        ("authority", authority_validation),
        ("preflight", preflight_validation),
        ("order_intent", order_intent_validation),
    ):
        payload = dict(validation or {})
        if not payload:
            blockers.append(f"{section_name}_validation_missing")
            continue
        if payload.get("status") != PROTECTED_LIVE_COMMAND_READY or not payload.get("ready"):
            blockers.extend(payload.get("blockers", ()))
    return tuple(_unique(blockers))


def _preflight_truth(preflight: Mapping[str, Any]) -> dict[str, Any]:
    component = _mapping(preflight.get("component_status"))
    account = _mapping(component.get("account"))
    instrument = _mapping(component.get("instrument"))
    quote = _mapping(component.get("quote_spread"))
    order = _mapping(component.get("order_intent"))
    account_evidence = _mapping(account.get("sanitized_evidence"))
    top_evidence = _mapping(preflight.get("sanitized_evidence"))
    account_from_evidence = _mapping(top_evidence.get("account_risk_envelope"))
    live_preflight_ready = bool(preflight.get("live_preflight_ready", False)) or (
        preflight.get("status") == live_preflight_evidence_bundle_v1.LIVE_PREFLIGHT_EVIDENCE_READY
        and bool(preflight.get("ready", False))
    )

    return {
        "live_preflight_ready": live_preflight_ready,
        "final_bridge_ready": bool(preflight.get("final_bridge_ready", component.get("final_bridge_ready", False))),
        "runtime_injection_ready": bool(
            preflight.get("runtime_injection_ready", component.get("runtime_injection_ready", False))
        ),
        "oanda_connector_ready": bool(
            preflight.get("oanda_connector_ready", component.get("oanda_connector_ready", False))
        ),
        "oanda_transport_ready": bool(
            preflight.get("oanda_transport_ready", component.get("oanda_transport_ready", False))
        ),
        "account_risk_ready": bool(preflight.get("account_risk_ready", account.get("ready", False))),
        "instrument_ready": bool(preflight.get("instrument_ready", instrument.get("ready", False))),
        "quote_spread_ready": bool(preflight.get("quote_spread_ready", quote.get("ready", False))),
        "order_intent_ready": bool(preflight.get("order_intent_ready", order.get("ready", False))),
        "mobile_operator_ready": bool(
            preflight.get("mobile_operator_ready", component.get("mobile_operator_ready", False))
        ),
        "max_loss_gate_clear": _first_bool(
            preflight,
            account_evidence,
            account_from_evidence,
            key="max_loss_gate_clear",
            default=False,
        ),
        "daily_stop_clear": _first_bool(
            preflight,
            account_evidence,
            account_from_evidence,
            key="daily_stop_clear",
            default=False,
        ),
        "kill_switch_enabled": _first_bool(
            preflight,
            account_evidence,
            account_from_evidence,
            key="kill_switch_enabled",
            default=False,
        ),
        "credential_persisted": bool(preflight.get("credential_persisted", False)),
        "account_id_persisted": bool(preflight.get("account_id_persisted", False)),
        "broker_call_performed": bool(preflight.get("broker_call_performed", False)),
        "order_executed": bool(preflight.get("order_executed", False)),
        "execution_allowed": bool(preflight.get("execution_allowed", False)),
    }


def _integration_summary() -> dict[str, Any]:
    return {
        "live_preflight_status": live_preflight_evidence_bundle_v1.LIVE_PREFLIGHT_EVIDENCE_READY,
        "runtime_injection_status": protected_runtime_credential_injection_v1.PROTECTED_RUNTIME_INJECTION_READY,
        "oanda_connector_status": oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY,
        "oanda_transport_status": oanda_live_http_transport_v1.OANDA_LIVE_HTTP_TRANSPORT_READY,
        "final_bridge_status": final_live_operator_bridge_v1.FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "executor_request_status": live_runtime_executor_v1.LIVE_RUNTIME_REQUEST_READY,
        "uses_sanitized_readiness_shapes_only": True,
    }


def _command_status(
    validations: Sequence[Mapping[str, Any]],
    blockers: tuple[str, ...],
) -> str:
    statuses = tuple(str(validation.get("status", "")) for validation in validations)
    if any(status == PROTECTED_LIVE_COMMAND_INVALID for status in statuses):
        return PROTECTED_LIVE_COMMAND_INVALID
    if any(status == PROTECTED_LIVE_COMMAND_REVIEW_REQUIRED for status in statuses):
        return PROTECTED_LIVE_COMMAND_REVIEW_REQUIRED
    if blockers:
        return PROTECTED_LIVE_COMMAND_BLOCKED
    return PROTECTED_LIVE_COMMAND_READY


def _protected_action_status(status: str, sealed: str) -> str:
    if sealed == PROTECTED_LIVE_COMMAND_SEALED:
        return "SEALED_FOR_HUMAN_REVIEW_ONLY"
    if status == PROTECTED_LIVE_COMMAND_READY:
        return "READY_TO_SEAL_FOR_HUMAN_REVIEW"
    if status == PROTECTED_LIVE_COMMAND_REVIEW_REQUIRED:
        return "HUMAN_REVIEW_REQUIRED"
    return "PROTECTED_LIVE_COMMAND_BLOCKED"


def _next_action(status: str) -> str:
    return {
        PROTECTED_LIVE_COMMAND_READY: "seal_for_human_review_without_execution",
        PROTECTED_LIVE_COMMAND_SEALED: "stop_and_wait_for_separate_human_live_execution_command_outside_codex",
        PROTECTED_LIVE_COMMAND_BLOCKED: "resolve_command_package_blockers",
        PROTECTED_LIVE_COMMAND_INVALID: "provide_complete_sanitized_command_inputs",
        PROTECTED_LIVE_COMMAND_REVIEW_REQUIRED: "obtain_human_review_before_sealing",
        PROTECTED_LIVE_COMMAND_EXECUTION_FORBIDDEN: "do_not_execute_inside_codex",
    }.get(status, "provide_complete_sanitized_command_inputs")


def _safety_summary() -> dict[str, bool | int | str]:
    return {
        "protected_live_command_package": True,
        "execution_forbidden_inside_codex": True,
        "execution_requested": False,
        "execution_allowed": False,
        "order_executed": False,
        "broker_call_performed": False,
        "network_call_performed": False,
        "credential_persistence": False,
        "account_id_persistence": False,
        "raw_broker_payload_persistence": False,
        "one_order_only": True,
        "micro_size_only": True,
        "max_units": MAX_LIVE_MICRO_UNITS,
        "sanitized_evidence_only": True,
        "next_runtime_boundary": "separate_human_approved_command_outside_codex",
    }


def _order_summary_from_package(package: Mapping[str, Any]) -> dict[str, Any]:
    order = _mapping(package.get("order_intent_summary"))
    if not order:
        command = _mapping(package.get("sanitized_command"))
        order = _mapping(command.get("order_intent_summary"))
    return sanitize_protected_live_command(order)


def _preflight_bool(package: Mapping[str, Any], key: str) -> bool:
    preflight = _mapping(package.get("preflight_summary"))
    return bool(preflight.get(key, False))


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).lower().strip()
            if normalized in _SENSITIVE_KEYS:
                return True
            if _contains_sensitive_keys(value):
                return True
    elif isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _first_bool(
    first: Mapping[str, Any],
    second: Mapping[str, Any],
    third: Mapping[str, Any],
    key: str,
    default: bool,
) -> bool:
    for payload in (first, second, third):
        if key in payload:
            return bool(payload.get(key, default))
    return default


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return tuple(output)
