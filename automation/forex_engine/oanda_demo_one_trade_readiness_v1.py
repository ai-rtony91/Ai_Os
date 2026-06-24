from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-ONE-TRADE-READINESS-V1"
READINESS_VERSION = "v1"

READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE = (
    "READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE"
)
BLOCKED_BY_PREFLIGHT = "BLOCKED_BY_PREFLIGHT"
BLOCKED_BY_RISK_GATE = "BLOCKED_BY_RISK_GATE"
BLOCKED_BY_KILL_SWITCH = "BLOCKED_BY_KILL_SWITCH"
BLOCKED_BY_ORDER_CAP = "BLOCKED_BY_ORDER_CAP"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

READINESS_CLASSIFICATIONS = (
    READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE,
    BLOCKED_BY_PREFLIGHT,
    BLOCKED_BY_RISK_GATE,
    BLOCKED_BY_KILL_SWITCH,
    BLOCKED_BY_ORDER_CAP,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_PROFIT_CLAIM,
)

READINESS_FIELDS = (
    "demo_only_confirmed",
    "read_only_preflight_passed",
    "owner_runtime_command_required",
    "broker_call_not_performed_by_codex",
    "instrument_allowed",
    "eur_usd_available",
    "direction_allowed",
    "micro_units_present",
    "stop_loss_present",
    "take_profit_present",
    "max_loss_gate_passed",
    "daily_stop_gate_passed",
    "kill_switch_state_passed",
    "one_order_only_cap_available",
    "post_trade_evidence_plan_present",
    "result_bucket_plan_present",
    "next_allocation_plan_present",
    "compound_or_withdraw_decision_is_conditional",
    "no_live_endpoint",
    "no_scheduler_daemon_webhook",
    "no_profit_claim",
)

PREFLIGHT_FIELDS = (
    "demo_only_confirmed",
    "read_only_preflight_passed",
    "owner_runtime_command_required",
    "broker_call_not_performed_by_codex",
    "instrument_allowed",
    "eur_usd_available",
    "direction_allowed",
)

RISK_GATE_FIELDS = (
    "micro_units_present",
    "stop_loss_present",
    "take_profit_present",
    "max_loss_gate_passed",
    "daily_stop_gate_passed",
    "post_trade_evidence_plan_present",
    "result_bucket_plan_present",
    "next_allocation_plan_present",
)

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "broker_call_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "order_mutation_allowed",
    "position_mutation_allowed",
)


def default_oanda_demo_one_trade_readiness_context_v1() -> dict[str, bool]:
    return {
        "demo_only_confirmed": False,
        "read_only_preflight_passed": False,
        "owner_runtime_command_required": True,
        "broker_call_not_performed_by_codex": True,
        "instrument_allowed": False,
        "eur_usd_available": False,
        "direction_allowed": False,
        "micro_units_present": False,
        "stop_loss_present": False,
        "take_profit_present": False,
        "max_loss_gate_passed": False,
        "daily_stop_gate_passed": False,
        "kill_switch_state_passed": False,
        "one_order_only_cap_available": False,
        "post_trade_evidence_plan_present": False,
        "result_bucket_plan_present": False,
        "next_allocation_plan_present": False,
        "compound_or_withdraw_decision_is_conditional": True,
        "no_live_endpoint": True,
        "no_scheduler_daemon_webhook": True,
        "no_profit_claim": True,
    }


def evaluate_oanda_demo_one_trade_readiness_v1(
    readiness_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    inputs = _readiness_inputs(readiness_context)
    blockers = _readiness_blockers(inputs)
    classification = _classify_readiness(inputs)

    return {
        "packet_id": PACKET_ID,
        "readiness_version": READINESS_VERSION,
        "classification": classification,
        "readiness_ready": (
            classification == READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE
        ),
        "readiness_inputs": inputs,
        "blockers": blockers,
        "allowed_instrument": "EUR_USD" if inputs["instrument_allowed"] else None,
        "owner_runtime_boundary": {
            "owner_runtime_command_required": inputs[
                "owner_runtime_command_required"
            ],
            "codex_broker_call_allowed": False,
            "codex_order_allowed": False,
            "owner_manual_demo_only_gate_required": True,
        },
        "safety_proof": {
            "broker_call_performed_by_codex": False,
            "order_placement_performed": False,
            "orders_endpoint_called": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "credential_value_printed": False,
            "account_id_value_printed": False,
            "dotenv_read": False,
            "live_endpoint_used": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
            "profit_claim_made": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(classification),
    }


def _readiness_inputs(
    readiness_context: Mapping[str, Any] | None,
) -> dict[str, bool]:
    default_context = default_oanda_demo_one_trade_readiness_context_v1()
    context = readiness_context if isinstance(readiness_context, Mapping) else {}
    return {
        field: _bool(context.get(field, default_context[field]))
        for field in READINESS_FIELDS
    }


def _readiness_blockers(inputs: Mapping[str, bool]) -> list[str]:
    blockers: list[str] = []
    for field in READINESS_FIELDS:
        if inputs.get(field) is not True:
            blockers.append(f"{field}_required")
    return blockers


def _classify_readiness(inputs: Mapping[str, bool]) -> str:
    if all(inputs.get(field) is True for field in READINESS_FIELDS):
        return READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE
    if (
        inputs.get("no_profit_claim") is not True
        or inputs.get("compound_or_withdraw_decision_is_conditional") is not True
    ):
        return BLOCKED_BY_PROFIT_CLAIM
    if inputs.get("no_scheduler_daemon_webhook") is not True:
        return BLOCKED_BY_AUTONOMY_REQUEST
    if inputs.get("no_live_endpoint") is not True:
        return BLOCKED_BY_LIVE_ENDPOINT
    if any(inputs.get(field) is not True for field in PREFLIGHT_FIELDS):
        return BLOCKED_BY_PREFLIGHT
    if any(inputs.get(field) is not True for field in RISK_GATE_FIELDS):
        return BLOCKED_BY_RISK_GATE
    if inputs.get("kill_switch_state_passed") is not True:
        return BLOCKED_BY_KILL_SWITCH
    if inputs.get("one_order_only_cap_available") is not True:
        return BLOCKED_BY_ORDER_CAP
    return BLOCKED_BY_RISK_GATE


def _next_safe_action(classification: str) -> str:
    if classification == READY_FOR_OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE:
        return "create_owner_demo_one_trade_command_package_packet"
    if classification == BLOCKED_BY_PREFLIGHT:
        return "repair_or_recapture_read_only_preflight_evidence_before_trade_readiness"
    if classification == BLOCKED_BY_RISK_GATE:
        return "repair_micro_size_stop_loss_take_profit_or_risk_plan_before_trade_packet"
    if classification == BLOCKED_BY_KILL_SWITCH:
        return "stop_until_kill_switch_state_is_owner_reviewed_and_passed"
    if classification == BLOCKED_BY_ORDER_CAP:
        return "stop_until_one_order_only_cap_is_available"
    if classification == BLOCKED_BY_LIVE_ENDPOINT:
        return "remove_live_endpoint_before_any_demo_trade_packet"
    if classification == BLOCKED_BY_AUTONOMY_REQUEST:
        return "remove_scheduler_daemon_webhook_or_unattended_path"
    if classification == BLOCKED_BY_PROFIT_CLAIM:
        return "remove_profit_or_campaign_guarantee_claim"
    return "stop_and_review_readiness_classification"


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _bool(value: Any) -> bool:
    return value is True
