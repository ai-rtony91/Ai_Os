"""Governed live micro-trade lane milestone."""

from __future__ import annotations

from typing import Any, Mapping

import time

LIVE_READINESS_READY = "LIVE_READINESS_READY"
LIVE_READINESS_BLOCKED = "LIVE_READINESS_BLOCKED"
LIVE_READINESS_INVALID = "LIVE_READINESS_INVALID"
LIVE_READINESS_REVIEW_REQUIRED = "LIVE_READINESS_REVIEW_REQUIRED"

LIVE_BROKER_PREFLIGHT_READY = "LIVE_BROKER_PREFLIGHT_READY"
LIVE_BROKER_PREFLIGHT_BLOCKED = "LIVE_BROKER_PREFLIGHT_BLOCKED"
LIVE_BROKER_PREFLIGHT_INVALID = "LIVE_BROKER_PREFLIGHT_INVALID"
LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED = "LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED"

LIVE_MICRO_TRADE_ARMED = "LIVE_MICRO_TRADE_ARMED"
LIVE_MICRO_TRADE_BLOCKED = "LIVE_MICRO_TRADE_BLOCKED"
LIVE_MICRO_TRADE_INVALID = "LIVE_MICRO_TRADE_INVALID"
LIVE_MICRO_TRADE_REVIEW_REQUIRED = "LIVE_MICRO_TRADE_REVIEW_REQUIRED"

LIVE_ORDER_COMMAND_READY = "LIVE_ORDER_COMMAND_READY"
LIVE_ORDER_COMMAND_BLOCKED = "LIVE_ORDER_COMMAND_BLOCKED"
LIVE_ORDER_COMMAND_INVALID = "LIVE_ORDER_COMMAND_INVALID"
LIVE_ORDER_COMMAND_REVIEW_REQUIRED = "LIVE_ORDER_COMMAND_REVIEW_REQUIRED"

OPERATOR_LOGIN_PORTAL_READY = "OPERATOR_LOGIN_PORTAL_READY"
OPERATOR_LOGIN_PORTAL_BLOCKED = "OPERATOR_LOGIN_PORTAL_BLOCKED"
OPERATOR_LOGIN_PORTAL_INVALID = "OPERATOR_LOGIN_PORTAL_INVALID"
OPERATOR_LOGIN_PORTAL_REVIEW_REQUIRED = "OPERATOR_LOGIN_PORTAL_REVIEW_REQUIRED"

PROTECTED_LIVE_ACTION_AUTH_READY = "PROTECTED_LIVE_ACTION_AUTH_READY"
PROTECTED_LIVE_ACTION_AUTH_BLOCKED = "PROTECTED_LIVE_ACTION_AUTH_BLOCKED"
PROTECTED_LIVE_ACTION_AUTH_INVALID = "PROTECTED_LIVE_ACTION_AUTH_INVALID"
PROTECTED_LIVE_ACTION_AUTH_REVIEW_REQUIRED = "PROTECTED_LIVE_ACTION_AUTH_REVIEW_REQUIRED"

LIVE_BROKER_EXCEPTION_CLASSIFICATION = "LIVE_EXCEPTION_APPROVED"
SUPPORTED_LOGIN_PROVIDERS = ("github", "google", "microsoft")
SUPPORTED_PROTECTED_ACTIONS = {
    "live_readiness_review",
    "live_broker_preflight",
    "live_micro_trade_arming",
    "live_order_command_contract",
    "risk_limit_change",
    "credential_runtime_injection",
}

LIVE_MICRO_UNITS_MAX = 1000


