"""Corrected OANDA demo command package builder.

This module builds a sanitized owner command template only. It performs no
broker calls, reads no credentials, and does not authorize a future order.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_sltp_validation_correction_v1 import (
    BLOCKED_BY_INVALID_NUMERIC_PRICE,
    BLOCKED_BY_MISSING_REFERENCE_PRICE,
    SLTP_VALIDATION_READY,
    evaluate_oanda_demo_sltp_validation_correction_v1,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-CORRECTED-ORDER-COMMAND-PACKAGE-V1"
NEXT_SAFE_PACKET = "AIOS-FOREX-OANDA-DEMO-FUTURE-ORDER-APPROVAL-GATE-V1"

CORRECTED_ORDER_COMMAND_PACKAGE_READY = "CORRECTED_ORDER_COMMAND_PACKAGE_READY"
BLOCKED_BY_SLTP_VALIDATION = "BLOCKED_BY_SLTP_VALIDATION"
BLOCKED_BY_PRIOR_ORDER_CAP = "BLOCKED_BY_PRIOR_ORDER_CAP"
BLOCKED_BY_MISSING_REFERENCE_PRICE = "BLOCKED_BY_MISSING_REFERENCE_PRICE"
BLOCKED_BY_INVALID_TRADE_INTENT = "BLOCKED_BY_INVALID_TRADE_INTENT"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

APPROVED_INSTRUMENT = "EUR_USD"
APPROVED_ORDER_TYPE = "MARKET"
APPROVED_DIRECTIONS = {"BUY", "SELL"}
CORRECTED_CLIENT_ORDER_ID = "AIOS-DEMO-CORRECTED-ONE-ORDER-OWNER-RUNTIME-001"


@dataclass(frozen=True)
class CorrectedCommandPackageInput:
    instrument: str = APPROVED_INSTRUMENT
    direction: str = "BUY"
    units: Any = 1
    reference_price: Any = None
    stop_loss: Any = None
    take_profit: Any = None
    risk_amount: Any = "1.00"
    client_order_id: str = CORRECTED_CLIENT_ORDER_ID
    order_type: str = APPROVED_ORDER_TYPE
    demo_only_confirmed: bool = False
    sltp_validation_passed_confirmed: bool = False
    one_prior_order_cap_consumed_confirmed: bool = False
    new_owner_approval_required_before_any_future_order_confirmed: bool = False
    owner_manual_runtime_only_confirmed: bool = False
    no_live_endpoint_confirmed: bool = False
    no_autonomous_order_confirmed: bool = False
    post_trade_evidence_required_confirmed: bool = False
    no_profit_claim_confirmed: bool = False
    profit_claim_made: bool = False
    live_endpoint_requested: bool = False
    autonomous_order_requested: bool = False
    second_order_requested: bool = False


def default_corrected_command_package_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "units": 1,
        "reference_price": None,
        "stop_loss": None,
        "take_profit": None,
        "risk_amount": "1.00",
        "client_order_id": CORRECTED_CLIENT_ORDER_ID,
        "order_type": APPROVED_ORDER_TYPE,
        "demo_only_confirmed": False,
        "sltp_validation_passed_confirmed": False,
        "one_prior_order_cap_consumed_confirmed": False,
        "new_owner_approval_required_before_any_future_order_confirmed": False,
        "owner_manual_runtime_only_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_autonomous_order_confirmed": False,
        "post_trade_evidence_required_confirmed": False,
        "no_profit_claim_confirmed": False,
        "profit_claim_made": False,
        "live_endpoint_requested": False,
        "autonomous_order_requested": False,
        "second_order_requested": False,
    }


def build_oanda_demo_corrected_order_command_package_v1(
    command_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = default_corrected_command_package_context_v1()
    if command_context:
        context.update(dict(command_context))

    normalized = _normalize_input(context)
    sltp_result = evaluate_oanda_demo_sltp_validation_correction_v1(
        {
            "instrument": normalized.instrument,
            "direction": normalized.direction,
            "reference_price": normalized.reference_price,
            "stop_loss": normalized.stop_loss,
            "take_profit": normalized.take_profit,
            "demo_only_confirmed": normalized.demo_only_confirmed,
            "no_broker_call_confirmed": True,
            "no_second_order_confirmed": True,
            "no_live_endpoint_confirmed": normalized.no_live_endpoint_confirmed,
            "no_profit_claim_confirmed": normalized.no_profit_claim_confirmed,
            "second_order_requested": normalized.second_order_requested,
            "live_endpoint_requested": normalized.live_endpoint_requested,
            "profit_claim_made": normalized.profit_claim_made,
        }
    )

    blockers = _classify_blockers(normalized, sltp_result)
    classification = blockers[0] if blockers else CORRECTED_ORDER_COMMAND_PACKAGE_READY
    package_ready = classification == CORRECTED_ORDER_COMMAND_PACKAGE_READY

    return {
        "packet_id": PACKET_ID,
        "script_status": classification,
        "classification": classification,
        "package_ready": package_ready,
        "blockers": blockers,
        "sltp_validation": {
            "classification": sltp_result.get("classification"),
            "validation_ready": sltp_result.get("validation_ready"),
            "blockers": sltp_result.get("blockers", []),
        },
        "corrected_order_command_package": {
            "template_only": True,
            "owner_command_template": _owner_transport_command_template(normalized)
            if package_ready
            else None,
            "validation_command_template": _validation_command_template(normalized),
            "prior_one_order_cap_consumed": True,
            "future_order_requires_separate_owner_approval": True,
            "order_authorized_by_this_package": False,
            "second_order_allowed_by_this_package": False,
            "post_trade_evidence_required_after_any_future_approved_run": True,
        },
        "input_summary": {
            "instrument": normalized.instrument,
            "direction": normalized.direction,
            "units": normalized.units,
            "reference_price": _string_or_none(normalized.reference_price),
            "stop_loss": _string_or_none(normalized.stop_loss),
            "take_profit": _string_or_none(normalized.take_profit),
            "risk_amount": _string_or_none(normalized.risk_amount),
            "client_order_id": normalized.client_order_id,
            "order_type": normalized.order_type,
        },
        "safety_boundaries": {
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
            "vault_read_performed": False,
            "environment_read_performed": False,
            "dotenv_read_performed": False,
            "live_endpoint_used": False,
            "scheduler_created": False,
            "daemon_created": False,
            "webhook_created": False,
            "profit_claimed": False,
            "fill_claimed": False,
        },
        "next_safe_packet": NEXT_SAFE_PACKET,
        "next_safe_action": "owner_approval_gate_required_before_any_future_demo_order_attempt",
    }


def _classify_blockers(
    normalized: CorrectedCommandPackageInput,
    sltp_result: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []

    if normalized.profit_claim_made or not normalized.no_profit_claim_confirmed:
        blockers.append(BLOCKED_BY_PROFIT_CLAIM)

    if normalized.live_endpoint_requested or not normalized.no_live_endpoint_confirmed:
        blockers.append(BLOCKED_BY_LIVE_ENDPOINT)

    if (
        normalized.autonomous_order_requested
        or not normalized.owner_manual_runtime_only_confirmed
        or not normalized.no_autonomous_order_confirmed
        or not normalized.post_trade_evidence_required_confirmed
    ):
        blockers.append(BLOCKED_BY_AUTONOMY_REQUEST)

    if (
        normalized.second_order_requested
        or not normalized.one_prior_order_cap_consumed_confirmed
        or not normalized.new_owner_approval_required_before_any_future_order_confirmed
    ):
        blockers.append(BLOCKED_BY_PRIOR_ORDER_CAP)

    if not _valid_trade_intent(normalized):
        blockers.append(BLOCKED_BY_INVALID_TRADE_INTENT)

    sltp_classification = sltp_result.get("classification")
    if sltp_classification == BLOCKED_BY_MISSING_REFERENCE_PRICE:
        blockers.append(BLOCKED_BY_MISSING_REFERENCE_PRICE)
    elif sltp_classification == BLOCKED_BY_INVALID_NUMERIC_PRICE:
        blockers.append(BLOCKED_BY_INVALID_TRADE_INTENT)
    elif sltp_classification != SLTP_VALIDATION_READY:
        blockers.append(BLOCKED_BY_SLTP_VALIDATION)

    if not normalized.sltp_validation_passed_confirmed:
        blockers.append(BLOCKED_BY_SLTP_VALIDATION)

    return _dedupe(blockers)


def _valid_trade_intent(normalized: CorrectedCommandPackageInput) -> bool:
    return (
        normalized.demo_only_confirmed
        and normalized.instrument == APPROVED_INSTRUMENT
        and normalized.direction in APPROVED_DIRECTIONS
        and _valid_units(normalized.units)
        and _valid_positive_decimal(normalized.risk_amount)
        and normalized.client_order_id == CORRECTED_CLIENT_ORDER_ID
        and normalized.order_type == APPROVED_ORDER_TYPE
    )


def _owner_transport_command_template(normalized: CorrectedCommandPackageInput) -> str:
    return " ".join(
        [
            "python",
            "scripts/forex_delivery/run_oanda_demo_vault_backed_one_order_transport_v1.py",
            "--execute-vault-backed-demo-one-order",
            "--instrument",
            normalized.instrument,
            "--direction",
            normalized.direction,
            "--units",
            str(normalized.units),
            "--stop-loss",
            str(normalized.stop_loss),
            "--take-profit",
            str(normalized.take_profit),
            "--risk-amount",
            str(normalized.risk_amount),
            "--client-order-id",
            normalized.client_order_id,
            "--order-type",
            normalized.order_type,
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


def _validation_command_template(normalized: CorrectedCommandPackageInput) -> str:
    return " ".join(
        [
            "python",
            "scripts/forex_delivery/run_oanda_demo_sltp_validation_correction_v1.py",
            "--validate-sltp",
            "--instrument",
            normalized.instrument,
            "--direction",
            normalized.direction,
            "--reference-price",
            str(normalized.reference_price),
            "--stop-loss",
            str(normalized.stop_loss),
            "--take-profit",
            str(normalized.take_profit),
            "--i-confirm-demo-only",
            "--i-confirm-no-broker-call",
            "--i-confirm-no-second-order",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-profit-claim",
        ]
    )


def _normalize_input(context: Mapping[str, Any]) -> CorrectedCommandPackageInput:
    return CorrectedCommandPackageInput(
        instrument=str(context.get("instrument", "")).upper(),
        direction=str(context.get("direction", "")).upper(),
        units=context.get("units"),
        reference_price=context.get("reference_price"),
        stop_loss=context.get("stop_loss"),
        take_profit=context.get("take_profit"),
        risk_amount=context.get("risk_amount"),
        client_order_id=str(context.get("client_order_id", "")),
        order_type=str(context.get("order_type", "")).upper(),
        demo_only_confirmed=_bool(context.get("demo_only_confirmed")),
        sltp_validation_passed_confirmed=_bool(
            context.get("sltp_validation_passed_confirmed")
        ),
        one_prior_order_cap_consumed_confirmed=_bool(
            context.get("one_prior_order_cap_consumed_confirmed")
        ),
        new_owner_approval_required_before_any_future_order_confirmed=_bool(
            context.get("new_owner_approval_required_before_any_future_order_confirmed")
        ),
        owner_manual_runtime_only_confirmed=_bool(
            context.get("owner_manual_runtime_only_confirmed")
        ),
        no_live_endpoint_confirmed=_bool(context.get("no_live_endpoint_confirmed")),
        no_autonomous_order_confirmed=_bool(
            context.get("no_autonomous_order_confirmed")
        ),
        post_trade_evidence_required_confirmed=_bool(
            context.get("post_trade_evidence_required_confirmed")
        ),
        no_profit_claim_confirmed=_bool(context.get("no_profit_claim_confirmed")),
        profit_claim_made=_bool(context.get("profit_claim_made")),
        live_endpoint_requested=_bool(context.get("live_endpoint_requested")),
        autonomous_order_requested=_bool(context.get("autonomous_order_requested")),
        second_order_requested=_bool(context.get("second_order_requested")),
    )


def _valid_units(value: Any) -> bool:
    try:
        units = int(value)
    except (TypeError, ValueError):
        return False
    return 1 <= units <= 1000


def _valid_positive_decimal(value: Any) -> bool:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return False
    return parsed > 0 and parsed.is_finite()


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _bool(value: Any) -> bool:
    return bool(value)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value not in seen:
            deduped.append(value)
            seen.add(value)
    return deduped
