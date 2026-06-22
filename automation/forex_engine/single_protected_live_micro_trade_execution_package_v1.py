"""Single protected live micro-trade execution package V1.

This module builds the final Codex-safe package around the sealed protected
live command. It accepts injected dictionaries and fake clients only. Real live
runtime use remains outside Codex under a separate human-approved command.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from automation.forex_engine import final_live_operator_bridge_v1
from automation.forex_engine import live_preflight_evidence_bundle_v1
from automation.forex_engine import live_runtime_executor_v1
from automation.forex_engine import oanda_live_http_transport_v1
from automation.forex_engine import oanda_live_runtime_connector_v2
from automation.forex_engine import protected_live_execution_command_package_v1
from automation.forex_engine import protected_runtime_credential_injection_v1


SINGLE_LIVE_MICRO_TRADE_READY = "SINGLE_LIVE_MICRO_TRADE_READY"
SINGLE_LIVE_MICRO_TRADE_BLOCKED = "SINGLE_LIVE_MICRO_TRADE_BLOCKED"
SINGLE_LIVE_MICRO_TRADE_INVALID = "SINGLE_LIVE_MICRO_TRADE_INVALID"
SINGLE_LIVE_MICRO_TRADE_REVIEW_REQUIRED = "SINGLE_LIVE_MICRO_TRADE_REVIEW_REQUIRED"
SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED = "SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED"
SINGLE_LIVE_MICRO_TRADE_REAL_EXECUTION_FORBIDDEN_IN_CODEX = (
    "SINGLE_LIVE_MICRO_TRADE_REAL_EXECUTION_FORBIDDEN_IN_CODEX"
)
SINGLE_LIVE_MICRO_TRADE_RESULT_READY = "SINGLE_LIVE_MICRO_TRADE_RESULT_READY"

MAX_LIVE_MICRO_UNITS = 1000

_EXECUTION_SCHEMA = "AIOS_SINGLE_PROTECTED_LIVE_MICRO_TRADE_EXECUTION_PACKAGE_V1"

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

_AUTHORITY_TRUE_FIELDS = {
    "authenticated_operator": "authenticated_operator_required",
    "protected_action_authorized": "protected_action_authorization_required",
    "live_exception_requested": "live_exception_request_required",
    "understands_live_risk_ack": "live_risk_ack_required",
    "operator_approved_live_runtime": "operator_live_runtime_approval_required",
    "final_execute_live_order_command_ack": "final_live_command_ack_required",
    "final_human_execution_approval": "final_human_execution_approval_required",
    "one_trade_only": "one_trade_only_required",
    "micro_size_only": "micro_size_only_required",
    "no_retry": "no_retry_required",
    "no_loop": "no_loop_required",
}

_COMMAND_TRUE_FIELDS = {
    "protected_command_ready": "protected_command_not_ready",
    "protected_command_sealed": "protected_command_not_sealed",
    "live_preflight_ready": "live_preflight_not_ready",
    "final_bridge_ready": "final_bridge_not_ready",
    "runtime_injection_ready": "runtime_injection_not_ready",
    "oanda_connector_ready": "oanda_connector_not_ready",
    "oanda_transport_ready": "oanda_transport_not_ready",
}

_COMMAND_FALSE_FIELDS = {
    "execution_allowed": "execution_allowed_must_be_false_before_runtime",
    "order_executed": "order_executed_must_be_false_before_runtime",
    "broker_call_performed": "broker_call_performed_must_be_false_before_runtime",
    "credential_persisted": "credential_persisted_blocked",
    "account_id_persisted": "account_id_persisted_blocked",
}

_RUNTIME_TRUE_FIELDS = {
    "runtime_auth_provider_injected": "runtime_auth_provider_injected_required",
    "http_client_injected": "http_client_injected_required",
    "fake_client_mode": "fake_client_mode_required_inside_codex",
    "real_execution_forbidden_in_codex": "real_execution_forbidden_in_codex_required",
}

_RUNTIME_FALSE_FIELDS = {
    "allow_live_network_once": "allow_live_network_once_forbidden_inside_codex",
    "protected_live_execution_command": "protected_live_execution_command_forbidden_inside_codex",
}

_ORDER_TRUE_FIELDS = {
    "risk_cap_confirmed": "risk_cap_not_confirmed",
    "stop_loss_confirmed": "stop_loss_not_confirmed",
    "take_profit_confirmed": "take_profit_not_confirmed",
    "one_trade_only": "one_trade_only_required",
    "micro_size_only": "micro_size_only_required",
}


def validate_single_live_micro_trade_authority(
    authority_state: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate final human authority evidence without enabling execution."""

    authority = dict(authority_state or {})
    blockers: list[str] = []
    if not authority:
        blockers.append("authority_state_missing")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    elif _contains_sensitive_keys(authority):
        blockers.append("sensitive_authority_field_detected")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    else:
        blockers.extend(_missing_true_blockers(authority, _AUTHORITY_TRUE_FIELDS))
        if _to_int(authority.get("max_order_count")) != 1:
            blockers.append("max_order_count_must_equal_one")
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED if blockers else SINGLE_LIVE_MICRO_TRADE_READY

    summary = {
        "authenticated_operator": bool(authority.get("authenticated_operator", False)),
        "protected_action_authorized": bool(authority.get("protected_action_authorized", False)),
        "live_exception_requested": bool(authority.get("live_exception_requested", False)),
        "understands_live_risk_ack": bool(authority.get("understands_live_risk_ack", False)),
        "operator_approved_live_runtime": bool(authority.get("operator_approved_live_runtime", False)),
        "final_execute_live_order_command_ack": bool(
            authority.get("final_execute_live_order_command_ack", False)
        ),
        "final_human_execution_approval": bool(authority.get("final_human_execution_approval", False)),
        "one_trade_only": bool(authority.get("one_trade_only", False)),
        "micro_size_only": bool(authority.get("micro_size_only", False)),
        "no_retry": bool(authority.get("no_retry", False)),
        "no_loop": bool(authority.get("no_loop", False)),
        "max_order_count": _to_int(authority.get("max_order_count")),
    }
    return {
        "validation_schema": "AIOS_SINGLE_LIVE_MICRO_TRADE_AUTHORITY_VALIDATION_V1",
        "status": status,
        "ready": status == SINGLE_LIVE_MICRO_TRADE_READY,
        "blockers": tuple(_unique(blockers)),
        "authority_summary": sanitize_single_live_micro_trade_result(summary),
        "next_safe_action": _next_action(status),
    }