def evaluate_live_readiness_evidence(
    demo_state: Mapping[str, Any] | None = None,
    strategy_evidence: Mapping[str, Any] | None = None,
    risk_state: Mapping[str, Any] | None = None,
    operator_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    demo_start = time.perf_counter()
    demo_payload = dict(demo_state or {})
    demo_read_ms = _ms(demo_start, time.perf_counter())
    strategy_start = time.perf_counter()
    strategy_payload = dict(strategy_evidence or {})
    strategy_read_ms = _ms(strategy_start, time.perf_counter())
    risk_start = time.perf_counter()
    risk_payload = dict(risk_state or {})
    risk_read_ms = _ms(risk_start, time.perf_counter())
    operator_start = time.perf_counter()
    operator_payload = dict(operator_state or {})
    operator_read_ms = _ms(operator_start, time.perf_counter())

    blockers: list[str] = []

    if demo_state is None:
        blockers.append("demo_state_missing")
    if strategy_evidence is None:
        blockers.append("strategy_evidence_missing")
    if risk_state is None:
        blockers.append("risk_state_missing")
    if operator_state is None:
        blockers.append("operator_state_missing")

    demo_validated = bool(demo_payload.get("demo_validated", False))
    demo_trade_count = _coerce_positive_int(demo_payload.get("demo_trade_count"))
    demo_execution_quality_clear = bool(demo_payload.get("demo_execution_quality_clear", False))
    demo_drawdown_clear = bool(demo_payload.get("demo_drawdown_clear", False))

    expected_value_positive = bool(strategy_payload.get("expected_value_positive", False))
    strategy_blocked_markers = [
        ("win_rate_present", strategy_payload.get("win_rate_present")),
        ("average_win_present", strategy_payload.get("average_win_present")),
        ("average_loss_present", strategy_payload.get("average_loss_present")),
        ("max_drawdown_present", strategy_payload.get("max_drawdown_present")),
        ("risk_of_ruin_present", strategy_payload.get("risk_of_ruin_present")),
        ("repeatability_present", strategy_payload.get("repeatability_present")),
    ]

    kill_switch_enabled = bool(risk_payload.get("kill_switch_enabled", False))
    max_loss_gate_clear = bool(risk_payload.get("max_loss_gate_clear", False))
    daily_stop_clear = bool(risk_payload.get("daily_stop_clear", False))
    position_size_micro_only = bool(risk_payload.get("position_size_micro_only", False))
    stop_loss_required = bool(risk_payload.get("stop_loss_required", False))
    take_profit_required = bool(risk_payload.get("take_profit_required", False))

    authenticated_operator = bool(operator_payload.get("authenticated_operator", False))
    protected_action_authorized = bool(operator_payload.get("protected_action_authorized", False))
    live_exception_requested = bool(operator_payload.get("live_exception_requested", False))
    understands_live_risk_ack = bool(operator_payload.get("understands_live_risk_ack", False))

    if not demo_validated:
        blockers.append("demo_validation_incomplete")
    if demo_trade_count <= 0:
        blockers.append("demo_trade_count_missing_or_invalid")
    if not demo_drawdown_clear:
        blockers.append("demo_drawdown_not_clear")
    if not demo_execution_quality_clear:
        blockers.append("demo_execution_quality_not_clear")
    if not expected_value_positive:
        blockers.append("expected_value_not_positive")
    if not stop_loss_required:
        blockers.append("stop_loss_not_required")
    if not take_profit_required:
        blockers.append("take_profit_not_required")
    if not position_size_micro_only:
        blockers.append("micro_size_only_not_confirmed")
    if kill_switch_enabled:
        blockers.append("kill_switch_enabled")
    if not max_loss_gate_clear:
        blockers.append("max_loss_gate_blocked")
    if not daily_stop_clear:
        blockers.append("daily_stop_blocked")

    for field_name, value in strategy_blocked_markers:
        if not bool(value):
            blockers.append(f"{field_name}_missing")

    operator_ready = (
        authenticated_operator
        and protected_action_authorized
        and live_exception_requested
        and understands_live_risk_ack
    )

    if not operator_ready and not blockers:
        readiness_status = LIVE_READINESS_REVIEW_REQUIRED
    elif blockers:
        readiness_status = (
            LIVE_READINESS_INVALID
            if "demo_state_missing" in blockers or "strategy_evidence_missing" in blockers or "risk_state_missing" in blockers or "operator_state_missing" in blockers
            else LIVE_READINESS_BLOCKED
        )
    else:
        readiness_status = LIVE_READINESS_READY

    evidence_summary = {
        "demo_state": {
            "demo_validated": demo_validated,
            "demo_trade_count": demo_trade_count,
            "demo_profit_factor_clear": bool(demo_payload.get("demo_profit_factor_clear", False)),
            "demo_drawdown_clear": demo_drawdown_clear,
            "demo_execution_quality_clear": demo_execution_quality_clear,
            "demo_result_ledger_present": bool(demo_payload.get("demo_result_ledger_present", False)),
        },
        "strategy_evidence": {
            "expected_value_positive": expected_value_positive,
            "win_rate_present": bool(strategy_payload.get("win_rate_present", False)),
            "average_win_present": bool(strategy_payload.get("average_win_present", False)),
            "average_loss_present": bool(strategy_payload.get("average_loss_present", False)),
            "max_drawdown_present": bool(strategy_payload.get("max_drawdown_present", False)),
            "risk_of_ruin_present": bool(strategy_payload.get("risk_of_ruin_present", False)),
            "repeatability_present": bool(strategy_payload.get("repeatability_present", False)),
        },
        "risk_state": {
            "kill_switch_enabled": kill_switch_enabled,
            "max_loss_gate_clear": max_loss_gate_clear,
            "daily_stop_clear": daily_stop_clear,
            "position_size_micro_only": position_size_micro_only,
            "portfolio_exposure_clear": bool(risk_payload.get("portfolio_exposure_clear", False)),
            "stop_loss_required": stop_loss_required,
            "take_profit_required": take_profit_required,
        },
        "operator_state": {
            "authenticated_operator": authenticated_operator,
            "protected_action_authorized": protected_action_authorized,
            "live_exception_requested": live_exception_requested,
            "understands_live_risk_ack": understands_live_risk_ack,
        },
    }

    readiness_summary = {
        "live_readiness_ready": readiness_status == LIVE_READINESS_READY,
        "review_required": readiness_status == LIVE_READINESS_REVIEW_REQUIRED,
        "blocked": readiness_status == LIVE_READINESS_BLOCKED,
    }

    return {
        "readiness_schema": "AIOS_LIVE_READINESS_EVIDENCE_V10.v1",
        "readiness_status": readiness_status,
        "ready": readiness_status == LIVE_READINESS_READY,
        "blockers": tuple(blockers),
        "sanitized_summary": _safe_copy(evidence_summary),
        "safety_summary": {
            "live_trade_executed": False,
            "order_executed": False,
            "broker_call_performed": False,
            "no_credential_persistence": True,
            "no_default_network": True,
            "no_live_trading_execution": False,
        },
        "next_safe_action": _live_readiness_next_action(readiness_status),
        "readiness_summary": readiness_summary,
        "latency_budget": {
            "demo_state_read_ms": demo_read_ms,
            "strategy_evidence_read_ms": strategy_read_ms,
            "risk_state_read_ms": risk_read_ms,
            "operator_state_read_ms": operator_read_ms,
            "evidence_eval_ms": _ms(strategy_start, time.perf_counter()),
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _ms(start, time.perf_counter()),
        },
    }


def build_live_broker_connection_preflight(
    live_readiness: Mapping[str, Any] | None,
    live_connection_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    readiness_payload = dict(live_readiness or {})
    readiness_start = time.perf_counter()
    readiness_read_ms = _ms(readiness_start, time.perf_counter())

    request = dict(live_connection_request or {})
    request_start = time.perf_counter()
    request_read_ms = _ms(request_start, time.perf_counter())

    blockers: list[str] = []
    operator_approved = bool(request.get("operator_approved", False))
    live_exception_mode = bool(request.get("live_exception_mode", False))
    read_only_first = bool(request.get("read_only_first", False))
    credentials_runtime_only = bool(request.get("credentials_runtime_only", False))
    credentials_persisted = bool(request.get("credentials_persisted", False))
    account_id_persisted = bool(request.get("account_id_persisted", False))
    endpoint_classification = str(request.get("endpoint_classification", ""))
    order_execution_requested = bool(request.get("order_execution_requested", False))
    network_requested = bool(request.get("network_requested", False))
    single_micro_trade_scope = bool(request.get("single_micro_trade_scope", False))

    readiness_ready = bool(readiness_payload.get("ready", False))
    readiness_status = str(readiness_payload.get("readiness_status", ""))

    if not live_readiness:
        preflight_status = LIVE_BROKER_PREFLIGHT_INVALID
        blockers.append("live_readiness_missing")
    elif readiness_status != LIVE_READINESS_READY or not readiness_ready:
        preflight_status = LIVE_BROKER_PREFLIGHT_INVALID
        blockers.append("live_readiness_not_ready")
    elif not live_connection_request:
        preflight_status = LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED
        blockers.append("request_missing")
    elif not operator_approved:
        preflight_status = LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED
        blockers.append("operator_approval_missing")
    elif endpoint_classification != LIVE_BROKER_EXCEPTION_CLASSIFICATION:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("endpoint_not_live_exception_approved")
    elif credentials_persisted:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("credentials_persisted_blocked")
    elif account_id_persisted:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("account_id_persisted_blocked")
    elif order_execution_requested:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("order_execution_request_blocked")
    elif single_micro_trade_scope is not True:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("single_micro_trade_scope_required")
    elif credentials_runtime_only is not True:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("credentials_runtime_only_required")
    elif not live_exception_mode:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("live_exception_mode_required")
    elif not read_only_first:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("read_only_first_scope_required")
    elif network_requested and not operator_approved:
        preflight_status = LIVE_BROKER_PREFLIGHT_BLOCKED
        blockers.append("network_requested_without_operator_approval")
    else:
        preflight_status = LIVE_BROKER_PREFLIGHT_READY

    return {
        "preflight_schema": "AIOS_LIVE_BROKER_PREFLIGHT_V11.v1",
        "preflight_status": preflight_status,
        "ready": preflight_status == LIVE_BROKER_PREFLIGHT_READY,
        "blockers": tuple(blockers),
        "sanitized_connection_plan": {
            "live_exception_mode": live_exception_mode,
            "read_only_first": read_only_first,
            "endpoint_classification": endpoint_classification,
            "single_micro_trade_scope": single_micro_trade_scope,
            "credentials_runtime_only": credentials_runtime_only,
            "credentials_persisted": False,
            "account_id_persisted": False,
            "order_execution_requested": order_execution_requested,
            "network_requested": network_requested,
            "operator_approved": operator_approved,
        },
        "safety_summary": {
            "order_executed": False,
            "broker_call_performed": False,
            "no_credential_persistence": True,
            "no_default_network": True,
            "no_live_execution": False,
            "safety_only_review_mode": read_only_first,
        },
        "next_safe_action": _live_preflight_next_action(preflight_status),
        "latency_budget": {
            "readiness_read_ms": readiness_read_ms,
            "request_read_ms": request_read_ms,
            "preflight_mapping_ms": _ms(request_start, time.perf_counter()),
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _ms(start, time.perf_counter()),
        },
    }


def build_live_micro_trade_arming_packet(
    live_preflight: Mapping[str, Any] | None,
    trade_intent: Mapping[str, Any] | None = None,
    approval: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    preflight = dict(live_preflight or {})
    preflight_start = time.perf_counter()
    preflight_read_ms = _ms(preflight_start, time.perf_counter())

    trade = dict(trade_intent or {})
    trade_start = time.perf_counter()
    trade_eval_ms = _ms(trade_start, time.perf_counter())

    approval_payload = dict(approval or {})
    approval_start = time.perf_counter()
    approval_read_ms = _ms(approval_start, time.perf_counter())

    blockers: list[str] = []

    side = str(trade.get("side", "")).upper()
    units = _coerce_positive_int(trade.get("units"))
    risk_cap = _coerce_positive_int(trade.get("risk_cap"))
    stop_loss = trade.get("stop_loss")
    take_profit = trade.get("take_profit")
    live_exception_only = bool(trade.get("live_exception_only", False))
    single_trade_only = bool(trade.get("single_trade_only", False))
    micro_size_only = bool(trade.get("micro_size_only", False))
    kill_switch_enabled = bool(trade.get("kill_switch_enabled", False))
    max_loss_gate_clear = bool(trade.get("max_loss_gate_clear", False))
    daily_stop_clear = bool(trade.get("daily_stop_clear", False))
    protected_action_auth_passed = bool(approval_payload.get("protected_action_auth_passed", False))

    approval_fields = {
        "human_approved_live_micro_trade": bool(approval_payload.get("human_approved_live_micro_trade", False)),
        "authenticated_operator": bool(approval_payload.get("authenticated_operator", False)),
        "understands_loss_risk_ack": bool(approval_payload.get("understands_loss_risk_ack", False)),
        "single_trade_ack": bool(approval_payload.get("single_trade_ack", False)),
        "no_revenge_trade_ack": bool(approval_payload.get("no_revenge_trade_ack", False)),
        "stop_after_execution_ack": bool(approval_payload.get("stop_after_execution_ack", False)),
        "protected_action_auth_passed": protected_action_auth_passed,
    }

    preflight_ready = bool(preflight.get("ready", False))
    preflight_status = str(preflight.get("preflight_status", ""))

    if not live_preflight:
        arming_status = LIVE_MICRO_TRADE_INVALID
        blockers.append("live_preflight_missing")
    elif preflight_status != LIVE_BROKER_PREFLIGHT_READY or not preflight_ready:
        arming_status = LIVE_MICRO_TRADE_INVALID
        blockers.append("live_preflight_not_ready")
    elif not approval:
        arming_status = LIVE_MICRO_TRADE_REVIEW_REQUIRED
        blockers.append("approval_missing")
    elif not all(approval_fields.values()):
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("approval_gate_failed")
    elif side not in {"BUY", "SELL"}:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("invalid_side")
    elif units <= 0:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("units_not_positive")
    elif units > LIVE_MICRO_UNITS_MAX:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("units_above_micro_policy")
    elif risk_cap <= 0:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("risk_cap_not_positive")
    elif kill_switch_enabled:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("kill_switch_enabled")
    elif not max_loss_gate_clear:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("max_loss_gate_not_clear")
    elif not daily_stop_clear:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("daily_stop_not_clear")
    elif stop_loss is None or take_profit is None:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("stop_or_take_profit_missing")
    elif not live_exception_only or not single_trade_only or not micro_size_only:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("live_exception_single_micro_scope_required")
    elif not protected_action_auth_passed:
        arming_status = LIVE_MICRO_TRADE_BLOCKED
        blockers.append("protected_action_auth_failed")
    else:
        arming_status = LIVE_MICRO_TRADE_ARMED

    sanitized_trade = _sanitize_trade_input(trade)

    return {
        "arming_schema": "AIOS_LIVE_MICRO_TRADE_ARMING_V12.v1",
        "arming_status": arming_status,
        "ready": arming_status == LIVE_MICRO_TRADE_ARMED,
        "blockers": tuple(blockers),
        "sanitized_trade_intent": sanitized_trade,
        "approval_summary": approval_fields,
        "safety_summary": {
            "order_executed": False,
            "broker_call_performed": False,
            "no_credential_persistence": True,
            "no_default_network": True,
            "order_size_ok": units <= LIVE_MICRO_UNITS_MAX,
            "no_live_execution": False,
        },
        "next_safe_action": _live_arming_next_action(arming_status),
        "latency_budget": {
            "preflight_read_ms": preflight_read_ms,
            "trade_eval_ms": trade_eval_ms,
            "approval_read_ms": approval_read_ms,
            "mapping_ms": _ms(approval_start, time.perf_counter()),
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _ms(start, time.perf_counter()),
        },
    }


def build_live_order_execution_command_contract(
    arming_packet: Mapping[str, Any] | None,
    final_operator_command: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    arming_payload = dict(arming_packet or {})
    arming_start = time.perf_counter()
    arming_read_ms = _ms(arming_start, time.perf_counter())

    command = dict(final_operator_command or {})
    command_start = time.perf_counter()
    command_eval_ms = _ms(command_start, time.perf_counter())

    blockers: list[str] = []
    required_fields = (
        "final_execute_live_order_command",
        "confirmed_one_trade_only",
        "confirmed_micro_size",
        "confirmed_stop_loss",
        "confirmed_take_profit",
        "confirmed_risk_cap",
        "confirmed_no_default_network",
        "confirmed_manual_operator_presence",
    )

    command_ok = all(bool(command.get(field, False)) for field in required_fields)

    arming_ready = bool(arming_payload.get("ready", False))
    arming_status = str(arming_payload.get("arming_status", ""))

    if not arming_packet:
        command_status = LIVE_ORDER_COMMAND_INVALID
        blockers.append("arming_packet_missing")
    elif arming_status != LIVE_MICRO_TRADE_ARMED or not arming_ready:
        command_status = LIVE_ORDER_COMMAND_INVALID
        blockers.append("arming_not_ready")
    elif not final_operator_command:
        command_status = LIVE_ORDER_COMMAND_REVIEW_REQUIRED
        blockers.append("final_operator_command_missing")
    elif not command_ok:
        command_status = LIVE_ORDER_COMMAND_BLOCKED
        blockers.append("final_operator_command_incomplete")
    else:
        command_status = LIVE_ORDER_COMMAND_READY

    return {
        "command_schema": "AIOS_LIVE_ORDER_COMMAND_V13.v1",
        "command_status": command_status,
        "ready": command_status == LIVE_ORDER_COMMAND_READY,
        "blockers": tuple(blockers),
        "packet_summary": {
            "command_ready": command_status == LIVE_ORDER_COMMAND_READY,
            "final_execute_live_order_command": bool(command.get("final_execute_live_order_command", False)),
            "confirmed_one_trade_only": bool(command.get("confirmed_one_trade_only", False)),
            "confirmed_micro_size": bool(command.get("confirmed_micro_size", False)),
            "confirmed_stop_loss": bool(command.get("confirmed_stop_loss", False)),
            "confirmed_take_profit": bool(command.get("confirmed_take_profit", False)),
            "confirmed_risk_cap": bool(command.get("confirmed_risk_cap", False)),
        },
        "sanitized_summary": {
            "confirmed_no_default_network": bool(command.get("confirmed_no_default_network", False)),
            "confirmed_manual_operator_presence": bool(command.get("confirmed_manual_operator_presence", False)),
        },
        "safety_summary": {
            "order_executed": False,
            "broker_call_performed": False,
            "no_credential_persistence": True,
            "no_default_network": bool(command.get("confirmed_no_default_network", False)),
            "order_execution_required": True,
            "no_live_execution": False,
        },
        "next_safe_action": _live_order_command_next_action(command_status),
        "latency_budget": {
            "arming_read_ms": arming_read_ms,
            "command_eval_ms": command_eval_ms,
            "mapping_ms": _ms(command_start, time.perf_counter()),
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _ms(start, time.perf_counter()),
        },
    }


def build_operator_login_portal_contract(config: Mapping[str, Any] | None = None) -> dict[str, Any]:
    start = time.perf_counter()

    provider_input = dict(config or {}).get("providers", {})
    cloudflare_input = dict(config or {}).get("cloudflare", {})

    providers = []
    providers_missing: list[str] = []
    providers_blocked: list[str] = []

    default_providers = {
        "github": {
            "provider_name": "GitHub",
            "oauth_enabled": True,
            "client_id_runtime_configured": True,
            "client_secret_persisted": False,
            "redirect_uri_registered": True,
            "scopes": ("read:org", "read:user"),
            "allowed_for_operator_login": True,
        },
        "google": {
            "provider_name": "Google",
            "oauth_enabled": True,
            "client_id_runtime_configured": True,
            "client_secret_persisted": False,
            "redirect_uri_registered": True,
            "scopes": ("openid", "email", "profile"),
            "allowed_for_operator_login": True,
        },
        "microsoft": {
            "provider_name": "Microsoft",
            "oauth_enabled": True,
            "client_id_runtime_configured": True,
            "client_secret_persisted": False,
            "redirect_uri_registered": True,
            "scopes": ("email", "offline_access"),
            "allowed_for_operator_login": True,
        },
    }

    for key, defaults in default_providers.items():
        provided = provider_input.get(key, {})
        if provided:
            providers.append(
                {
                    "provider_name": defaults["provider_name"],
                    "oauth_enabled": bool(provided.get("oauth_enabled", defaults["oauth_enabled"])),
                    "client_id_runtime_configured": bool(
                        provided.get("client_id_runtime_configured", defaults["client_id_runtime_configured"])
                    ),
                    "client_secret_persisted": bool(
                        provided.get("client_secret_persisted", defaults["client_secret_persisted"])
                    ),
                    "redirect_uri_registered": bool(
                        provided.get("redirect_uri_registered", defaults["redirect_uri_registered"])
                    ),
                    "scopes": tuple(provided.get("scopes", defaults["scopes"])),
                    "allowed_for_operator_login": bool(
                        provided.get("allowed_for_operator_login", defaults["allowed_for_operator_login"])
                    ),
                }
            )
            if providers[-1]["client_secret_persisted"]:
                providers_blocked.append(f"{key}_secret_persistence_not_allowed")
        else:
            providers.append(dict(defaults))
            providers_missing.append(f"{key}_provider_missing")

    cloudflare = {
        "cloudflare_turnstile_required": bool(
            cloudflare_input.get("cloudflare_turnstile_required", True)
        ),
        "human_challenge_required": bool(cloudflare_input.get("human_challenge_required", True)),
        "bot_detection_required": bool(cloudflare_input.get("bot_detection_required", True)),
        "bypass_allowed": bool(cloudflare_input.get("bypass_allowed", False)),
    }

    blockers: list[str] = []
    if providers_blocked:
        blockers.extend(providers_blocked)
    if providers_missing:
        blockers.extend(providers_missing)
    if not cloudflare["cloudflare_turnstile_required"]:
        blockers.append("cloudflare_turnstile_required_false")
    if not cloudflare["human_challenge_required"]:
        blockers.append("human_challenge_required_false")
    if not cloudflare["bot_detection_required"]:
        blockers.append("bot_detection_required_false")
    if cloudflare["bypass_allowed"]:
        blockers.append("cloudflare_bypass_allowed_blocked")

    if blockers:
        portal_status = OPERATOR_LOGIN_PORTAL_BLOCKED
    else:
        portal_status = OPERATOR_LOGIN_PORTAL_READY

    if not config:
        portal_status = OPERATOR_LOGIN_PORTAL_READY
    if "providers" in dict(config or {}) and not provider_input:
        portal_status = OPERATOR_LOGIN_PORTAL_INVALID
        blockers.append("provider_payload_invalid")

    return {
        "portal_schema": "AIOS_OPERATOR_LOGIN_PORTAL_V1.v1",
        "portal_status": portal_status,
        "ready": portal_status == OPERATOR_LOGIN_PORTAL_READY,
        "blockers": tuple(blockers),
        "sanitized_summary": {
            "providers": providers,
            "cloudflare_gate": cloudflare,
            "provider_set_complete": len(providers_missing) == 0,
        },
        "safety_summary": {
            "order_executed": False,
            "broker_call_performed": False,
            "no_credential_persistence": True,
            "no_default_network": True,
            "oauth_secret_handled": False,
            "no_live_execution": False,
        },
        "next_safe_action": _login_portal_next_action(portal_status),
        "latency_budget": {
            "providers_eval_ms": _ms(start, time.perf_counter()),
            "cloudflare_eval_ms": _ms(start, time.perf_counter()),
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _ms(start, time.perf_counter()),
        },
    }


def build_protected_live_action_auth_gate(
    login_contract: Mapping[str, Any] | None,
    action_request: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    start = time.perf_counter()

    contract = dict(login_contract or {})
    contract_start = time.perf_counter()
    contract_read_ms = _ms(contract_start, time.perf_counter())

    action_payload = dict(action_request or {})
    action_start = time.perf_counter()
    action_eval_ms = _ms(action_start, time.perf_counter())

    blockers: list[str] = []

    provider = str(action_payload.get("provider", "")).lower()
    operator_authenticated = bool(action_payload.get("operator_authenticated", False))
    cloudflare_human_challenge_passed = bool(
        action_payload.get("cloudflare_human_challenge_passed", False)
    )
    bot_detection_passed = bool(action_payload.get("bot_detection_passed", False))
    protected_action = str(action_payload.get("protected_action", ""))
    reauth_completed = bool(action_payload.get("reauth_completed", False))
    operator_approval_recorded = bool(action_payload.get("operator_approval_recorded", False))

    if not login_contract:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_INVALID
        blockers.append("login_contract_missing")
    elif str(contract.get("portal_status", "")) != OPERATOR_LOGIN_PORTAL_READY:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_INVALID
        blockers.append("login_contract_not_ready")
    elif not action_request:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_REVIEW_REQUIRED
        blockers.append("action_request_missing")
    elif provider not in SUPPORTED_LOGIN_PROVIDERS:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("unsupported_provider")
    elif not cloudflare_human_challenge_passed:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("human_challenge_not_passed")
    elif not bot_detection_passed:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("bot_detection_failed")
    elif not operator_authenticated:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("operator_not_authenticated")
    elif not reauth_completed:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("reauth_not_completed")
    elif protected_action not in SUPPORTED_PROTECTED_ACTIONS:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("unsupported_protected_action")
    elif not operator_approval_recorded:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_BLOCKED
        blockers.append("operator_approval_not_recorded")
    else:
        gate_status = PROTECTED_LIVE_ACTION_AUTH_READY

    return {
        "auth_gate_schema": "AIOS_PROTECTED_LIVE_ACTION_AUTH_GATE_V1.v1",
        "auth_gate_status": gate_status,
        "ready": gate_status == PROTECTED_LIVE_ACTION_AUTH_READY,
        "blockers": tuple(blockers),
        "sanitized_summary": {
            "provider": provider,
            "protected_action": protected_action,
            "operator_authenticated": operator_authenticated,
            "cloudflare_human_challenge_passed": cloudflare_human_challenge_passed,
            "bot_detection_passed": bot_detection_passed,
            "reauth_completed": reauth_completed,
            "operator_approval_recorded": operator_approval_recorded,
        },
        "safety_summary": {
            "order_executed": False,
            "broker_call_performed": False,
            "no_credential_persistence": True,
            "no_default_network": True,
            "oauth_secret_handled": False,
            "no_live_execution": False,
        },
        "next_safe_action": _protected_action_gate_next_action(gate_status),
        "latency_budget": {
            "login_contract_read_ms": contract_read_ms,
            "action_request_eval_ms": action_eval_ms,
            "mapping_ms": _ms(action_start, time.perf_counter()),
            "network_latency_ms": "excluded_offline_default",
            "total_ms": _ms(start, time.perf_counter()),
        },
    }


def _safe_copy(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _sanitize_trade_input(trade_intent: Mapping[str, Any]) -> dict[str, Any]:
    forbidden = {
        "credential",
        "credentials",
        "account_id",
        "broker_order_id",
        "raw_payload",
        "raw_response",
        "secret",
        "token",
        "password",
    }
    sanitized: dict[str, Any] = {}
    for key, value in trade_intent.items():
        if str(key).lower() in forbidden:
            continue
        sanitized[str(key)] = value
    return sanitized


def _coerce_positive_int(value: Any) -> int:
    try:
        as_int = int(value)
    except (TypeError, ValueError):
        return 0
    return as_int if as_int > 0 else 0


def _ms(start: float, end: float) -> float:
    return (end - start) * 1000.0


def _live_readiness_next_action(status: str) -> str:
    return {
        LIVE_READINESS_READY: "prepare_live_broker_connection_preflight",
        LIVE_READINESS_BLOCKED: "resolve_live_readiness_blockers",
        LIVE_READINESS_INVALID: "repair_live_readiness_inputs",
        LIVE_READINESS_REVIEW_REQUIRED: "complete_live_readiness_operator_acknowledgment",
    }.get(status, "complete_live_readiness_operator_acknowledgment")


def _live_preflight_next_action(status: str) -> str:
    return {
        LIVE_BROKER_PREFLIGHT_READY: "prepare_live_micro_trade_arming_packet",
        LIVE_BROKER_PREFLIGHT_BLOCKED: "resolve_live_broker_preflight_blockers",
        LIVE_BROKER_PREFLIGHT_INVALID: "repair_live_readiness_packet",
        LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED: "obtain_operator_live_preflight_approval",
    }.get(status, "obtain_operator_live_preflight_approval")


def _live_arming_next_action(status: str) -> str:
    return {
        LIVE_MICRO_TRADE_ARMED: "route_to_final_live_order_command_contract",
        LIVE_MICRO_TRADE_BLOCKED: "resolve_live_micro_trade_arming_blockers",
        LIVE_MICRO_TRADE_INVALID: "repair_live_broker_preflight_packet",
        LIVE_MICRO_TRADE_REVIEW_REQUIRED: "obtain_live_micro_trade_human_approval",
    }.get(status, "obtain_live_micro_trade_human_approval")


def _live_order_command_next_action(status: str) -> str:
    return {
        LIVE_ORDER_COMMAND_READY: "await_separate_explicit_runtime_order_executor_packet",
        LIVE_ORDER_COMMAND_BLOCKED: "resolve_live_order_command_blockers",
        LIVE_ORDER_COMMAND_INVALID: "repair_live_arming_packet",
        LIVE_ORDER_COMMAND_REVIEW_REQUIRED: "obtain_final_live_execution_command",
    }.get(status, "obtain_final_live_execution_command")


def _login_portal_next_action(status: str) -> str:
    return {
        OPERATOR_LOGIN_PORTAL_READY: "route_protected_action_auth_gate",
        OPERATOR_LOGIN_PORTAL_BLOCKED: "repair_login_portal_contract",
        OPERATOR_LOGIN_PORTAL_INVALID: "repair_login_portal_inputs",
        OPERATOR_LOGIN_PORTAL_REVIEW_REQUIRED: "collect_login_contract_inputs",
    }.get(status, "collect_login_contract_inputs")


def _protected_action_gate_next_action(status: str) -> str:
    return {
        PROTECTED_LIVE_ACTION_AUTH_READY: "proceed_live_governance_lane",
        PROTECTED_LIVE_ACTION_AUTH_BLOCKED: "resolve_live_action_auth_blockers",
        PROTECTED_LIVE_ACTION_AUTH_INVALID: "repair_login_portal_or_action_request",
        PROTECTED_LIVE_ACTION_AUTH_REVIEW_REQUIRED: "collect_live_action_auth_request",
    }.get(status, "collect_live_action_auth_request")

