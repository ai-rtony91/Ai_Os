from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_bid_ask_sltp_validation_v1 import (
    BID_ASK_SLTP_VALIDATION_READY,
    BLOCKED_BY_INVALID_NUMERIC_INPUT,
    BLOCKED_BY_MISSING_BID_ASK,
    evaluate_oanda_demo_bid_ask_sltp_validation_v1,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-BID-ASK-CORRECTED-RUNTIME-PACKET-V1"
RUNTIME_PACKET_VERSION = "v1"

BID_ASK_CORRECTED_RUNTIME_PACKET_READY = "BID_ASK_CORRECTED_RUNTIME_PACKET_READY"
BLOCKED_BY_BID_ASK_VALIDATION = "BLOCKED_BY_BID_ASK_VALIDATION"
BLOCKED_BY_INVALID_BID_ASK = "BLOCKED_BY_INVALID_BID_ASK"
BLOCKED_BY_INVALID_TRADE_INTENT = "BLOCKED_BY_INVALID_TRADE_INTENT"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

APPROVED_INSTRUMENT = "EUR_USD"
ALLOWED_DIRECTIONS = ("BUY", "SELL")
APPROVED_UNITS = 1
APPROVED_ORDER_TYPE = "MARKET"
DEFAULT_CLIENT_ORDER_ID = "AIOS-DEMO-BIDASK-CORRECTED-OWNER-RUNTIME-001"
DEFAULT_RISK_AMOUNT = "1.00"

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "order_mutation_allowed",
    "position_mutation_allowed",
)


def default_oanda_demo_bid_ask_corrected_runtime_packet_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "units": APPROVED_UNITS,
        "bid": "",
        "ask": "",
        "stop_loss": "",
        "take_profit": "",
        "min_distance_pips": "2",
        "pip_size": "0.0001",
        "risk_amount": DEFAULT_RISK_AMOUNT,
        "client_order_id": DEFAULT_CLIENT_ORDER_ID,
        "order_type": APPROVED_ORDER_TYPE,
        "bid_ask_sltp_validation_ready_confirmed": False,
        "demo_only_confirmed": False,
        "owner_manual_runtime_only_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_autonomous_order_confirmed": False,
        "post_trade_evidence_required_confirmed": False,
        "no_profit_claim_confirmed": False,
        "live_endpoint_requested": False,
        "autonomous_order_requested": False,
        "scheduler_requested": False,
        "daemon_requested": False,
        "webhook_requested": False,
        "profit_claim_made": False,
    }


