from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-BID-ASK-SLTP-VALIDATION-V1"
VALIDATION_VERSION = "v1"

BID_ASK_SLTP_VALIDATION_READY = "BID_ASK_SLTP_VALIDATION_READY"
BLOCKED_BY_MISSING_BID_ASK = "BLOCKED_BY_MISSING_BID_ASK"
BLOCKED_BY_INVALID_NUMERIC_INPUT = "BLOCKED_BY_INVALID_NUMERIC_INPUT"
BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_BID = (
    "BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_BID"
)
BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK = (
    "BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK"
)
BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_ASK = (
    "BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_ASK"
)
BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID = (
    "BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID"
)
BLOCKED_BY_MIN_DISTANCE = "BLOCKED_BY_MIN_DISTANCE"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
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


def default_oanda_demo_bid_ask_sltp_validation_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "bid": "",
        "ask": "",
        "stop_loss": "",
        "take_profit": "",
        "min_distance_pips": "2",
        "pip_size": "0.0001",
        "demo_only_confirmed": False,
        "no_broker_call_confirmed": False,
        "no_order_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_profit_claim_confirmed": False,
        "live_endpoint_requested": False,
        "profit_claim_made": False,
    }


def evaluate_oanda_demo_bid_ask_sltp_validation_v1(
    validation_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = _normalize_context(validation_context)
    blockers = _blockers(normalized)
    classification = _classification(blockers)
    return {
        "packet_id": PACKET_ID,
        "validation_version": VALIDATION_VERSION,
        "classification": classification,
        "validation_ready": classification == BID_ASK_SLTP_VALIDATION_READY,
        "blockers": blockers,
        "quote_relationship": _quote_relationship(normalized),
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
            "broker_quote_lookup_performed": False,
            "live_market_data_read": False,
            "profit_claim_made": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(classification),
    }


def _normalize_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    defaults = default_oanda_demo_bid_ask_sltp_validation_context_v1()
    supplied = context if isinstance(context, Mapping) else {}
    merged = {**defaults, **dict(supplied)}
    return {
        "instrument": _text(merged.get("instrument")).upper(),
        "direction": _text(merged.get("direction")).upper(),
        "bid_text": _text(merged.get("bid")),
        "ask_text": _text(merged.get("ask")),
        "stop_loss_text": _text(merged.get("stop_loss")),
        "take_profit_text": _text(merged.get("take_profit")),
        "min_distance_pips_text": _text(merged.get("min_distance_pips")),
        "pip_size_text": _text(merged.get("pip_size")),
        "bid": _decimal_or_none(merged.get("bid")),
        "ask": _decimal_or_none(merged.get("ask")),
        "stop_loss": _decimal_or_none(merged.get("stop_loss")),
        "take_profit": _decimal_or_none(merged.get("take_profit")),
        "min_distance_pips": _decimal_or_none(merged.get("min_distance_pips")),
        "pip_size": _decimal_or_none(merged.get("pip_size")),
        "demo_only_confirmed": _bool(merged.get("demo_only_confirmed")),
        "no_broker_call_confirmed": _bool(merged.get("no_broker_call_confirmed")),
        "no_order_confirmed": _bool(merged.get("no_order_confirmed")),
        "no_live_endpoint_confirmed": _bool(
            merged.get("no_live_endpoint_confirmed")
        ),
        "no_profit_claim_confirmed": _bool(merged.get("no_profit_claim_confirmed")),
        "live_endpoint_requested": _bool(merged.get("live_endpoint_requested")),
        "profit_claim_made": _bool(merged.get("profit_claim_made")),
    }


def _blockers(normalized: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    def add(classification: str, message: str) -> None:
        blockers.append(f"{classification}:{message}")

    if (
        not normalized["demo_only_confirmed"]
        or not normalized["no_broker_call_confirmed"]
        or not normalized["no_order_confirmed"]
        or not normalized["no_live_endpoint_confirmed"]
        or normalized["live_endpoint_requested"]
    ):
        add(BLOCKED_BY_LIVE_ENDPOINT, "demo_only_no_broker_no_order_no_live_required")

    if not normalized["no_profit_claim_confirmed"] or normalized["profit_claim_made"]:
        add(BLOCKED_BY_PROFIT_CLAIM, "no_profit_claim_required")

    if not normalized["bid_text"] or not normalized["ask_text"]:
        add(BLOCKED_BY_MISSING_BID_ASK, "current_bid_and_ask_required")

    if normalized["instrument"] != APPROVED_INSTRUMENT:
        add(BLOCKED_BY_INVALID_NUMERIC_INPUT, "instrument_must_be_eur_usd")
    if normalized["direction"] not in ALLOWED_DIRECTIONS:
        add(BLOCKED_BY_INVALID_NUMERIC_INPUT, "direction_must_be_buy_or_sell")

    for field in (
        "bid",
        "ask",
        "stop_loss",
        "take_profit",
        "min_distance_pips",
        "pip_size",
    ):
        if normalized[field] is None:
            add(BLOCKED_BY_INVALID_NUMERIC_INPUT, f"{field}_must_be_numeric")
        elif normalized[field] <= Decimal("0"):
            add(BLOCKED_BY_INVALID_NUMERIC_INPUT, f"{field}_must_be_positive")

    bid = normalized["bid"]
    ask = normalized["ask"]
    stop_loss = normalized["stop_loss"]
    take_profit = normalized["take_profit"]
    min_distance = _minimum_distance(normalized)
    direction = normalized["direction"]
    if not all(
        isinstance(value, Decimal)
        for value in (bid, ask, stop_loss, take_profit, min_distance)
    ):
        return _unique(blockers)

    if ask <= bid:
        add(BLOCKED_BY_INVALID_NUMERIC_INPUT, "ask_must_be_above_bid")
        return _unique(blockers)

    if direction == "BUY":
        if stop_loss >= bid:
            add(
                BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_BID,
                "buy_stop_loss_must_be_below_current_bid",
            )
        elif bid - stop_loss < min_distance:
            add(
                BLOCKED_BY_MIN_DISTANCE,
                "buy_stop_loss_must_be_at_least_min_distance_below_bid",
            )

        if take_profit <= ask:
            add(
                BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK,
                "buy_take_profit_must_be_above_current_ask",
            )
        elif take_profit - ask < min_distance:
            add(
                BLOCKED_BY_MIN_DISTANCE,
                "buy_take_profit_must_be_at_least_min_distance_above_ask",
            )
    elif direction == "SELL":
        if stop_loss <= ask:
            add(
                BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_ASK,
                "sell_stop_loss_must_be_above_current_ask",
            )
        elif stop_loss - ask < min_distance:
            add(
                BLOCKED_BY_MIN_DISTANCE,
                "sell_stop_loss_must_be_at_least_min_distance_above_ask",
            )

        if take_profit >= bid:
            add(
                BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID,
                "sell_take_profit_must_be_below_current_bid",
            )
        elif bid - take_profit < min_distance:
            add(
                BLOCKED_BY_MIN_DISTANCE,
                "sell_take_profit_must_be_at_least_min_distance_below_bid",
            )

    return _unique(blockers)


def _classification(blockers: list[str]) -> str:
    for classification in (
        BLOCKED_BY_LIVE_ENDPOINT,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_MISSING_BID_ASK,
        BLOCKED_BY_INVALID_NUMERIC_INPUT,
        BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_BID,
        BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK,
        BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_ASK,
        BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID,
        BLOCKED_BY_MIN_DISTANCE,
    ):
        if any(blocker.startswith(f"{classification}:") for blocker in blockers):
            return classification
    return BID_ASK_SLTP_VALIDATION_READY


def _quote_relationship(normalized: Mapping[str, Any]) -> dict[str, Any]:
    bid = normalized["bid"]
    ask = normalized["ask"]
    stop_loss = normalized["stop_loss"]
    take_profit = normalized["take_profit"]
    min_distance = _minimum_distance(normalized)
    return {
        "instrument": normalized["instrument"],
        "direction": normalized["direction"],
        "bid": _decimal_text(bid),
        "ask": _decimal_text(ask),
        "stop_loss": _decimal_text(stop_loss),
        "take_profit": _decimal_text(take_profit),
        "min_distance": _decimal_text(min_distance),
        "buy_executable_entry_side": "ask",
        "sell_executable_entry_side": "bid",
        "buy_stop_loss_below_bid": _compare(stop_loss, bid, "<"),
        "buy_take_profit_above_ask": _compare(take_profit, ask, ">"),
        "sell_stop_loss_above_ask": _compare(stop_loss, ask, ">"),
        "sell_take_profit_below_bid": _compare(take_profit, bid, "<"),
        "bid_ask_owner_or_upstream_supplied": bool(
            normalized["bid_text"] and normalized["ask_text"]
        ),
        "broker_quote_lookup_performed": False,
        "live_market_data_read": False,
    }


def _minimum_distance(normalized: Mapping[str, Any]) -> Decimal | None:
    min_distance_pips = normalized["min_distance_pips"]
    pip_size = normalized["pip_size"]
    if not isinstance(min_distance_pips, Decimal):
        return None
    if not isinstance(pip_size, Decimal):
        return None
    return min_distance_pips * pip_size


def _next_safe_action(classification: str) -> str:
    return {
        BID_ASK_SLTP_VALIDATION_READY: (
            "owner_may_use_bid_ask_validated_sltp_values_in_a_separate_runtime_packet"
        ),
        BLOCKED_BY_MISSING_BID_ASK: "provide_current_non_secret_bid_and_ask",
        BLOCKED_BY_INVALID_NUMERIC_INPUT: "provide_positive_numeric_bid_ask_sltp_inputs",
        BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_BID: "move_buy_stop_loss_below_current_bid",
        BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK: (
            "move_buy_take_profit_above_current_ask"
        ),
        BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_ASK: (
            "move_sell_stop_loss_above_current_ask"
        ),
        BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID: (
            "move_sell_take_profit_below_current_bid"
        ),
        BLOCKED_BY_MIN_DISTANCE: "increase_sltp_distance_from_executable_side",
        BLOCKED_BY_LIVE_ENDPOINT: "preserve_demo_only_no_broker_no_order_boundary",
        BLOCKED_BY_PROFIT_CLAIM: "remove_profit_or_campaign_claim",
    }.get(classification, "stop_and_review_bid_ask_sltp_validation")


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


def _compare(left: Any, right: Any, operator: str) -> bool:
    if not isinstance(left, Decimal) or not isinstance(right, Decimal):
        return False
    if operator == "<":
        return left < right
    if operator == ">":
        return left > right
    return False


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
