from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_bid_ask_sltp_validation_v1 import (
    BID_ASK_SLTP_VALIDATION_READY,
    evaluate_oanda_demo_bid_ask_sltp_validation_v1,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-LIVE-QUOTE-DERIVED-SLTP-RUNTIME-V1"
RUNTIME_VERSION = "v1"

LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY = (
    "LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY"
)
LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED = (
    "LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED"
)
BLOCKED_BY_MISSING_VAULT_CREDENTIALS = "BLOCKED_BY_MISSING_VAULT_CREDENTIALS"
BLOCKED_BY_PRICING_FETCH = "BLOCKED_BY_PRICING_FETCH"
BLOCKED_BY_INVALID_PRICING = "BLOCKED_BY_INVALID_PRICING"
BLOCKED_BY_SLTP_VALIDATION = "BLOCKED_BY_SLTP_VALIDATION"
BLOCKED_BY_INVALID_TRADE_INTENT = "BLOCKED_BY_INVALID_TRADE_INTENT"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_ORDER_CAP = "BLOCKED_BY_ORDER_CAP"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

APPROVED_ACCESS_TOKEN_LABEL = "AIOS_OANDA_DEMO_ACCESS_TOKEN"
APPROVED_ACCOUNT_ID_LABEL = "AIOS_OANDA_DEMO_ACCOUNT_ID"
APPROVED_VAULT_LABELS = (
    APPROVED_ACCESS_TOKEN_LABEL,
    APPROVED_ACCOUNT_ID_LABEL,
)
APPROVED_INSTRUMENT = "EUR_USD"
APPROVED_ORDER_TYPE = "MARKET"
ALLOWED_DIRECTIONS = ("BUY", "SELL")
DEMO_API_BASE_URL_PREFIX = "https://api-fxpractice.oanda.com/v3"
DEFAULT_CLIENT_ORDER_ID = "AIOS-DEMO-LIVEQUOTE-DERIVED-OWNER-RUNTIME-001"
REDACTED_TOKEN_REFERENCE = "REDACTED_RUNTIME_ACCESS_TOKEN"
REDACTED_ACCOUNT_ID_REFERENCE = "REDACTED_RUNTIME_ACCOUNT_ID"
REDACTED_RUNTIME_ONLY_REFERENCE = "REDACTED_RUNTIME_ONLY_REFERENCE"

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

SENSITIVE_KEY_EXACT = {
    "access_token",
    "token",
    "authorization",
    "password",
    "secret",
    "api_key",
    "secret_value",
    "credential_value",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
}

SENSITIVE_KEY_TERMS = (
    "access_token",
    "authorization",
    "password",
    "secret",
    "api_key",
    "secret_value",
    "credential_value",
    "runtime_access_token",
    "runtime_account_id",
    "account_id",
    "accountid",
)


def default_live_quote_derived_sltp_runtime_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "units": "1",
        "stop_loss_pips": "",
        "take_profit_pips": "",
        "min_distance_pips": "2",
        "pip_size": "0.0001",
        "risk_amount": "1.00",
        "client_order_id": DEFAULT_CLIENT_ORDER_ID,
        "order_type": APPROVED_ORDER_TYPE,
        "demo_only_confirmed": False,
        "vault_backed_runtime_only_confirmed": False,
        "one_order_only_confirmed": False,
        "owner_manual_runtime_only_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_autonomous_order_confirmed": False,
        "no_second_order_confirmed": False,
        "post_trade_evidence_required_confirmed": False,
        "no_profit_claim_confirmed": False,
        "loss_possible_understood": False,
        "no_profit_guarantee_understood": False,
        "live_endpoint_requested": False,
        "autonomous_order_requested": False,
        "scheduler_requested": False,
        "daemon_requested": False,
        "webhook_requested": False,
        "order_already_attempted": False,
        "profit_claim_made": False,
    }