def build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
    runtime_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = _normalize_context(runtime_context)
    validation = _bid_ask_validation_result(normalized)
    blockers = _blockers(normalized, validation)
    classification = _classification(blockers)
    packet_ready = classification == BID_ASK_CORRECTED_RUNTIME_PACKET_READY
    return {
        "packet_id": PACKET_ID,
        "runtime_packet_version": RUNTIME_PACKET_VERSION,
        "script_status": classification,
        "classification": classification,
        "runtime_packet_ready": packet_ready,
        "blockers": blockers,
        "prior_cancel_evidence": {
            "first_owner_run_cancel_reason": "TAKE_PROFIT_ON_FILL_LOSS",
            "corrected_future_cancel_reason": "TAKE_PROFIT_ON_FILL_LOSS",
            "corrected_future_order_create_transaction_id": "315",
            "corrected_future_order_cancel_transaction_id": "316",
            "order_fill_transaction_observed": False,
            "fill_claimed": False,
            "profit_claimed": False,
        },
        "bid_ask_validation_evidence": {
            "required_classification": BID_ASK_SLTP_VALIDATION_READY,
            "observed_classification": validation.get("classification"),
            "validation_ready": validation.get("validation_ready", False),
            "broker_quote_lookup_performed": False,
            "live_market_data_read": False,
        },
        "runtime_packet": {
            "owner_only": True,
            "owner_command_template": _owner_transport_command_template(normalized)
            if packet_ready
            else None,
            "vault_backed_transport_only": True,
            "codex_execution_authorized": False,
            "order_authorized_for_codex": False,
            "broker_command_run_by_codex": False,
            "post_trade_evidence_required": True,
        },
        "input_summary": {
            "instrument": normalized["instrument"],
            "direction": normalized["direction"],
            "units": _decimal_text(normalized["units"]),
            "bid": _decimal_text(normalized["bid"]),
            "ask": _decimal_text(normalized["ask"]),
            "stop_loss": _decimal_text(normalized["stop_loss"]),
            "take_profit": _decimal_text(normalized["take_profit"]),
            "min_distance": _decimal_text(_minimum_distance(normalized)),
            "risk_amount": _decimal_text(normalized["risk_amount"]),
            "client_order_id": normalized["client_order_id"],
            "order_type": normalized["order_type"],
        },
        "runtime_rules": {
            "buy_rule": "stop_loss <= bid - minimum_distance and take_profit >= ask + minimum_distance",
            "sell_rule": "stop_loss >= ask + minimum_distance and take_profit <= bid - minimum_distance",
            "buy_executable_entry_side": "ask",
            "sell_executable_entry_side": "bid",
        },
        "safety_boundaries": {
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "vault_read_performed": False,
            "environment_read_performed": False,
            "dotenv_read_performed": False,
            "token_argument_supported": False,
            "account_id_argument_supported": False,
            "live_endpoint_used": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
            "profit_claimed": False,
            "fill_claimed": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(classification),
    }


def _normalize_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    defaults = default_oanda_demo_bid_ask_corrected_runtime_packet_context_v1()
    supplied = context if isinstance(context, Mapping) else {}
    merged = {**defaults, **dict(supplied)}
    return {
        "instrument": _text(merged.get("instrument")).upper(),
        "direction": _text(merged.get("direction")).upper(),
        "units": _decimal_or_none(merged.get("units")),
        "bid": _decimal_or_none(merged.get("bid")),
        "ask": _decimal_or_none(merged.get("ask")),
        "stop_loss": _decimal_or_none(merged.get("stop_loss")),
        "take_profit": _decimal_or_none(merged.get("take_profit")),
        "min_distance_pips": _decimal_or_none(merged.get("min_distance_pips")),
        "pip_size": _decimal_or_none(merged.get("pip_size")),
        "risk_amount": _decimal_or_none(merged.get("risk_amount")),
        "client_order_id": _text(merged.get("client_order_id")),
        "order_type": _text(merged.get("order_type")).upper(),
        "bid_ask_sltp_validation_ready_confirmed": _bool(
            merged.get("bid_ask_sltp_validation_ready_confirmed")
        ),
        "demo_only_confirmed": _bool(merged.get("demo_only_confirmed")),
        "owner_manual_runtime_only_confirmed": _bool(
            merged.get("owner_manual_runtime_only_confirmed")
        ),
        "no_live_endpoint_confirmed": _bool(
            merged.get("no_live_endpoint_confirmed")
        ),
        "no_autonomous_order_confirmed": _bool(
            merged.get("no_autonomous_order_confirmed")
        ),
        "post_trade_evidence_required_confirmed": _bool(
            merged.get("post_trade_evidence_required_confirmed")
        ),
        "no_profit_claim_confirmed": _bool(merged.get("no_profit_claim_confirmed")),
        "live_endpoint_requested": _bool(merged.get("live_endpoint_requested")),
        "autonomous_order_requested": _bool(merged.get("autonomous_order_requested")),
        "scheduler_requested": _bool(merged.get("scheduler_requested")),
        "daemon_requested": _bool(merged.get("daemon_requested")),
        "webhook_requested": _bool(merged.get("webhook_requested")),
        "profit_claim_made": _bool(merged.get("profit_claim_made")),
    }


def _bid_ask_validation_result(normalized: Mapping[str, Any]) -> Mapping[str, Any]:
    return evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        {
            "instrument": normalized["instrument"],
            "direction": normalized["direction"],
            "bid": _decimal_text(normalized["bid"]),
            "ask": _decimal_text(normalized["ask"]),
            "stop_loss": _decimal_text(normalized["stop_loss"]),
            "take_profit": _decimal_text(normalized["take_profit"]),
            "min_distance_pips": _decimal_text(normalized["min_distance_pips"]),
            "pip_size": _decimal_text(normalized["pip_size"]),
            "demo_only_confirmed": normalized["demo_only_confirmed"],
            "no_broker_call_confirmed": True,
            "no_order_confirmed": True,
            "no_live_endpoint_confirmed": normalized["no_live_endpoint_confirmed"],
            "no_profit_claim_confirmed": normalized["no_profit_claim_confirmed"],
            "live_endpoint_requested": normalized["live_endpoint_requested"],
            "profit_claim_made": normalized["profit_claim_made"],
        }
    )


def _blockers(
    normalized: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []

    def add(classification: str, message: str) -> None:
        blockers.append(f"{classification}:{message}")

    if normalized["live_endpoint_requested"] or not normalized["no_live_endpoint_confirmed"]:
        add(BLOCKED_BY_LIVE_ENDPOINT, "no_live_endpoint_required")

    if (
        normalized["autonomous_order_requested"]
        or normalized["scheduler_requested"]
        or normalized["daemon_requested"]
        or normalized["webhook_requested"]
        or not normalized["owner_manual_runtime_only_confirmed"]
        or not normalized["no_autonomous_order_confirmed"]
        or not normalized["post_trade_evidence_required_confirmed"]
    ):
        add(
            BLOCKED_BY_AUTONOMY_REQUEST,
            "owner_manual_runtime_only_and_post_trade_evidence_required",
        )

    if normalized["profit_claim_made"] or not normalized["no_profit_claim_confirmed"]:
        add(BLOCKED_BY_PROFIT_CLAIM, "no_profit_claim_required")

    if not _valid_trade_intent(normalized):
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "invalid_runtime_trade_intent")

    validation_classification = validation.get("classification")
    if validation_classification in (
        BLOCKED_BY_MISSING_BID_ASK,
        BLOCKED_BY_INVALID_NUMERIC_INPUT,
    ):
        add(BLOCKED_BY_INVALID_BID_ASK, str(validation_classification))

    if (
        not normalized["bid_ask_sltp_validation_ready_confirmed"]
        or validation.get("validation_ready") is not True
        or validation_classification != BID_ASK_SLTP_VALIDATION_READY
    ):
        add(BLOCKED_BY_BID_ASK_VALIDATION, "bid_ask_sltp_validation_ready_required")

    return _unique(blockers)


