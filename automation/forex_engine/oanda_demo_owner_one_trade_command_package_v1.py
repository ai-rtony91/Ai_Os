from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-OWNER-ONE-TRADE-COMMAND-PACKAGE-V1"
PACKAGE_VERSION = "v1"

OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY = (
    "OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY"
)
BLOCKED_BY_MISSING_TRADE_INTENT = "BLOCKED_BY_MISSING_TRADE_INTENT"
BLOCKED_BY_INVALID_INSTRUMENT = "BLOCKED_BY_INVALID_INSTRUMENT"
BLOCKED_BY_INVALID_DIRECTION = "BLOCKED_BY_INVALID_DIRECTION"
BLOCKED_BY_INVALID_UNITS = "BLOCKED_BY_INVALID_UNITS"
BLOCKED_BY_MISSING_STOP_LOSS = "BLOCKED_BY_MISSING_STOP_LOSS"
BLOCKED_BY_MISSING_TAKE_PROFIT = "BLOCKED_BY_MISSING_TAKE_PROFIT"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

APPROVED_INSTRUMENT = "EUR_USD"
ALLOWED_DIRECTIONS = ("BUY", "SELL")
MICRO_UNITS_MIN = 1
MICRO_UNITS_MAX = 1000

TRADE_INTENT_FIELDS = (
    "instrument",
    "direction",
    "units",
    "stop_loss_price",
    "take_profit_price",
)

CONFIRMATION_FIELDS = (
    "demo_only_confirmed",
    "one_order_only_confirmed",
    "owner_manual_runtime_only_confirmed",
    "stop_loss_present_confirmed",
    "take_profit_present_confirmed",
    "no_live_endpoint_confirmed",
    "no_autonomous_order_confirmed",
    "post_trade_evidence_required_confirmed",
    "result_bucket_required_confirmed",
    "no_profit_claim_confirmed",
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


def default_oanda_demo_owner_one_trade_command_package_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "units": 1,
        "stop_loss_price": "EXAMPLE_STOP_LOSS_PRICE",
        "take_profit_price": "EXAMPLE_TAKE_PROFIT_PRICE",
        "demo_only_confirmed": False,
        "one_order_only_confirmed": False,
        "owner_manual_runtime_only_confirmed": False,
        "stop_loss_present_confirmed": False,
        "take_profit_present_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_autonomous_order_confirmed": False,
        "post_trade_evidence_required_confirmed": False,
        "result_bucket_required_confirmed": False,
        "no_profit_claim_confirmed": False,
    }