def build_live_quote_derived_sltp_runtime_v1(
    runtime_context: Mapping[str, Any] | None = None,
    *,
    vault_load_callable: object | None = None,
    http_get_pricing_callable: object | None = None,
    http_post_order_callable: object | None = None,
    execute_order: bool = False,
) -> dict[str, Any]:
    normalized = _normalize_context(runtime_context)
    intent_blockers = _intent_blockers(normalized)
    if intent_blockers:
        return _result(
            classification=_classification(intent_blockers),
            blockers=intent_blockers,
            normalized=normalized,
            vault_records=[],
            runtime_access_token="",
            runtime_account_id="",
            pricing_result=None,
            pricing_snapshot=None,
            derived_sltp=None,
            validation=None,
            order_submission=None,
            execute_order=execute_order,
        )

    if not callable(vault_load_callable):
        return _result(
            classification=BLOCKED_BY_MISSING_VAULT_CREDENTIALS,
            blockers=["approved_windows_vault_loader_required_at_owner_runtime"],
            normalized=normalized,
            vault_records=[],
            runtime_access_token="",
            runtime_account_id="",
            pricing_result=None,
            pricing_snapshot=None,
            derived_sltp=None,
            validation=None,
            order_submission=None,
            execute_order=execute_order,
        )

    vault_records = _load_approved_vault_records(vault_load_callable)
    runtime_access_token = _extract_loaded_secret(vault_records[0])
    runtime_account_id = _extract_loaded_secret(vault_records[1])
    if not runtime_access_token or not runtime_account_id:
        return _result(
            classification=BLOCKED_BY_MISSING_VAULT_CREDENTIALS,
            blockers=["approved_demo_access_token_or_account_id_missing_from_vault"],
            normalized=normalized,
            vault_records=vault_records,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            pricing_result=None,
            pricing_snapshot=None,
            derived_sltp=None,
            validation=None,
            order_submission=None,
            execute_order=execute_order,
        )

    if not callable(http_get_pricing_callable):
        return _result(
            classification=BLOCKED_BY_PRICING_FETCH,
            blockers=["read_only_pricing_get_callable_required"],
            normalized=normalized,
            vault_records=vault_records,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            pricing_result=None,
            pricing_snapshot=None,
            derived_sltp=None,
            validation=None,
            order_submission=None,
            execute_order=execute_order,
        )

    pricing_result = _call_pricing_get(
        http_get_pricing_callable,
        normalized=normalized,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )
    pricing_snapshot = _pricing_snapshot(pricing_result)
    if not _pricing_snapshot_valid(pricing_snapshot, normalized):
        return _result(
            classification=BLOCKED_BY_INVALID_PRICING,
            blockers=["valid_current_bid_ask_pricing_required"],
            normalized=normalized,
            vault_records=vault_records,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            pricing_result=pricing_result,
            pricing_snapshot=pricing_snapshot,
            derived_sltp=None,
            validation=None,
            order_submission=None,
            execute_order=execute_order,
        )

    derived_sltp = _derive_sltp(normalized, pricing_snapshot)
    validation = _validate_derived_sltp(normalized, pricing_snapshot, derived_sltp)
    if validation.get("classification") != BID_ASK_SLTP_VALIDATION_READY:
        return _result(
            classification=BLOCKED_BY_SLTP_VALIDATION,
            blockers=["computed_sltp_failed_bid_ask_validation"],
            normalized=normalized,
            vault_records=vault_records,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            pricing_result=pricing_result,
            pricing_snapshot=pricing_snapshot,
            derived_sltp=derived_sltp,
            validation=validation,
            order_submission=None,
            execute_order=execute_order,
        )

    if not execute_order:
        return _result(
            classification=LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY,
            blockers=[],
            normalized=normalized,
            vault_records=vault_records,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            pricing_result=pricing_result,
            pricing_snapshot=pricing_snapshot,
            derived_sltp=derived_sltp,
            validation=validation,
            order_submission=None,
            execute_order=execute_order,
        )

    if not callable(http_post_order_callable):
        return _result(
            classification=BLOCKED_BY_INVALID_TRADE_INTENT,
            blockers=["order_post_callable_required_for_owner_execute_mode"],
            normalized=normalized,
            vault_records=vault_records,
            runtime_access_token=runtime_access_token,
            runtime_account_id=runtime_account_id,
            pricing_result=pricing_result,
            pricing_snapshot=pricing_snapshot,
            derived_sltp=derived_sltp,
            validation=validation,
            order_submission=None,
            execute_order=execute_order,
        )

    order_submission = _call_order_post(
        http_post_order_callable,
        normalized=normalized,
        derived_sltp=derived_sltp,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )
    return _result(
        classification=LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED,
        blockers=[],
        normalized=normalized,
        vault_records=vault_records,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
        pricing_result=pricing_result,
        pricing_snapshot=pricing_snapshot,
        derived_sltp=derived_sltp,
        validation=validation,
        order_submission=order_submission,
        execute_order=execute_order,
    )


