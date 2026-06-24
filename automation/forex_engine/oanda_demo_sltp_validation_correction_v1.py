from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-SLTP-VALIDATION-CORRECTION-V1"
VALIDATION_VERSION = "v1"

SLTP_VALIDATION_READY = "SLTP_VALIDATION_READY"
BLOCKED_BY_MISSING_REFERENCE_PRICE = "BLOCKED_BY_MISSING_REFERENCE_PRICE"
BLOCKED_BY_INVALID_NUMERIC_PRICE = "BLOCKED_BY_INVALID_NUMERIC_PRICE"
BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE = (
    "BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE"
)
BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE = (
    "BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE"
)
BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE = (
    "BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE"
)
BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE = (
    "BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE"
)
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_SECOND_ORDER_REQUEST = "BLOCKED_BY_SECOND_ORDER_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

APPROVED_INSTRUMENT = "EUR_USD"
ALLOWED_DIRECTIONS = ("BUY", "SELL")

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


def default_oanda_demo_sltp_validation_correction_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "reference_price": "",
        "stop_loss": "",
        "take_profit": "",
        "demo_only_confirmed": False,
        "no_broker_call_confirmed": False,
        "no_second_order_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_profit_claim_confirmed": False,
        "live_endpoint_requested": False,
        "second_order_requested": False,
        "profit_claim_made": False,
    }