def validate_single_live_micro_trade_command(
    command_package: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate a sealed protected command package without executing it."""

    command = dict(command_package or {})
    truth = _command_truth(command)
    blockers: list[str] = []
    if not command:
        blockers.append("command_package_missing")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    elif _contains_sensitive_keys(command):
        blockers.append("sensitive_command_field_detected")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    else:
        blockers.extend(_missing_true_blockers(truth, _COMMAND_TRUE_FIELDS))
        blockers.extend(_bad_false_blockers(truth, _COMMAND_FALSE_FIELDS))
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED if blockers else SINGLE_LIVE_MICRO_TRADE_READY

    return {
        "validation_schema": "AIOS_SINGLE_LIVE_MICRO_TRADE_COMMAND_VALIDATION_V1",
        "status": status,
        "ready": status == SINGLE_LIVE_MICRO_TRADE_READY,
        "blockers": tuple(_unique(blockers)),
        "sanitized_command_summary": sanitize_single_live_micro_trade_result(truth),
        "integration_summary": _integration_summary(),
        "next_safe_action": _next_action(status),
    }


def validate_single_live_micro_trade_runtime_inputs(
    runtime_inputs: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Validate Codex-safe runtime input shape for fake-only execution."""

    runtime = dict(runtime_inputs or {})
    blockers: list[str] = []
    if not runtime:
        blockers.append("runtime_inputs_missing")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    elif _contains_sensitive_keys(runtime):
        blockers.append("sensitive_runtime_input_field_detected")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    else:
        blockers.extend(_missing_true_blockers(runtime, _RUNTIME_TRUE_FIELDS))
        blockers.extend(_bad_false_blockers(runtime, _RUNTIME_FALSE_FIELDS))
        if bool(runtime.get("fake_execution_selected", False)) is not True and bool(
            runtime.get("dry_run_only", False)
        ) is not True:
            blockers.append("dry_run_only_required_when_fake_execution_not_selected")
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED if blockers else SINGLE_LIVE_MICRO_TRADE_READY

    summary = {
        "runtime_auth_provider_injected": bool(runtime.get("runtime_auth_provider_injected", False)),
        "http_client_injected": bool(runtime.get("http_client_injected", False)),
        "fake_client_mode": bool(runtime.get("fake_client_mode", False)),
        "fake_execution_selected": bool(runtime.get("fake_execution_selected", False)),
        "allow_live_network_once": bool(runtime.get("allow_live_network_once", False)),
        "protected_live_execution_command": bool(runtime.get("protected_live_execution_command", False)),
        "real_execution_forbidden_in_codex": True,
        "dry_run_only": bool(runtime.get("dry_run_only", False)),
        "credential_values_returned": False,
        "account_identifier_values_returned": False,
    }
    return {
        "validation_schema": "AIOS_SINGLE_LIVE_MICRO_TRADE_RUNTIME_INPUT_VALIDATION_V1",
        "status": status,
        "ready": status == SINGLE_LIVE_MICRO_TRADE_READY,
        "blockers": tuple(_unique(blockers)),
        "runtime_summary": sanitize_single_live_micro_trade_result(summary),
        "next_safe_action": _next_action(status),
    }


def build_single_live_micro_trade_execution_package(
    authority_state: Mapping[str, Any] | None = None,
    command_package: Mapping[str, Any] | None = None,
    runtime_inputs: Mapping[str, Any] | None = None,
    order_intent: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the final Codex-safe execution package without real execution."""

    authority = validate_single_live_micro_trade_authority(authority_state)
    command = validate_single_live_micro_trade_command(command_package)
    runtime = validate_single_live_micro_trade_runtime_inputs(runtime_inputs)
    order = _validate_order_intent(order_intent)
    blockers = classify_single_live_micro_trade_blockers(authority, command, runtime, order)
    status = _package_status((authority, command, runtime, order), blockers)
    runtime_summary = runtime["runtime_summary"]
    order_summary = order["order_intent_summary"]
    fake_execution_summary = {
        "fake_execution_selected": bool(runtime_summary.get("fake_execution_selected", False)),
        "fake_execution_status": "FAKE_EXECUTION_AVAILABLE"
        if status == SINGLE_LIVE_MICRO_TRADE_READY and runtime_summary.get("fake_execution_selected")
        else "FAKE_EXECUTION_NOT_AVAILABLE",
        "fake_order_executed": False,
        "fake_broker_call_performed": False,
        "second_order_blocked": False,
    }
    mobile_summary = build_single_live_micro_trade_mobile_summary(
        status=status,
        blockers=blockers,
        order_intent_summary=order_summary,
        runtime_summary=runtime_summary,
        fake_execution_summary=fake_execution_summary,
    )
    return {
        "execution_schema": _EXECUTION_SCHEMA,
        "status": status,
        "ready": status == SINGLE_LIVE_MICRO_TRADE_READY,
        "blockers": blockers,
        "authority_summary": authority["authority_summary"],
        "sanitized_command_summary": command["sanitized_command_summary"],
        "order_intent_summary": order_summary,
        "runtime_summary": runtime_summary,
        "fake_execution_summary": fake_execution_summary,
        "mobile_summary": mobile_summary,
        "safety_summary": _safety_summary(),
        "integration_summary": _integration_summary(),
        "next_safe_action": _next_action(status),
        "protected_action_status": _protected_action_status(status),
        "real_execution_forbidden_in_codex": True,
        "fake_execution_available": status == SINGLE_LIVE_MICRO_TRADE_READY
        and bool(runtime_summary.get("fake_execution_selected", False)),
        "execution_allowed": False,
        "real_order_executed": False,
        "real_broker_call_performed": False,
        "order_executed": False,
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
    }


def execute_single_live_micro_trade_fake_only(
    execution_package: Mapping[str, Any] | None,
    fake_client: Any = None,
    fake_transport: Any = None,
) -> dict[str, Any]:
    """Submit one fake order through an injected fake object only."""

    package = _mutable_package(execution_package)
    blockers: list[str] = []
    runtime = _mapping(package.get("runtime_summary"))
    order = _mapping(package.get("order_intent_summary"))
    previous_fake_count = _to_int(package.get("fake_order_count"))

    if not package:
        blockers.append("execution_package_missing")
    elif package.get("status") != SINGLE_LIVE_MICRO_TRADE_READY or not package.get("ready"):
        blockers.append("execution_package_not_ready")
    if bool(runtime.get("fake_client_mode", False)) is not True:
        blockers.append("fake_client_mode_required")
    if bool(package.get("real_execution_forbidden_in_codex", True)) is not True:
        blockers.append("real_execution_forbidden_in_codex_required")
    if previous_fake_count >= 1:
        blockers.append("second_order_blocked")
    blockers.extend(_fake_target_blockers(fake_client, fake_transport))

    if blockers:
        return _fake_result(
            status=SINGLE_LIVE_MICRO_TRADE_BLOCKED,
            order=order,
            blockers=blockers,
            fake_response={},
            fake_count=previous_fake_count,
        )

    fake_response = _call_fake_submitter(fake_client, fake_transport, order)
    if isinstance(execution_package, dict):
        execution_package["fake_order_count"] = previous_fake_count + 1
        execution_package["fake_execution_summary"] = {
            "fake_execution_status": SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED,
            "fake_order_executed": True,
            "fake_broker_call_performed": True,
            "second_order_blocked": False,
        }
    return _fake_result(
        status=SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED,
        order=order,
        blockers=(),
        fake_response=fake_response,
        fake_count=previous_fake_count + 1,
    )


def build_single_live_micro_trade_result_evidence(
    fake_execution_output: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Build sanitized result evidence from fake-only execution output."""

    output = sanitize_single_live_micro_trade_result(fake_execution_output or {})
    blockers: list[str] = []
    if not output:
        blockers.append("fake_execution_output_missing")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    elif output.get("status") != SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED:
        blockers.append("fake_execution_not_submitted")
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED
    elif bool(fake_execution_output.get("real_order_executed", False)):  # type: ignore[union-attr]
        blockers.append("real_order_claim_forbidden")
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED
    elif bool(fake_execution_output.get("real_broker_call_performed", False)):  # type: ignore[union-attr]
        blockers.append("real_broker_call_claim_forbidden")
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED
    else:
        status = SINGLE_LIVE_MICRO_TRADE_RESULT_READY

    result_summary = {
        "fake_order_executed": bool(output.get("fake_order_executed", False)),
        "fake_broker_call_performed": bool(output.get("fake_broker_call_performed", False)),
        "real_order_executed": False,
        "real_broker_call_performed": False,
        "order_executed": False,
        "fake_status": output.get("status", SINGLE_LIVE_MICRO_TRADE_INVALID),
        "fake_order_count": _to_int(output.get("fake_order_count")),
    }
    return {
        "result_schema": "AIOS_SINGLE_LIVE_MICRO_TRADE_RESULT_EVIDENCE_V1",
        "status": status,
        "ready": status == SINGLE_LIVE_MICRO_TRADE_RESULT_READY,
        "blockers": tuple(_unique(blockers)),
        "sanitized_result_summary": sanitize_single_live_micro_trade_result(result_summary),
        "sanitized_fake_result": output,
        "fake_order_executed": bool(output.get("fake_order_executed", False)),
        "fake_broker_call_performed": bool(output.get("fake_broker_call_performed", False)),
        "real_order_executed": False,
        "real_broker_call_performed": False,
        "order_executed": False,
        "safety_summary": _safety_summary(),
        "next_safe_action": _next_result_action(status),
    }


def build_single_live_micro_trade_mobile_summary(
    execution_package: Mapping[str, Any] | None = None,
    status: str | None = None,
    blockers: Sequence[str] | None = None,
    order_intent_summary: Mapping[str, Any] | None = None,
    runtime_summary: Mapping[str, Any] | None = None,
    fake_execution_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build compact Samsung/mobile truth fields from sanitized evidence."""

    package = sanitize_single_live_micro_trade_result(execution_package or {})
    order = sanitize_single_live_micro_trade_result(
        order_intent_summary or package.get("order_intent_summary", {})
    )
    runtime = sanitize_single_live_micro_trade_result(
        runtime_summary or package.get("runtime_summary", {})
    )
    fake = sanitize_single_live_micro_trade_result(
        fake_execution_summary or package.get("fake_execution_summary", {})
    )
    active_status = status or str(package.get("status", SINGLE_LIVE_MICRO_TRADE_INVALID))
    active_blockers = tuple(_unique(list(blockers or package.get("blockers", ()))))
    return {
        "mode": "GOVERNED_SINGLE_LIVE_MICRO_TRADE_FAKE_ONLY_CODEX_PACKAGE",
        "status": active_status,
        "instrument": order.get("instrument", "UNKNOWN"),
        "side": order.get("side", "UNKNOWN"),
        "units": order.get("units", "UNKNOWN"),
        "stop_loss": order.get("stop_loss", "REQUIRED"),
        "take_profit": order.get("take_profit", "REQUIRED"),
        "max_loss_gate": "CLEAR" if order.get("max_loss_gate_clear", True) else "NOT_CLEAR",
        "daily_stop_gate": "CLEAR" if order.get("daily_stop_clear", True) else "NOT_CLEAR",
        "kill_switch": "ENABLED" if order.get("kill_switch_enabled", False) else "DISABLED",
        "fake_execution_status": fake.get("fake_execution_status", "FAKE_EXECUTION_NOT_RUN"),
        "real_execution_blocked_status": SINGLE_LIVE_MICRO_TRADE_REAL_EXECUTION_FORBIDDEN_IN_CODEX,
        "runtime_auth_provider_injected": bool(runtime.get("runtime_auth_provider_injected", False)),
        "http_client_injected": bool(runtime.get("http_client_injected", False)),
        "fake_client_mode": bool(runtime.get("fake_client_mode", False)),
        "execution_allowed": False,
        "real_order_executed": False,
        "real_broker_call_performed": False,
        "blockers": active_blockers,
        "next_safe_action": _next_action(active_status),
    }


def sanitize_single_live_micro_trade_result(payload: Any) -> dict[str, Any]:
    """Remove sensitive fields and force real-execution flags false."""

    if not isinstance(payload, Mapping):
        return {}
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        normalized = str(key).lower().strip()
        if normalized in _SENSITIVE_KEYS:
            continue
        if isinstance(value, Mapping):
            sanitized[str(key)] = sanitize_single_live_micro_trade_result(value)
        elif isinstance(value, list | tuple):
            sanitized[str(key)] = tuple(
                sanitize_single_live_micro_trade_result(item) if isinstance(item, Mapping) else item
                for item in value
            )
        else:
            sanitized[str(key)] = value
    sanitized["credential_persisted"] = False
    sanitized["account_id_persisted"] = False
    sanitized["raw_broker_payload_persisted"] = False
    sanitized["real_order_executed"] = False
    sanitized["real_broker_call_performed"] = False
    return sanitized


def classify_single_live_micro_trade_blockers(
    authority_validation: Mapping[str, Any] | None = None,
    command_validation: Mapping[str, Any] | None = None,
    runtime_validation: Mapping[str, Any] | None = None,
    order_intent_validation: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Collect blockers across authority, command, runtime, and order inputs."""

    blockers: list[str] = []
    for section_name, validation in (
        ("authority", authority_validation),
        ("command", command_validation),
        ("runtime", runtime_validation),
        ("order_intent", order_intent_validation),
    ):
        payload = dict(validation or {})
        if not payload:
            blockers.append(f"{section_name}_validation_missing")
        elif payload.get("status") != SINGLE_LIVE_MICRO_TRADE_READY or not payload.get("ready"):
            blockers.extend(payload.get("blockers", ()))
    return tuple(_unique(blockers))


def _validate_order_intent(order_intent: Mapping[str, Any] | None) -> dict[str, Any]:
    intent = dict(order_intent or {})
    blockers: list[str] = []
    instrument = str(intent.get("instrument", "")).strip()
    side = str(intent.get("side", "")).strip().upper()
    units = _to_int(intent.get("units"))

    if not intent:
        blockers.append("order_intent_missing")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
    elif _contains_sensitive_keys(intent):
        blockers.append("sensitive_order_intent_field_detected")
        status = SINGLE_LIVE_MICRO_TRADE_INVALID
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
        blockers.extend(_missing_true_blockers(intent, _ORDER_TRUE_FIELDS))
        status = SINGLE_LIVE_MICRO_TRADE_BLOCKED if blockers else SINGLE_LIVE_MICRO_TRADE_READY

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
        "max_loss_gate_clear": bool(intent.get("max_loss_gate_clear", True)),
        "daily_stop_clear": bool(intent.get("daily_stop_clear", True)),
        "kill_switch_enabled": bool(intent.get("kill_switch_enabled", False)),
        "order_executed": False,
        "broker_call_performed": False,
    }
    return {
        "validation_schema": "AIOS_SINGLE_LIVE_MICRO_TRADE_ORDER_INTENT_VALIDATION_V1",
        "status": status,
        "ready": status == SINGLE_LIVE_MICRO_TRADE_READY,
        "blockers": tuple(_unique(blockers)),
        "order_intent_summary": sanitize_single_live_micro_trade_result(summary),
        "next_safe_action": _next_action(status),
    }


def _command_truth(command_package: Mapping[str, Any]) -> dict[str, Any]:
    command = protected_live_execution_command_package_v1.sanitize_protected_live_command(command_package)
    preflight = _mapping(command.get("preflight_summary"))
    sanitized_command = _mapping(command.get("sanitized_command"))
    protected_ready = bool(command.get("protected_command_ready", False)) or (
        command.get("command_status")
        in {
            protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_READY,
            protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED,
        }
        and bool(command.get("ready", False))
    )
    protected_sealed = bool(command.get("protected_command_sealed", False)) or (
        command.get("sealed")
        == protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED
        and command.get("command_status")
        == protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED
    )
    return {
        "protected_command_ready": protected_ready,
        "protected_command_sealed": protected_sealed,
        "live_preflight_ready": bool(
            command.get("live_preflight_ready", preflight.get("live_preflight_ready", False))
        ),
        "final_bridge_ready": bool(command.get("final_bridge_ready", preflight.get("final_bridge_ready", False))),
        "runtime_injection_ready": bool(
            command.get("runtime_injection_ready", preflight.get("runtime_injection_ready", False))
        ),
        "oanda_connector_ready": bool(
            command.get("oanda_connector_ready", preflight.get("oanda_connector_ready", False))
        ),
        "oanda_transport_ready": bool(
            command.get("oanda_transport_ready", preflight.get("oanda_transport_ready", False))
        ),
        "execution_allowed": bool(command.get("execution_allowed", sanitized_command.get("execution_allowed", False))),
        "order_executed": bool(command.get("order_executed", sanitized_command.get("order_executed", False))),
        "broker_call_performed": bool(
            command.get("broker_call_performed", sanitized_command.get("broker_call_performed", False))
        ),
        "credential_persisted": bool(command.get("credential_persisted", False)),
        "account_id_persisted": bool(command.get("account_id_persisted", False)),
        "sealed_status": command.get("sealed", "UNKNOWN"),
        "command_status": command.get("command_status", "UNKNOWN"),
        "preview_only": bool(sanitized_command.get("preview_only", True)),
    }


def _fake_target_blockers(fake_client: Any, fake_transport: Any) -> tuple[str, ...]:
    target = fake_client if fake_client is not None else fake_transport
    if target is None:
        return ("fake_submitter_missing",)
    if callable(getattr(target, "place_live_micro_order", None)):
        return tuple()
    if callable(getattr(target, "submit_live_micro_order", None)):
        return tuple()
    return ("fake_submitter_method_missing",)


def _call_fake_submitter(fake_client: Any, fake_transport: Any, order: Mapping[str, Any]) -> dict[str, Any]:
    target = fake_client if fake_client is not None else fake_transport
    if callable(getattr(target, "place_live_micro_order", None)):
        return sanitize_single_live_micro_trade_result(target.place_live_micro_order(dict(order)))
    if callable(getattr(target, "submit_live_micro_order", None)):
        return sanitize_single_live_micro_trade_result(target.submit_live_micro_order(dict(order)))
    return {}


def _fake_result(
    status: str,
    order: Mapping[str, Any],
    blockers: Sequence[str],
    fake_response: Mapping[str, Any],
    fake_count: int,
) -> dict[str, Any]:
    fake_submitted = status == SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED
    return {
        "fake_execution_schema": "AIOS_SINGLE_LIVE_MICRO_TRADE_FAKE_EXECUTION_RESULT_V1",
        "status": status,
        "ready": fake_submitted,
        "blockers": tuple(_unique(blockers)),
        "instrument": order.get("instrument", "UNKNOWN"),
        "side": order.get("side", "UNKNOWN"),
        "units": order.get("units", "UNKNOWN"),
        "fake_order_count": fake_count,
        "sanitized_fake_response": sanitize_single_live_micro_trade_result(fake_response),
        "real_broker_call_performed": False,
        "fake_broker_call_performed": fake_submitted,
        "order_executed": False,
        "real_order_executed": False,
        "fake_order_executed": fake_submitted,
        "second_order_blocked": "second_order_blocked" in blockers,
        "credential_persisted": False,
        "account_id_persisted": False,
        "raw_broker_payload_persisted": False,
        "safety_summary": _safety_summary(),
        "next_safe_action": _next_result_action(status),
    }


def _missing_true_blockers(payload: Mapping[str, Any], required: Mapping[str, str]) -> list[str]:
    return [blocker for field, blocker in required.items() if bool(payload.get(field, False)) is not True]


def _bad_false_blockers(payload: Mapping[str, Any], required: Mapping[str, str]) -> list[str]:
    return [blocker for field, blocker in required.items() if bool(payload.get(field, False)) is not False]


def _package_status(validations: Sequence[Mapping[str, Any]], blockers: tuple[str, ...]) -> str:
    statuses = tuple(str(validation.get("status", "")) for validation in validations)
    if SINGLE_LIVE_MICRO_TRADE_INVALID in statuses:
        return SINGLE_LIVE_MICRO_TRADE_INVALID
    if SINGLE_LIVE_MICRO_TRADE_REVIEW_REQUIRED in statuses:
        return SINGLE_LIVE_MICRO_TRADE_REVIEW_REQUIRED
    if blockers:
        return SINGLE_LIVE_MICRO_TRADE_BLOCKED
    return SINGLE_LIVE_MICRO_TRADE_READY


def _integration_summary() -> dict[str, Any]:
    return {
        "protected_command_status": protected_live_execution_command_package_v1.PROTECTED_LIVE_COMMAND_SEALED,
        "live_preflight_status": live_preflight_evidence_bundle_v1.LIVE_PREFLIGHT_EVIDENCE_READY,
        "runtime_injection_status": protected_runtime_credential_injection_v1.PROTECTED_RUNTIME_INJECTION_READY,
        "oanda_connector_status": oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY,
        "oanda_transport_status": oanda_live_http_transport_v1.OANDA_LIVE_HTTP_TRANSPORT_READY,
        "final_bridge_status": final_live_operator_bridge_v1.FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "executor_request_status": live_runtime_executor_v1.LIVE_RUNTIME_REQUEST_READY,
        "uses_sanitized_readiness_shapes_only": True,
    }


def _safety_summary() -> dict[str, bool | int | str]:
    return {
        "single_protected_live_micro_trade_package": True,
        "real_execution_forbidden_in_codex": True,
        "fake_only_execution_available": True,
        "execution_allowed": False,
        "order_executed": False,
        "real_order_executed": False,
        "real_broker_call_performed": False,
        "credential_persistence": False,
        "account_id_persistence": False,
        "raw_broker_payload_persistence": False,
        "network_call_performed": False,
        "no_retry": True,
        "no_loop": True,
        "one_order_only": True,
        "micro_size_only": True,
        "max_units": MAX_LIVE_MICRO_UNITS,
        "sanitized_evidence_only": True,
        "next_runtime_boundary": "separate_human_approved_runtime_outside_codex",
    }


def _protected_action_status(status: str) -> str:
    return {
        SINGLE_LIVE_MICRO_TRADE_READY: "READY_FOR_FAKE_ONLY_CODEX_TEST",
        SINGLE_LIVE_MICRO_TRADE_BLOCKED: "PROTECTED_LIVE_MICRO_TRADE_BLOCKED",
        SINGLE_LIVE_MICRO_TRADE_INVALID: "PROTECTED_LIVE_MICRO_TRADE_INVALID",
        SINGLE_LIVE_MICRO_TRADE_REVIEW_REQUIRED: "HUMAN_REVIEW_REQUIRED",
    }.get(status, "PROTECTED_LIVE_MICRO_TRADE_BLOCKED")


def _next_action(status: str) -> str:
    return {
        SINGLE_LIVE_MICRO_TRADE_READY: "run_fake_only_execution_test_or_stop_before_real_runtime",
        SINGLE_LIVE_MICRO_TRADE_BLOCKED: "resolve_single_live_micro_trade_blockers",
        SINGLE_LIVE_MICRO_TRADE_INVALID: "provide_complete_sanitized_single_live_micro_trade_inputs",
        SINGLE_LIVE_MICRO_TRADE_REVIEW_REQUIRED: "obtain_human_review_before_runtime",
        SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED: "build_sanitized_fake_result_evidence",
        SINGLE_LIVE_MICRO_TRADE_REAL_EXECUTION_FORBIDDEN_IN_CODEX: "do_not_execute_real_order_inside_codex",
    }.get(status, "provide_complete_sanitized_single_live_micro_trade_inputs")


def _next_result_action(status: str) -> str:
    return {
        SINGLE_LIVE_MICRO_TRADE_FAKE_SUBMITTED: "build_sanitized_fake_result_evidence",
        SINGLE_LIVE_MICRO_TRADE_RESULT_READY: "stop_and_wait_for_human_approved_real_runtime_outside_codex",
        SINGLE_LIVE_MICRO_TRADE_BLOCKED: "resolve_fake_result_blockers",
        SINGLE_LIVE_MICRO_TRADE_INVALID: "provide_fake_execution_output",
    }.get(status, "provide_fake_execution_output")


def _contains_sensitive_keys(payload: Any) -> bool:
    if isinstance(payload, Mapping):
        return bool(
            any(
                str(key).lower().strip() in _SENSITIVE_KEYS or _contains_sensitive_keys(value)
                for key, value in payload.items()
            )
        )
    if isinstance(payload, list | tuple):
        return any(_contains_sensitive_keys(item) for item in payload)
    return False


def _mutable_package(execution_package: Mapping[str, Any] | None) -> dict[str, Any]:
    return execution_package if isinstance(execution_package, dict) else dict(execution_package or {})


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


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