def _normalize_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    defaults = default_live_quote_derived_sltp_runtime_context_v1()
    supplied = context if isinstance(context, Mapping) else {}
    merged = {**defaults, **dict(supplied)}
    return {
        "instrument": _text(merged.get("instrument")).upper(),
        "direction": _text(merged.get("direction")).upper(),
        "units": _decimal_or_none(merged.get("units")),
        "stop_loss_pips": _decimal_or_none(merged.get("stop_loss_pips")),
        "take_profit_pips": _decimal_or_none(merged.get("take_profit_pips")),
        "min_distance_pips": _decimal_or_none(merged.get("min_distance_pips")),
        "pip_size": _decimal_or_none(merged.get("pip_size")),
        "risk_amount": _decimal_or_none(merged.get("risk_amount")),
        "client_order_id": _text(merged.get("client_order_id")),
        "order_type": _text(merged.get("order_type")).upper(),
        "demo_only_confirmed": _bool(merged.get("demo_only_confirmed")),
        "vault_backed_runtime_only_confirmed": _bool(
            merged.get("vault_backed_runtime_only_confirmed")
        ),
        "one_order_only_confirmed": _bool(merged.get("one_order_only_confirmed")),
        "owner_manual_runtime_only_confirmed": _bool(
            merged.get("owner_manual_runtime_only_confirmed")
        ),
        "no_live_endpoint_confirmed": _bool(
            merged.get("no_live_endpoint_confirmed")
        ),
        "no_autonomous_order_confirmed": _bool(
            merged.get("no_autonomous_order_confirmed")
        ),
        "no_second_order_confirmed": _bool(
            merged.get("no_second_order_confirmed")
        ),
        "post_trade_evidence_required_confirmed": _bool(
            merged.get("post_trade_evidence_required_confirmed")
        ),
        "no_profit_claim_confirmed": _bool(merged.get("no_profit_claim_confirmed")),
        "loss_possible_understood": _bool(merged.get("loss_possible_understood")),
        "no_profit_guarantee_understood": _bool(
            merged.get("no_profit_guarantee_understood")
        ),
        "live_endpoint_requested": _bool(merged.get("live_endpoint_requested")),
        "autonomous_order_requested": _bool(merged.get("autonomous_order_requested")),
        "scheduler_requested": _bool(merged.get("scheduler_requested")),
        "daemon_requested": _bool(merged.get("daemon_requested")),
        "webhook_requested": _bool(merged.get("webhook_requested")),
        "order_already_attempted": _bool(merged.get("order_already_attempted")),
        "profit_claim_made": _bool(merged.get("profit_claim_made")),
    }