def evaluate_oanda_demo_sltp_validation_correction_v1(
    validation_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = _normalize_context(validation_context)
    blockers = _blockers(normalized)
    classification = _classification(blockers)
    return {
        "packet_id": PACKET_ID,
        "validation_version": VALIDATION_VERSION,
        "classification": classification,
        "validation_ready": classification == SLTP_VALIDATION_READY,
        "blockers": blockers,
        "price_relationship": _price_relationship(normalized),
        "safety_proof": {
            "broker_call_performed": False,
            "order_placement_performed": False,
            "second_order_allowed": False,
            "live_endpoint_used": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "windows_vault_read_performed": False,
            "environment_variable_read_performed": False,
            "dotenv_read": False,
            "live_market_data_read": False,
            "profit_claim_made": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(classification),
    }


def _normalize_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    defaults = default_oanda_demo_sltp_validation_correction_context_v1()
    supplied = context if isinstance(context, Mapping) else {}
    merged = {**defaults, **dict(supplied)}
    return {
        "instrument": _text(merged.get("instrument")).upper(),
        "direction": _text(merged.get("direction")).upper(),
        "reference_price_text": _text(merged.get("reference_price")),
        "stop_loss_text": _text(merged.get("stop_loss")),
        "take_profit_text": _text(merged.get("take_profit")),
        "reference_price": _decimal_or_none(merged.get("reference_price")),
        "stop_loss": _decimal_or_none(merged.get("stop_loss")),
        "take_profit": _decimal_or_none(merged.get("take_profit")),
        "demo_only_confirmed": _bool(merged.get("demo_only_confirmed")),
        "no_broker_call_confirmed": _bool(merged.get("no_broker_call_confirmed")),
        "no_second_order_confirmed": _bool(merged.get("no_second_order_confirmed")),
        "no_live_endpoint_confirmed": _bool(
            merged.get("no_live_endpoint_confirmed")
        ),
        "no_profit_claim_confirmed": _bool(merged.get("no_profit_claim_confirmed")),
        "live_endpoint_requested": _bool(merged.get("live_endpoint_requested")),
        "second_order_requested": _bool(merged.get("second_order_requested")),
        "profit_claim_made": _bool(merged.get("profit_claim_made")),
    }


def _blockers(normalized: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    def add(classification: str, message: str) -> None:
        blockers.append(f"{classification}:{message}")

    if (
        not normalized["demo_only_confirmed"]
        or not normalized["no_broker_call_confirmed"]
        or not normalized["no_live_endpoint_confirmed"]
        or normalized["live_endpoint_requested"]
    ):
        add(BLOCKED_BY_LIVE_ENDPOINT, "demo_only_no_broker_no_live_required")

    if not normalized["no_second_order_confirmed"] or normalized["second_order_requested"]:
        add(BLOCKED_BY_SECOND_ORDER_REQUEST, "no_second_order_required")

    if not normalized["no_profit_claim_confirmed"] or normalized["profit_claim_made"]:
        add(BLOCKED_BY_PROFIT_CLAIM, "no_profit_claim_required")

    if not normalized["reference_price_text"]:
        add(BLOCKED_BY_MISSING_REFERENCE_PRICE, "reference_price_required")

    if normalized["instrument"] != APPROVED_INSTRUMENT:
        add(BLOCKED_BY_INVALID_NUMERIC_PRICE, "instrument_must_be_eur_usd")
    if normalized["direction"] not in ALLOWED_DIRECTIONS:
        add(BLOCKED_BY_INVALID_NUMERIC_PRICE, "direction_must_be_buy_or_sell")
    for field in ("reference_price", "stop_loss", "take_profit"):
        if normalized[field] is None:
            add(BLOCKED_BY_INVALID_NUMERIC_PRICE, f"{field}_must_be_numeric")
        elif normalized[field] <= Decimal("0"):
            add(BLOCKED_BY_INVALID_NUMERIC_PRICE, f"{field}_must_be_positive")

    reference_price = normalized["reference_price"]
    stop_loss = normalized["stop_loss"]
    take_profit = normalized["take_profit"]
    direction = normalized["direction"]
    if not isinstance(reference_price, Decimal):
        return _unique(blockers)
    if not isinstance(stop_loss, Decimal):
        return _unique(blockers)
    if not isinstance(take_profit, Decimal):
        return _unique(blockers)

    if direction == "BUY":
        if stop_loss >= reference_price:
            add(
                BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE,
                "buy_stop_loss_must_be_below_reference",
            )
        if take_profit <= reference_price:
            add(
                BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE,
                "buy_take_profit_must_be_above_reference",
            )
    elif direction == "SELL":
        if stop_loss <= reference_price:
            add(
                BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE,
                "sell_stop_loss_must_be_above_reference",
            )
        if take_profit >= reference_price:
            add(
                BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE,
                "sell_take_profit_must_be_below_reference",
            )
    return _unique(blockers)


def _classification(blockers: list[str]) -> str:
    for classification in (
        BLOCKED_BY_LIVE_ENDPOINT,
        BLOCKED_BY_SECOND_ORDER_REQUEST,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_MISSING_REFERENCE_PRICE,
        BLOCKED_BY_INVALID_NUMERIC_PRICE,
        BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE,
        BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE,
        BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE,
        BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE,
    ):
        if any(blocker.startswith(f"{classification}:") for blocker in blockers):
            return classification
    return SLTP_VALIDATION_READY


def _price_relationship(normalized: Mapping[str, Any]) -> dict[str, Any]:
    reference_price = normalized["reference_price"]
    stop_loss = normalized["stop_loss"]
    take_profit = normalized["take_profit"]
    return {
        "instrument": normalized["instrument"],
        "direction": normalized["direction"],
        "reference_price": _decimal_text(reference_price),
        "stop_loss": _decimal_text(stop_loss),
        "take_profit": _decimal_text(take_profit),
        "buy_stop_loss_below_reference": (
            stop_loss < reference_price
            if isinstance(stop_loss, Decimal) and isinstance(reference_price, Decimal)
            else False
        ),
        "buy_take_profit_above_reference": (
            take_profit > reference_price
            if isinstance(take_profit, Decimal)
            and isinstance(reference_price, Decimal)
            else False
        ),
        "sell_stop_loss_above_reference": (
            stop_loss > reference_price
            if isinstance(stop_loss, Decimal) and isinstance(reference_price, Decimal)
            else False
        ),
        "sell_take_profit_below_reference": (
            take_profit < reference_price
            if isinstance(take_profit, Decimal)
            and isinstance(reference_price, Decimal)
            else False
        ),
        "reference_price_owner_supplied": bool(normalized["reference_price_text"]),
        "broker_price_lookup_performed": False,
        "live_market_data_read": False,
    }


def _next_safe_action(classification: str) -> str:
    return {
        SLTP_VALIDATION_READY: (
            "owner_may_use_validated_sltp_values_in_a_separate_command_package"
        ),
        BLOCKED_BY_MISSING_REFERENCE_PRICE: (
            "provide_owner_reviewed_non_secret_reference_price"
        ),
        BLOCKED_BY_INVALID_NUMERIC_PRICE: (
            "provide_positive_numeric_reference_stop_loss_and_take_profit"
        ),
        BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE: (
            "move_buy_stop_loss_below_reference_price"
        ),
        BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE: (
            "move_buy_take_profit_above_reference_price"
        ),
        BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE: (
            "move_sell_stop_loss_above_reference_price"
        ),
        BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE: (
            "move_sell_take_profit_below_reference_price"
        ),
        BLOCKED_BY_LIVE_ENDPOINT: "preserve_demo_only_no_broker_call_boundary",
        BLOCKED_BY_SECOND_ORDER_REQUEST: "preserve_no_second_order_boundary",
        BLOCKED_BY_PROFIT_CLAIM: "remove_profit_or_campaign_claim",
    }.get(classification, "stop_and_review_sltp_validation")


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


def _decimal_text(value: Any) -> str:
    return format(value, "f") if isinstance(value, Decimal) else "INVALID"


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _bool(value: Any) -> bool:
    return value is True


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