def build_oanda_demo_owner_one_trade_command_package_v1(
    command_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    normalized = _normalize_context(command_context)
    blockers = _blockers(normalized)
    classification = _classification(normalized)
    package_ready = classification == OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY

    return {
        "packet_id": PACKET_ID,
        "package_version": PACKAGE_VERSION,
        "classification": classification,
        "package_ready": package_ready,
        "blockers": blockers,
        "trade_intent": {
            "instrument": normalized["instrument"],
            "direction": normalized["direction"],
            "units": normalized["units"],
            "micro_units_only": _micro_units_valid(normalized["units"]),
            "stop_loss_present": _present(normalized["stop_loss_price"]),
            "take_profit_present": _present(normalized["take_profit_price"]),
        },
        "owner_manual_command_package": {
            "template_only": True,
            "owner_manual_runtime_only": True,
            "ready": package_ready,
            "one_order_only": True,
            "max_order_attempts": 1,
            "must_replace_example_placeholders_before_owner_runtime": True,
            "owner_manual_command_template": _owner_manual_command_template(normalized)
            if package_ready
            else None,
        },
        "required_next_packet": (
            "AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1"
        ),
        "safety_proof": {
            "broker_call_performed_by_codex": False,
            "order_placement_performed": False,
            "orders_endpoint_called": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "credential_value_printed": False,
            "account_id_value_printed": False,
            "dotenv_read": False,
            "windows_vault_read_performed": False,
            "live_endpoint_used": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
            "profit_claim_made": False,
        },
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(classification),
    }


def _normalize_context(command_context: Mapping[str, Any] | None) -> dict[str, Any]:
    context = command_context if isinstance(command_context, Mapping) else {}
    return {
        "instrument": _text(context.get("instrument")).upper(),
        "direction": _text(context.get("direction")).upper(),
        "units": _integer_or_none(context.get("units")),
        "units_supplied": context.get("units") is not None,
        "stop_loss_price": _text(context.get("stop_loss_price")),
        "take_profit_price": _text(context.get("take_profit_price")),
        "demo_only_confirmed": _bool(context.get("demo_only_confirmed")),
        "one_order_only_confirmed": _bool(context.get("one_order_only_confirmed")),
        "owner_manual_runtime_only_confirmed": _bool(
            context.get("owner_manual_runtime_only_confirmed")
        ),
        "stop_loss_present_confirmed": _bool(
            context.get("stop_loss_present_confirmed")
        ),
        "take_profit_present_confirmed": _bool(
            context.get("take_profit_present_confirmed")
        ),
        "no_live_endpoint_confirmed": _bool(context.get("no_live_endpoint_confirmed")),
        "no_autonomous_order_confirmed": _bool(
            context.get("no_autonomous_order_confirmed")
        ),
        "post_trade_evidence_required_confirmed": _bool(
            context.get("post_trade_evidence_required_confirmed")
        ),
        "result_bucket_required_confirmed": _bool(
            context.get("result_bucket_required_confirmed")
        ),
        "no_profit_claim_confirmed": _bool(context.get("no_profit_claim_confirmed")),
    }


def _blockers(normalized: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not normalized["instrument"]:
        blockers.append("instrument_required")
    elif normalized["instrument"] != APPROVED_INSTRUMENT:
        blockers.append("instrument_must_be_eur_usd")

    if not normalized["direction"]:
        blockers.append("direction_required")
    elif normalized["direction"] not in ALLOWED_DIRECTIONS:
        blockers.append("direction_must_be_buy_or_sell")

    if not normalized["units_supplied"]:
        blockers.append("units_required")
    elif not _micro_units_valid(normalized["units"]):
        blockers.append("units_must_be_integer_micro_size")

    if not _present(normalized["stop_loss_price"]):
        blockers.append("stop_loss_price_required")
    if not _present(normalized["take_profit_price"]):
        blockers.append("take_profit_price_required")

    if not _bool(normalized["demo_only_confirmed"]):
        blockers.append("demo_only_confirmation_required")
    if not _bool(normalized["one_order_only_confirmed"]):
        blockers.append("one_order_only_confirmation_required")
    if not _bool(normalized["owner_manual_runtime_only_confirmed"]):
        blockers.append("owner_manual_runtime_only_confirmation_required")
    if not _bool(normalized["stop_loss_present_confirmed"]):
        blockers.append("stop_loss_present_confirmation_required")
    if not _bool(normalized["take_profit_present_confirmed"]):
        blockers.append("take_profit_present_confirmation_required")
    if not _bool(normalized["no_live_endpoint_confirmed"]):
        blockers.append("no_live_endpoint_confirmation_required")
    if not _bool(normalized["no_autonomous_order_confirmed"]):
        blockers.append("no_autonomous_order_confirmation_required")
    if not _bool(normalized["post_trade_evidence_required_confirmed"]):
        blockers.append("post_trade_evidence_required_confirmation_required")
    if not _bool(normalized["result_bucket_required_confirmed"]):
        blockers.append("result_bucket_required_confirmation_required")
    if not _bool(normalized["no_profit_claim_confirmed"]):
        blockers.append("no_profit_claim_confirmation_required")
    return blockers


def _classification(normalized: Mapping[str, Any]) -> str:
    if (
        not normalized["instrument"]
        or not normalized["direction"]
        or not normalized["units_supplied"]
        or not _bool(normalized["demo_only_confirmed"])
        or not _bool(normalized["one_order_only_confirmed"])
        or not _bool(normalized["post_trade_evidence_required_confirmed"])
        or not _bool(normalized["result_bucket_required_confirmed"])
    ):
        return BLOCKED_BY_MISSING_TRADE_INTENT
    if normalized["instrument"] != APPROVED_INSTRUMENT:
        return BLOCKED_BY_INVALID_INSTRUMENT
    if normalized["direction"] not in ALLOWED_DIRECTIONS:
        return BLOCKED_BY_INVALID_DIRECTION
    if not _micro_units_valid(normalized["units"]):
        return BLOCKED_BY_INVALID_UNITS
    if (
        not _present(normalized["stop_loss_price"])
        or not _bool(normalized["stop_loss_present_confirmed"])
    ):
        return BLOCKED_BY_MISSING_STOP_LOSS
    if (
        not _present(normalized["take_profit_price"])
        or not _bool(normalized["take_profit_present_confirmed"])
    ):
        return BLOCKED_BY_MISSING_TAKE_PROFIT
    if not _bool(normalized["no_live_endpoint_confirmed"]):
        return BLOCKED_BY_LIVE_ENDPOINT
    if (
        not _bool(normalized["owner_manual_runtime_only_confirmed"])
        or not _bool(normalized["no_autonomous_order_confirmed"])
    ):
        return BLOCKED_BY_AUTONOMY_REQUEST
    if not _bool(normalized["no_profit_claim_confirmed"]):
        return BLOCKED_BY_PROFIT_CLAIM
    return OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY


def _owner_manual_command_template(normalized: Mapping[str, Any]) -> str:
    return " ".join(
        [
            "python",
            "scripts/forex_delivery/"
            "run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py",
            "--execute-transport",
            "--instrument",
            normalized["instrument"],
            "--direction",
            normalized["direction"],
            "--units",
            str(normalized["units"]),
            "--stop-loss",
            normalized["stop_loss_price"],
            "--take-profit",
            normalized["take_profit_price"],
            "--risk-amount",
            "EXAMPLE_RISK_AMOUNT",
            "--client-order-id",
            "AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001",
            "--order-type",
            "MARKET",
            "--i-confirm-transport-reviewed",
            "--i-confirm-actual-demo-order-intent",
            "--i-understand-demo-only",
            "--i-understand-one-order-only",
            "--i-understand-loss-possible",
            "--i-understand-no-profit-guarantee",
            "--i-confirm-stop-loss",
            "--i-confirm-take-profit",
            "--i-confirm-no-second-order",
            "--i-confirm-post-trade-evidence",
            "--i-confirm-kill-switch-ready",
            "--i-confirm-runtime-credentials-external",
        ]
    )


def _next_safe_action(classification: str) -> str:
    if classification == OWNER_DEMO_ONE_TRADE_COMMAND_PACKAGE_READY:
        return "owner_review_template_then_manually_run_demo_order_only_if_intended"
    if classification == BLOCKED_BY_MISSING_TRADE_INTENT:
        return "provide_demo_trade_intent_and_required_owner_confirmations"
    if classification == BLOCKED_BY_INVALID_INSTRUMENT:
        return "use_eur_usd_only"
    if classification == BLOCKED_BY_INVALID_DIRECTION:
        return "use_buy_or_sell_only"
    if classification == BLOCKED_BY_INVALID_UNITS:
        return "use_integer_micro_units_only"
    if classification == BLOCKED_BY_MISSING_STOP_LOSS:
        return "provide_stop_loss_placeholder_or_owner_runtime_price"
    if classification == BLOCKED_BY_MISSING_TAKE_PROFIT:
        return "provide_take_profit_placeholder_or_owner_runtime_price"
    if classification == BLOCKED_BY_LIVE_ENDPOINT:
        return "remove_live_endpoint_or_live_trading_request"
    if classification == BLOCKED_BY_AUTONOMY_REQUEST:
        return "remove_autonomous_scheduler_daemon_webhook_or_non_manual_path"
    if classification == BLOCKED_BY_PROFIT_CLAIM:
        return "remove_profit_or_campaign_guarantee_claim"
    return "stop_and_review_owner_command_package_classification"


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _micro_units_valid(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and MICRO_UNITS_MIN <= value <= MICRO_UNITS_MAX
    )


def _integer_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        if stripped and stripped.lstrip("-").isdigit():
            return int(stripped)
    return None


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _present(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else value is not None


def _bool(value: Any) -> bool:
    return value is True
