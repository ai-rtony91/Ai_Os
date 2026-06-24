"""Corrected future OANDA demo runtime packet builder.

This module builds a sanitized owner-only runtime command template. It never
calls OANDA, never reads credentials or Vault, and never authorizes Codex to
execute the command.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_corrected_order_command_package_v1 import (
    CORRECTED_CLIENT_ORDER_ID,
    CORRECTED_ORDER_COMMAND_PACKAGE_READY,
    build_oanda_demo_corrected_order_command_package_v1,
)
from automation.forex_engine.oanda_demo_future_order_approval_gate_v1 import (
    OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION,
    evaluate_oanda_demo_future_order_approval_gate_v1,
)


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-CORRECTED-FUTURE-RUNTIME-PACKET-V1"

CORRECTED_FUTURE_RUNTIME_PACKET_READY = "CORRECTED_FUTURE_RUNTIME_PACKET_READY"
BLOCKED_BY_MISSING_CORRECTED_PACKAGE = "BLOCKED_BY_MISSING_CORRECTED_PACKAGE"
BLOCKED_BY_MISSING_APPROVAL_GATE = "BLOCKED_BY_MISSING_APPROVAL_GATE"
BLOCKED_BY_SLTP_VALIDATION = "BLOCKED_BY_SLTP_VALIDATION"
BLOCKED_BY_INVALID_TRADE_INTENT = "BLOCKED_BY_INVALID_TRADE_INTENT"
BLOCKED_BY_LIVE_ENDPOINT = "BLOCKED_BY_LIVE_ENDPOINT"
BLOCKED_BY_AUTONOMY_REQUEST = "BLOCKED_BY_AUTONOMY_REQUEST"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"

APPROVED_INSTRUMENT = "EUR_USD"
APPROVED_DIRECTIONS = {"BUY", "SELL"}
APPROVED_ORDER_TYPE = "MARKET"
FUTURE_CLIENT_ORDER_ID = "AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001"


@dataclass(frozen=True)
class CorrectedFutureRuntimePacketInput:
    instrument: str = APPROVED_INSTRUMENT
    direction: str = "BUY"
    units: Any = 1
    reference_price: Any = None
    stop_loss: Any = None
    take_profit: Any = None
    risk_amount: Any = "1.00"
    client_order_id: str = FUTURE_CLIENT_ORDER_ID
    order_type: str = APPROVED_ORDER_TYPE
    corrected_package_ready_confirmed: bool = False
    future_approval_gate_ready_confirmed: bool = False
    sltp_validation_ready_confirmed: bool = False
    demo_only_confirmed: bool = False
    owner_manual_runtime_only_confirmed: bool = False
    no_live_endpoint_confirmed: bool = False
    no_autonomous_order_confirmed: bool = False
    post_trade_evidence_required_confirmed: bool = False
    no_profit_claim_confirmed: bool = False
    live_endpoint_requested: bool = False
    autonomous_order_requested: bool = False
    profit_claim_made: bool = False


def default_corrected_future_runtime_packet_context_v1() -> dict[str, Any]:
    return {
        "instrument": APPROVED_INSTRUMENT,
        "direction": "BUY",
        "units": 1,
        "reference_price": None,
        "stop_loss": None,
        "take_profit": None,
        "risk_amount": "1.00",
        "client_order_id": FUTURE_CLIENT_ORDER_ID,
        "order_type": APPROVED_ORDER_TYPE,
        "corrected_package_ready_confirmed": False,
        "future_approval_gate_ready_confirmed": False,
        "sltp_validation_ready_confirmed": False,
        "demo_only_confirmed": False,
        "owner_manual_runtime_only_confirmed": False,
        "no_live_endpoint_confirmed": False,
        "no_autonomous_order_confirmed": False,
        "post_trade_evidence_required_confirmed": False,
        "no_profit_claim_confirmed": False,
        "live_endpoint_requested": False,
        "autonomous_order_requested": False,
        "profit_claim_made": False,
    }


def build_oanda_demo_corrected_future_runtime_packet_v1(
    runtime_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    context = default_corrected_future_runtime_packet_context_v1()
    if runtime_context:
        context.update(dict(runtime_context))

    normalized = _normalize_input(context)
    numeric_prices = _numeric_prices(normalized)
    local_sltp_ready = _local_sltp_ready(normalized, numeric_prices)
    corrected_package = _corrected_package_result(normalized)
    approval_gate = _approval_gate_result(
        normalized,
        corrected_package_ready=(
            corrected_package.get("classification")
            == CORRECTED_ORDER_COMMAND_PACKAGE_READY
        ),
        local_sltp_ready=local_sltp_ready,
    )

    blockers = _classify_blockers(
        normalized=normalized,
        numeric_prices=numeric_prices,
        local_sltp_ready=local_sltp_ready,
        corrected_package=corrected_package,
        approval_gate=approval_gate,
    )
    classification = (
        blockers[0] if blockers else CORRECTED_FUTURE_RUNTIME_PACKET_READY
    )
    packet_ready = classification == CORRECTED_FUTURE_RUNTIME_PACKET_READY

    return {
        "packet_id": PACKET_ID,
        "script_status": classification,
        "classification": classification,
        "runtime_packet_ready": packet_ready,
        "blockers": blockers,
        "prior_evidence": {
            "result_bucket": "CANCELED_NOT_FILLED",
            "cancel_reason": "TAKE_PROFIT_ON_FILL_LOSS",
            "fill_claimed": False,
            "profit_claimed": False,
            "order_fill_transaction_observed": False,
        },
        "corrected_package_evidence": {
            "classification": corrected_package.get("classification"),
            "package_ready": corrected_package.get("package_ready"),
        },
        "approval_gate_evidence": {
            "classification": approval_gate.get("classification"),
            "ready_for_manual_decision": approval_gate.get(
                "ready_for_manual_decision"
            ),
            "order_execution_authorized": False,
        },
        "sltp_validation": {
            "classification": (
                "SLTP_VALIDATION_READY"
                if local_sltp_ready
                else "BLOCKED_BY_SLTP_VALIDATION"
            ),
            "validation_ready": local_sltp_ready,
            "buy_rule": "stop_loss < reference_price < take_profit",
            "sell_rule": "take_profit < reference_price < stop_loss",
        },
        "runtime_packet": {
            "owner_only": True,
            "owner_command_template": _owner_transport_command_template(normalized)
            if packet_ready
            else None,
            "codex_execution_authorized": False,
            "order_authorized_for_codex": False,
            "broker_command_run_by_codex": False,
            "post_trade_evidence_required": True,
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
        "next_safe_action": (
            "owner_only_review_corrected_template_and_capture_post_trade_evidence_if_run"
        ),
    }


def _classify_blockers(
    *,
    normalized: CorrectedFutureRuntimePacketInput,
    numeric_prices: Mapping[str, Decimal] | None,
    local_sltp_ready: bool,
    corrected_package: Mapping[str, Any],
    approval_gate: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []

    if not normalized.corrected_package_ready_confirmed:
        blockers.append(BLOCKED_BY_MISSING_CORRECTED_PACKAGE)

    if not normalized.future_approval_gate_ready_confirmed:
        blockers.append(BLOCKED_BY_MISSING_APPROVAL_GATE)

    if normalized.live_endpoint_requested or not normalized.no_live_endpoint_confirmed:
        blockers.append(BLOCKED_BY_LIVE_ENDPOINT)

    if (
        normalized.autonomous_order_requested
        or not normalized.owner_manual_runtime_only_confirmed
        or not normalized.no_autonomous_order_confirmed
        or not normalized.post_trade_evidence_required_confirmed
    ):
        blockers.append(BLOCKED_BY_AUTONOMY_REQUEST)

    if normalized.profit_claim_made or not normalized.no_profit_claim_confirmed:
        blockers.append(BLOCKED_BY_PROFIT_CLAIM)

    if numeric_prices is None or not _valid_trade_intent(normalized):
        blockers.append(BLOCKED_BY_INVALID_TRADE_INTENT)

    if not normalized.sltp_validation_ready_confirmed or not local_sltp_ready:
        blockers.append(BLOCKED_BY_SLTP_VALIDATION)

    if normalized.corrected_package_ready_confirmed and not corrected_package.get(
        "package_ready"
    ):
        blockers.append(BLOCKED_BY_MISSING_CORRECTED_PACKAGE)

    if normalized.future_approval_gate_ready_confirmed and approval_gate.get(
        "classification"
    ) != OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION:
        blockers.append(BLOCKED_BY_MISSING_APPROVAL_GATE)

    return _dedupe(blockers)


def _corrected_package_result(
    normalized: CorrectedFutureRuntimePacketInput,
) -> Mapping[str, Any]:
    return build_oanda_demo_corrected_order_command_package_v1(
        {
            "instrument": normalized.instrument,
            "direction": normalized.direction,
            "units": normalized.units,
            "reference_price": normalized.reference_price,
            "stop_loss": normalized.stop_loss,
            "take_profit": normalized.take_profit,
            "risk_amount": normalized.risk_amount,
            "client_order_id": CORRECTED_CLIENT_ORDER_ID,
            "order_type": normalized.order_type,
            "demo_only_confirmed": normalized.demo_only_confirmed,
            "sltp_validation_passed_confirmed": (
                normalized.sltp_validation_ready_confirmed
            ),
            "one_prior_order_cap_consumed_confirmed": True,
            "new_owner_approval_required_before_any_future_order_confirmed": True,
            "owner_manual_runtime_only_confirmed": (
                normalized.owner_manual_runtime_only_confirmed
            ),
            "no_live_endpoint_confirmed": normalized.no_live_endpoint_confirmed,
            "no_autonomous_order_confirmed": (
                normalized.no_autonomous_order_confirmed
            ),
            "post_trade_evidence_required_confirmed": (
                normalized.post_trade_evidence_required_confirmed
            ),
            "no_profit_claim_confirmed": normalized.no_profit_claim_confirmed,
            "profit_claim_made": normalized.profit_claim_made,
            "live_endpoint_requested": normalized.live_endpoint_requested,
            "autonomous_order_requested": normalized.autonomous_order_requested,
            "second_order_requested": False,
        }
    )


def _approval_gate_result(
    normalized: CorrectedFutureRuntimePacketInput,
    *,
    corrected_package_ready: bool,
    local_sltp_ready: bool,
) -> Mapping[str, Any]:
    return evaluate_oanda_demo_future_order_approval_gate_v1(
        {
            "corrected_order_package_ready": (
                normalized.corrected_package_ready_confirmed
                and corrected_package_ready
            ),
            "sltp_validation_ready": (
                normalized.sltp_validation_ready_confirmed and local_sltp_ready
            ),
            "prior_cancel_evidence_captured": True,
            "prior_order_cap_consumed_acknowledged": True,
            "explicit_new_owner_approval": (
                normalized.future_approval_gate_ready_confirmed
            ),
            "demo_only": normalized.demo_only_confirmed,
            "one_order_only": True,
            "no_live_endpoint": normalized.no_live_endpoint_confirmed,
            "no_autonomous_order": normalized.no_autonomous_order_confirmed,
            "post_trade_evidence_required": (
                normalized.post_trade_evidence_required_confirmed
            ),
            "no_profit_claim": normalized.no_profit_claim_confirmed,
            "live_endpoint_requested": normalized.live_endpoint_requested,
            "autonomous_order_requested": normalized.autonomous_order_requested,
            "profit_claim_made": normalized.profit_claim_made,
        }
    )


def _valid_trade_intent(normalized: CorrectedFutureRuntimePacketInput) -> bool:
    return (
        normalized.demo_only_confirmed
        and normalized.instrument == APPROVED_INSTRUMENT
        and normalized.direction in APPROVED_DIRECTIONS
        and _valid_units(normalized.units)
        and _valid_positive_decimal(normalized.risk_amount)
        and normalized.client_order_id == FUTURE_CLIENT_ORDER_ID
        and normalized.order_type == APPROVED_ORDER_TYPE
    )


def _local_sltp_ready(
    normalized: CorrectedFutureRuntimePacketInput,
    numeric_prices: Mapping[str, Decimal] | None,
) -> bool:
    if numeric_prices is None:
        return False
    reference = numeric_prices["reference_price"]
    stop_loss = numeric_prices["stop_loss"]
    take_profit = numeric_prices["take_profit"]
    if normalized.direction == "BUY":
        return stop_loss < reference and take_profit > reference
    if normalized.direction == "SELL":
        return stop_loss > reference and take_profit < reference
    return False


def _numeric_prices(
    normalized: CorrectedFutureRuntimePacketInput,
) -> dict[str, Decimal] | None:
    parsed = {
        "reference_price": _positive_decimal_or_none(normalized.reference_price),
        "stop_loss": _positive_decimal_or_none(normalized.stop_loss),
        "take_profit": _positive_decimal_or_none(normalized.take_profit),
    }
    if any(value is None for value in parsed.values()):
        return None
    return {key: value for key, value in parsed.items() if value is not None}


def _owner_transport_command_template(
    normalized: CorrectedFutureRuntimePacketInput,
) -> str:
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


def _normalize_input(
    context: Mapping[str, Any],
) -> CorrectedFutureRuntimePacketInput:
    return CorrectedFutureRuntimePacketInput(
        instrument=str(context.get("instrument", "")).upper(),
        direction=str(context.get("direction", "")).upper(),
        units=context.get("units"),
        reference_price=context.get("reference_price"),
        stop_loss=context.get("stop_loss"),
        take_profit=context.get("take_profit"),
        risk_amount=context.get("risk_amount"),
        client_order_id=str(context.get("client_order_id", "")),
        order_type=str(context.get("order_type", "")).upper(),
        corrected_package_ready_confirmed=_bool(
            context.get("corrected_package_ready_confirmed")
        ),
        future_approval_gate_ready_confirmed=_bool(
            context.get("future_approval_gate_ready_confirmed")
        ),
        sltp_validation_ready_confirmed=_bool(
            context.get("sltp_validation_ready_confirmed")
        ),
        demo_only_confirmed=_bool(context.get("demo_only_confirmed")),
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
        live_endpoint_requested=_bool(context.get("live_endpoint_requested")),
        autonomous_order_requested=_bool(context.get("autonomous_order_requested")),
        profit_claim_made=_bool(context.get("profit_claim_made")),
    )


def _valid_units(value: Any) -> bool:
    try:
        units = int(value)
    except (TypeError, ValueError):
        return False
    return 1 <= units <= 1000


def _valid_positive_decimal(value: Any) -> bool:
    return _positive_decimal_or_none(value) is not None


def _positive_decimal_or_none(value: Any) -> Decimal | None:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not parsed.is_finite() or parsed <= 0:
        return None
    return parsed


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