def _intent_blockers(normalized: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []

    def add(classification: str, message: str) -> None:
        blockers.append(f"{classification}:{message}")

    if normalized["live_endpoint_requested"] or not normalized["no_live_endpoint_confirmed"]:
        add(BLOCKED_BY_LIVE_ENDPOINT, "practice_demo_endpoint_only_required")

    if (
        normalized["autonomous_order_requested"]
        or normalized["scheduler_requested"]
        or normalized["daemon_requested"]
        or normalized["webhook_requested"]
        or not normalized["owner_manual_runtime_only_confirmed"]
        or not normalized["no_autonomous_order_confirmed"]
    ):
        add(BLOCKED_BY_AUTONOMY_REQUEST, "owner_manual_runtime_only_required")

    if (
        normalized["order_already_attempted"]
        or not normalized["one_order_only_confirmed"]
        or not normalized["no_second_order_confirmed"]
    ):
        add(BLOCKED_BY_ORDER_CAP, "one_order_only_and_no_second_order_required")

    if normalized["profit_claim_made"] or not normalized["no_profit_claim_confirmed"]:
        add(BLOCKED_BY_PROFIT_CLAIM, "no_profit_claim_required")
    if not normalized["no_profit_guarantee_understood"]:
        add(BLOCKED_BY_PROFIT_CLAIM, "no_profit_guarantee_required")

    for field in (
        "units",
        "stop_loss_pips",
        "take_profit_pips",
        "min_distance_pips",
        "pip_size",
        "risk_amount",
    ):
        if not _positive_decimal(normalized[field]):
            add(BLOCKED_BY_INVALID_TRADE_INTENT, f"{field}_must_be_positive_numeric")

    if normalized["instrument"] != APPROVED_INSTRUMENT:
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "instrument_must_be_eur_usd")
    if normalized["direction"] not in ALLOWED_DIRECTIONS:
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "direction_must_be_buy_or_sell")
    if normalized["units"] != Decimal("1"):
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "units_must_be_one")
    if normalized["order_type"] != APPROVED_ORDER_TYPE:
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "order_type_must_be_market")
    if not _sanitized_client_order_id(normalized["client_order_id"]):
        add(BLOCKED_BY_INVALID_TRADE_INTENT, "client_order_id_required_and_sanitized")
    if normalized["stop_loss_pips"] and normalized["min_distance_pips"]:
        if normalized["stop_loss_pips"] < normalized["min_distance_pips"]:
            add(BLOCKED_BY_INVALID_TRADE_INTENT, "stop_loss_pips_below_min_distance")
    if normalized["take_profit_pips"] and normalized["min_distance_pips"]:
        if normalized["take_profit_pips"] < normalized["min_distance_pips"]:
            add(BLOCKED_BY_INVALID_TRADE_INTENT, "take_profit_pips_below_min_distance")

    for field in (
        "demo_only_confirmed",
        "vault_backed_runtime_only_confirmed",
        "post_trade_evidence_required_confirmed",
        "loss_possible_understood",
    ):
        if not normalized[field]:
            add(BLOCKED_BY_INVALID_TRADE_INTENT, f"{field}_required")
    return _unique(blockers)


def _classification(blockers: list[str]) -> str:
    for classification in (
        BLOCKED_BY_LIVE_ENDPOINT,
        BLOCKED_BY_AUTONOMY_REQUEST,
        BLOCKED_BY_ORDER_CAP,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_INVALID_TRADE_INTENT,
    ):
        if any(blocker.startswith(f"{classification}:") for blocker in blockers):
            return classification
    return BLOCKED_BY_INVALID_TRADE_INTENT


def _load_approved_vault_records(vault_load_callable: object) -> list[dict[str, Any]]:
    return [
        _load_vault_record(vault_load_callable, APPROVED_ACCESS_TOKEN_LABEL),
        _load_vault_record(vault_load_callable, APPROVED_ACCOUNT_ID_LABEL),
    ]


def _load_vault_record(vault_load_callable: object, credential_name: str) -> dict[str, Any]:
    try:
        result = vault_load_callable({"credential_name": credential_name})  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive adapter boundary
        result = {
            "credential_name": credential_name,
            "load_status": "vault_adapter_exception",
            "error_type": type(exc).__name__,
            "secret_value": "",
        }
    return {
        "operation": "load",
        "credential_name": credential_name,
        "result": result,
    }


def _extract_loaded_secret(vault_record: Mapping[str, Any]) -> str:
    result = vault_record.get("result")
    if isinstance(result, str):
        return result
    if isinstance(result, Mapping):
        for key in ("secret_value", "value", "secret", "credential_value", "password"):
            value = result.get(key)
            if isinstance(value, str):
                return value
    return ""


def _call_pricing_get(
    http_get_pricing_callable: object,
    *,
    normalized: Mapping[str, Any],
    runtime_access_token: str,
    runtime_account_id: str,
) -> Mapping[str, Any]:
    payload = {
        "method": "GET",
        "endpoint_type": "OANDA practice/demo pricing endpoint only",
        "demo_api_base_url": DEMO_API_BASE_URL_PREFIX,
        "instrument": normalized["instrument"],
        "runtime_access_token": runtime_access_token,
        "runtime_account_id": runtime_account_id,
    }
    try:
        result = http_get_pricing_callable(payload)  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive adapter boundary
        return {
            "network_call_performed": False,
            "status_code": None,
            "error_type": type(exc).__name__,
            "response_json": None,
        }
    return result if isinstance(result, Mapping) else {"response_json": result}