def _classification(blockers: list[str]) -> str:
    for classification in (
        BLOCKED_BY_LIVE_ENDPOINT,
        BLOCKED_BY_AUTONOMY_REQUEST,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_INVALID_TRADE_INTENT,
        BLOCKED_BY_INVALID_BID_ASK,
        BLOCKED_BY_BID_ASK_VALIDATION,
    ):
        if any(blocker.startswith(f"{classification}:") for blocker in blockers):
            return classification
    return BID_ASK_CORRECTED_RUNTIME_PACKET_READY


def _valid_trade_intent(normalized: Mapping[str, Any]) -> bool:
    return (
        normalized["demo_only_confirmed"]
        and normalized["instrument"] == APPROVED_INSTRUMENT
        and normalized["direction"] in ALLOWED_DIRECTIONS
        and normalized["units"] == Decimal(str(APPROVED_UNITS))
        and normalized["order_type"] == APPROVED_ORDER_TYPE
        and _positive_decimal(normalized["risk_amount"])
        and _sanitized_client_order_id(normalized["client_order_id"])
    )


def _minimum_distance(normalized: Mapping[str, Any]) -> Decimal | None:
    min_distance_pips = normalized["min_distance_pips"]
    pip_size = normalized["pip_size"]
    if not isinstance(min_distance_pips, Decimal):
        return None
    if not isinstance(pip_size, Decimal):
        return None
    return min_distance_pips * pip_size


def _owner_transport_command_template(normalized: Mapping[str, Any]) -> str:
    return " ".join(
        [
            "python",
            "scripts/forex_delivery/run_oanda_demo_vault_backed_one_order_transport_v1.py",
            "--execute-vault-backed-demo-one-order",
            "--instrument",
            normalized["instrument"],
            "--direction",
            normalized["direction"],
            "--units",
            _decimal_text(normalized["units"]),
            "--stop-loss",
            _decimal_text(normalized["stop_loss"]),
            "--take-profit",
            _decimal_text(normalized["take_profit"]),
            "--risk-amount",
            _decimal_text(normalized["risk_amount"]),
            "--client-order-id",
            normalized["client_order_id"],
            "--order-type",
            normalized["order_type"],
            "--i-confirm-demo-only",
            "--i-confirm-vault-backed-runtime-only",
            "--i-confirm-one-order-only",
            "--i-confirm-owner-manual-runtime-only",
            "--i-confirm-stop-loss",
            "--i-confirm-take-profit",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-autonomous-order",
            "--i-confirm-no-second-order",
            "--i-confirm-post-trade-evidence",
            "--i-confirm-kill-switch-ready",
            "--i-understand-loss-possible",
            "--i-understand-no-profit-guarantee",
        ]
    )


def _next_safe_action(classification: str) -> str:
    return {
        BID_ASK_CORRECTED_RUNTIME_PACKET_READY: (
            "owner_may_review_template_and_manually_run_existing_vault_backed_transport_if_intended"
        ),
        BLOCKED_BY_BID_ASK_VALIDATION: (
            "repair_bid_ask_sltp_validation_before_runtime_packet"
        ),
        BLOCKED_BY_INVALID_BID_ASK: "provide_valid_current_bid_ask_and_sltp_values",
        BLOCKED_BY_INVALID_TRADE_INTENT: "repair_runtime_trade_intent",
        BLOCKED_BY_LIVE_ENDPOINT: "remove_live_endpoint_request",
        BLOCKED_BY_AUTONOMY_REQUEST: "preserve_owner_manual_runtime_only_boundary",
        BLOCKED_BY_PROFIT_CLAIM: "remove_profit_or_campaign_claim",
    }.get(classification, "stop_and_review_bid_ask_corrected_runtime_packet")


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _decimal_or_none(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, Decimal):
        return value if value.is_finite() else None
    if isinstance(value, (int, float)):
        try:
            decimal = Decimal(str(value))
        except InvalidOperation:
            return None
        return decimal if decimal.is_finite() else None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            decimal = Decimal(stripped)
        except InvalidOperation:
            return None
        return decimal if decimal.is_finite() else None
    return None


def _positive_decimal(value: Any) -> bool:
    return isinstance(value, Decimal) and value.is_finite() and value > 0


def _decimal_text(value: Any) -> str:
    if not isinstance(value, Decimal):
        return "INVALID"
    return format(value, "f")


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _bool(value: Any) -> bool:
    return value is True


def _sanitized_client_order_id(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    client_order_id = value.strip()
    if not client_order_id or client_order_id != value:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:")
    return all(character in allowed for character in client_order_id)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