def _pricing_snapshot(pricing_result: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(pricing_result, Mapping):
        return None
    response_json = pricing_result.get("response_json", pricing_result)
    if not isinstance(response_json, Mapping):
        return None
    prices = response_json.get("prices")
    if not isinstance(prices, list) or not prices:
        return None
    price = prices[0]
    if not isinstance(price, Mapping):
        return None
    bid = _first_price(price.get("bids"))
    ask = _first_price(price.get("asks"))
    return {
        "instrument": _text(price.get("instrument")).upper(),
        "time": _text(price.get("time")),
        "bid": bid,
        "ask": ask,
        "source": "owner_runtime_oanda_practice_pricing_get",
    }


def _first_price(values: Any) -> Decimal | None:
    if not isinstance(values, list) or not values:
        return None
    first = values[0]
    if not isinstance(first, Mapping):
        return None
    return _decimal_or_none(first.get("price"))


def _pricing_snapshot_valid(
    pricing_snapshot: Mapping[str, Any] | None,
    normalized: Mapping[str, Any],
) -> bool:
    if not isinstance(pricing_snapshot, Mapping):
        return False
    bid = pricing_snapshot.get("bid")
    ask = pricing_snapshot.get("ask")
    return (
        pricing_snapshot.get("instrument") == normalized["instrument"]
        and isinstance(bid, Decimal)
        and isinstance(ask, Decimal)
        and bid > 0
        and ask > bid
    )


def _derive_sltp(
    normalized: Mapping[str, Any],
    pricing_snapshot: Mapping[str, Any],
) -> dict[str, Decimal]:
    bid = pricing_snapshot["bid"]
    ask = pricing_snapshot["ask"]
    pip_size = normalized["pip_size"]
    stop_distance = normalized["stop_loss_pips"] * pip_size
    take_distance = normalized["take_profit_pips"] * pip_size
    if normalized["direction"] == "BUY":
        stop_loss = bid - stop_distance
        take_profit = ask + take_distance
    else:
        stop_loss = ask + stop_distance
        take_profit = bid - take_distance
    return {
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "stop_loss_distance": stop_distance,
        "take_profit_distance": take_distance,
    }


def _validate_derived_sltp(
    normalized: Mapping[str, Any],
    pricing_snapshot: Mapping[str, Any],
    derived_sltp: Mapping[str, Decimal],
) -> Mapping[str, Any]:
    return evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        {
            "instrument": normalized["instrument"],
            "direction": normalized["direction"],
            "bid": _decimal_text(pricing_snapshot["bid"]),
            "ask": _decimal_text(pricing_snapshot["ask"]),
            "stop_loss": _decimal_text(derived_sltp["stop_loss"]),
            "take_profit": _decimal_text(derived_sltp["take_profit"]),
            "min_distance_pips": _decimal_text(normalized["min_distance_pips"]),
            "pip_size": _decimal_text(normalized["pip_size"]),
            "demo_only_confirmed": True,
            "no_broker_call_confirmed": True,
            "no_order_confirmed": True,
            "no_live_endpoint_confirmed": normalized["no_live_endpoint_confirmed"],
            "no_profit_claim_confirmed": normalized["no_profit_claim_confirmed"],
        }
    )


def _call_order_post(
    http_post_order_callable: object,
    *,
    normalized: Mapping[str, Any],
    derived_sltp: Mapping[str, Decimal],
    runtime_access_token: str,
    runtime_account_id: str,
) -> Mapping[str, Any]:
    payload = {
        "method": "POST",
        "endpoint_type": "OANDA practice/demo orders endpoint only",
        "demo_api_base_url": DEMO_API_BASE_URL_PREFIX,
        "runtime_access_token": runtime_access_token,
        "runtime_account_id": runtime_account_id,
        "order_payload": _oanda_order_payload(normalized, derived_sltp),
        "one_order_only": True,
        "max_order_attempts": 1,
    }
    try:
        result = http_post_order_callable(payload)  # type: ignore[misc]
    except Exception as exc:  # pragma: no cover - defensive adapter boundary
        return {
            "network_call_performed": False,
            "order_placement_performed": False,
            "order_attempt_count": 0,
            "error_type": type(exc).__name__,
            "response_json": None,
        }
    return result if isinstance(result, Mapping) else {"response_json": result}


def _oanda_order_payload(
    normalized: Mapping[str, Any],
    derived_sltp: Mapping[str, Decimal],
) -> dict[str, Any]:
    units = "1" if normalized["direction"] == "BUY" else "-1"
    return {
        "order": {
            "type": "MARKET",
            "instrument": normalized["instrument"],
            "units": units,
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "clientExtensions": {"id": normalized["client_order_id"]},
            "stopLossOnFill": {"price": _decimal_text(derived_sltp["stop_loss"])},
            "takeProfitOnFill": {"price": _decimal_text(derived_sltp["take_profit"])},
        }
    }


def _result(
    *,
    classification: str,
    blockers: list[str],
    normalized: Mapping[str, Any],
    vault_records: list[dict[str, Any]],
    runtime_access_token: str,
    runtime_account_id: str,
    pricing_result: Mapping[str, Any] | None,
    pricing_snapshot: Mapping[str, Any] | None,
    derived_sltp: Mapping[str, Decimal] | None,
    validation: Mapping[str, Any] | None,
    order_submission: Mapping[str, Any] | None,
    execute_order: bool,
) -> dict[str, Any]:
    order_summary = _order_submission_summary(order_submission)
    pricing_status_code = pricing_result.get("status_code") if pricing_result else None
    result = {
        "packet_id": PACKET_ID,
        "runtime_version": RUNTIME_VERSION,
        "script_status": classification,
        "classification": classification,
        "runtime_ready": classification
        in (
            LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY,
            LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED,
        ),
        "owner_execute_requested": execute_order,
        "blockers": blockers,
        "approved_vault_labels": list(APPROVED_VAULT_LABELS),
        "vault_load_boundary": {
            "vault_load_attempted": bool(vault_records),
            "approved_vault_labels_only": True,
            "credential_values_runtime_only": True,
            "credential_values_printed": False,
            "credential_values_persisted_to_repo": False,
            "command_line_token_argument_supported": False,
            "command_line_account_id_argument_supported": False,
        },
        "sanitized_vault_load_result": vault_records if vault_records else None,
        "pricing_fetch": {
            "performed": bool(pricing_result),
            "endpoint_type": "OANDA practice/demo pricing endpoint only",
            "method": "GET",
            "status_code": pricing_status_code,
            "live_endpoint_used": False,
        },
        "pricing_snapshot": _sanitized_pricing_snapshot(pricing_snapshot),
        "derived_order": _derived_order_summary(normalized, derived_sltp),
        "bid_ask_validation": {
            "classification": validation.get("classification") if validation else None,
            "validation_ready": validation.get("validation_ready") if validation else False,
        },
        "order_submission": order_summary,
        "safety_boundaries": {
            "pricing_network_call_performed": bool(pricing_result),
            "broker_network_call_performed": bool(order_submission),
            "order_placement_performed": bool(order_submission),
            "order_attempt_count": 1 if order_submission else 0,
            "credential_read_performed": bool(vault_records),
            "account_id_read_performed": bool(vault_records),
            "credential_value_printed": False,
            "account_id_value_printed": False,
            "dotenv_read": False,
            "environment_variable_read_performed": False,
            "live_endpoint_used": False,
            "second_order_allowed": False,
            "retry_allowed": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
            "profit_claimed": False,
            "fill_claimed": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(classification),
    }
    return _sanitize_value(
        result,
        runtime_access_token=runtime_access_token,
        runtime_account_id=runtime_account_id,
    )


def _sanitized_pricing_snapshot(
    pricing_snapshot: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(pricing_snapshot, Mapping):
        return None
    return {
        "instrument": pricing_snapshot.get("instrument"),
        "time": pricing_snapshot.get("time") or "UNKNOWN",
        "bid": _decimal_text(pricing_snapshot.get("bid")),
        "ask": _decimal_text(pricing_snapshot.get("ask")),
        "source": pricing_snapshot.get("source"),
    }


def _derived_order_summary(
    normalized: Mapping[str, Any],
    derived_sltp: Mapping[str, Decimal] | None,
) -> dict[str, Any] | None:
    if not isinstance(derived_sltp, Mapping):
        return None
    return {
        "instrument": normalized["instrument"],
        "direction": normalized["direction"],
        "units": _decimal_text(normalized["units"]),
        "order_type": normalized["order_type"],
        "stop_loss": _decimal_text(derived_sltp.get("stop_loss")),
        "take_profit": _decimal_text(derived_sltp.get("take_profit")),
        "stop_loss_distance": _decimal_text(derived_sltp.get("stop_loss_distance")),
        "take_profit_distance": _decimal_text(
            derived_sltp.get("take_profit_distance")
        ),
        "client_order_id": normalized["client_order_id"],
    }


def _order_submission_summary(order_submission: Mapping[str, Any] | None) -> Any:
    if not isinstance(order_submission, Mapping):
        return None
    response_json = order_submission.get("response_json", order_submission)
    response_json = response_json if isinstance(response_json, Mapping) else {}
    create = _mapping(response_json.get("orderCreateTransaction"))
    fill = _mapping(response_json.get("orderFillTransaction"))
    cancel = _mapping(response_json.get("orderCancelTransaction"))
    return {
        "endpoint_type": "OANDA practice/demo orders endpoint only",
        "method": "POST",
        "status_code": order_submission.get("status_code"),
        "network_call_performed": bool(order_submission),
        "order_placement_performed": bool(order_submission),
        "order_attempt_count": 1,
        "order_create_transaction_id": create.get("id"),
        "order_fill_transaction_id": fill.get("id"),
        "order_cancel_transaction_id": cancel.get("id"),
        "cancel_reason": cancel.get("reason"),
        "related_transaction_ids": response_json.get("relatedTransactionIDs"),
    }


def _next_safe_action(classification: str) -> str:
    return {
        LIVE_QUOTE_DERIVED_RUNTIME_PACKET_READY: (
            "owner_may_review_quote_derived_values_or_execute_one_demo_order_if_intended"
        ),
        LIVE_QUOTE_DERIVED_DEMO_ORDER_ATTEMPTED: (
            "capture_sanitized_post_trade_evidence_and_do_not_rerun"
        ),
        BLOCKED_BY_MISSING_VAULT_CREDENTIALS: (
            "owner_confirm_approved_windows_vault_labels_exist"
        ),
        BLOCKED_BY_PRICING_FETCH: "repair_owner_runtime_pricing_get_path",
        BLOCKED_BY_INVALID_PRICING: "retry_only_with_fresh_valid_practice_pricing",
        BLOCKED_BY_SLTP_VALIDATION: "repair_live_quote_derived_sltp_computation",
        BLOCKED_BY_INVALID_TRADE_INTENT: "repair_trade_intent_and_confirmations",
        BLOCKED_BY_LIVE_ENDPOINT: "remove_live_endpoint_request",
        BLOCKED_BY_AUTONOMY_REQUEST: "preserve_owner_manual_runtime_only_boundary",
        BLOCKED_BY_ORDER_CAP: "preserve_one_order_only_boundary",
        BLOCKED_BY_PROFIT_CLAIM: "remove_profit_or_campaign_claim",
    }.get(classification, "stop_and_review_live_quote_derived_runtime_status")


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
    return format(value, "f") if isinstance(value, Decimal) else "INVALID"


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _bool(value: Any) -> bool:
    return value is True


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sanitized_client_order_id(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    client_order_id = value.strip()
    if not client_order_id or client_order_id != value:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.:")
    return all(character in allowed for character in client_order_id)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in {"credential_name", "approved_vault_labels"}:
        return False
    return key_text in SENSITIVE_KEY_EXACT or any(
        term in key_text for term in SENSITIVE_KEY_TERMS
    )


def _sanitize_value(
    value: Any,
    *,
    runtime_access_token: str,
    runtime_account_id: str,
) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text in {"credential_name", "approved_vault_labels"}:
                sanitized[key_text] = child
            elif _sensitive_key(key_text) and isinstance(child, str):
                sanitized[key_text] = REDACTED_RUNTIME_ONLY_REFERENCE
            else:
                sanitized[key_text] = _sanitize_value(
                    child,
                    runtime_access_token=runtime_access_token,
                    runtime_account_id=runtime_account_id,
                )
        return sanitized
    if isinstance(value, list):
        return [
            _sanitize_value(
                child,
                runtime_access_token=runtime_access_token,
                runtime_account_id=runtime_account_id,
            )
            for child in value
        ]
    if isinstance(value, str):
        redacted = value
        if runtime_access_token:
            redacted = redacted.replace(runtime_access_token, REDACTED_TOKEN_REFERENCE)
        if runtime_account_id:
            redacted = redacted.replace(runtime_account_id, REDACTED_ACCOUNT_ID_REFERENCE)
        return redacted
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return repr(value)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
