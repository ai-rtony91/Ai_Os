"""Sanitized non-executing ticket preview for one tiny supervised microtrade."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    EXACT_LIVE_WARNING,
    EXACT_OWNER_WARNING,
    PROTECTED_FLAG_NAMES,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
)


VERSION = "oanda_supervised_live_microtrade_ticket_preview_v1"

OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_READY_FOR_OWNER_REVIEW = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_READY_FOR_OWNER_REVIEW"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_REQUIRE_REPAIR = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_REQUIRE_REPAIR"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE"
)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeTicketPreviewInput:
    sanitized_local_ticket_id: str
    instrument: str
    direction: str
    order_type: str
    planned_units: Decimal
    max_units: Decimal
    planned_max_loss: Decimal
    planned_stop_distance: Decimal
    planned_take_profit_distance: Decimal
    planned_risk_r: Decimal
    one_shot_only: bool = True
    no_compounding: bool = True
    no_bank_movement: bool = True
    no_autonomous_loop: bool = True
    owner_final_approval_required: bool = True
    preview_only: bool = True
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeTicketPreviewResult:
    version: str
    classification: str
    sanitized_local_ticket_id: str
    instrument: str
    direction: str
    order_type: str
    planned_units: Decimal
    max_units: Decimal
    planned_max_loss: Decimal
    planned_stop_distance: Decimal
    planned_take_profit_distance: Decimal
    planned_risk_r: Decimal
    one_shot_only: bool
    no_compounding: bool
    no_bank_movement: bool
    no_autonomous_loop: bool
    owner_final_approval_required: bool
    preview_only: bool
    profit_guaranteed: bool
    live_approval_granted: bool
    repair_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    ticket_preview: Mapping[str, Any]
    owner_warning: str
    live_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    codex_live_execution_authorized: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool


def build_sample_ready_input() -> OandaSupervisedLiveMicrotradeTicketPreviewInput:
    return OandaSupervisedLiveMicrotradeTicketPreviewInput(
        sanitized_local_ticket_id="LOCAL-MICROTRADE-PREVIEW-001",
        instrument="EUR_USD",
        direction="long",
        order_type="market_owner_manual",
        planned_units=Decimal("1"),
        max_units=Decimal("1"),
        planned_max_loss=Decimal("1.00"),
        planned_stop_distance=Decimal("0.0010"),
        planned_take_profit_distance=Decimal("0.0015"),
        planned_risk_r=Decimal("1.00"),
    )


def build_sample_missing_input() -> OandaSupervisedLiveMicrotradeTicketPreviewInput:
    sample = build_sample_ready_input()
    return OandaSupervisedLiveMicrotradeTicketPreviewInput(
        sanitized_local_ticket_id=sample.sanitized_local_ticket_id,
        instrument=sample.instrument,
        direction=sample.direction,
        order_type=sample.order_type,
        planned_units=Decimal("3"),
        max_units=Decimal("1"),
        planned_max_loss=Decimal("1.00"),
        planned_stop_distance=Decimal("0.0010"),
        planned_take_profit_distance=Decimal("0.0015"),
        planned_risk_r=Decimal("1.00"),
    )


def build_sample_unsafe_input() -> OandaSupervisedLiveMicrotradeTicketPreviewInput:
    sample = build_sample_ready_input()
    return OandaSupervisedLiveMicrotradeTicketPreviewInput(
        sanitized_local_ticket_id="LOCAL-MICROTRADE-PREVIEW-UNSAFE",
        instrument=sample.instrument,
        direction=sample.direction,
        order_type=sample.order_type,
        planned_units=Decimal("1"),
        max_units=Decimal("1"),
        planned_max_loss=Decimal("1.00"),
        planned_stop_distance=Decimal("0.0010"),
        planned_take_profit_distance=Decimal("0.0015"),
        planned_risk_r=Decimal("1.00"),
        owner_final_approval_required=False,
        unsafe_flags={"owner_final_approval_missing": True},
    )


def build_oanda_supervised_live_microtrade_ticket_preview(
    ticket_input: OandaSupervisedLiveMicrotradeTicketPreviewInput | Mapping[str, Any] | None = None,
) -> OandaSupervisedLiveMicrotradeTicketPreviewResult:
    active_input = _coerce_input(ticket_input or build_sample_ready_input())
    repair_items = _repair_items(active_input)
    blocked_items = _blocked_items(active_input)
    if blocked_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE
    elif repair_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_REQUIRE_REPAIR
    else:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    preview = {
        "sanitized_local_ticket_id": active_input.sanitized_local_ticket_id,
        "instrument": active_input.instrument,
        "direction": active_input.direction,
        "order_type": active_input.order_type,
        "planned_units": active_input.planned_units,
        "max_units": active_input.max_units,
        "planned_max_loss": active_input.planned_max_loss,
        "planned_stop_distance": active_input.planned_stop_distance,
        "planned_take_profit_distance": active_input.planned_take_profit_distance,
        "planned_risk_r": active_input.planned_risk_r,
        "one_shot_only": active_input.one_shot_only,
        "no_compounding": active_input.no_compounding,
        "no_bank_movement": active_input.no_bank_movement,
        "no_autonomous_loop": active_input.no_autonomous_loop,
        "owner_final_approval_required": active_input.owner_final_approval_required,
        "preview_only": active_input.preview_only,
        "profit_guaranteed": False,
        "live_approval_granted": False,
    }
    return OandaSupervisedLiveMicrotradeTicketPreviewResult(
        version=VERSION,
        classification=classification,
        sanitized_local_ticket_id=active_input.sanitized_local_ticket_id,
        instrument=active_input.instrument,
        direction=active_input.direction,
        order_type=active_input.order_type,
        planned_units=active_input.planned_units,
        max_units=active_input.max_units,
        planned_max_loss=active_input.planned_max_loss,
        planned_stop_distance=active_input.planned_stop_distance,
        planned_take_profit_distance=active_input.planned_take_profit_distance,
        planned_risk_r=active_input.planned_risk_r,
        one_shot_only=active_input.one_shot_only,
        no_compounding=active_input.no_compounding,
        no_bank_movement=active_input.no_bank_movement,
        no_autonomous_loop=active_input.no_autonomous_loop,
        owner_final_approval_required=active_input.owner_final_approval_required,
        preview_only=active_input.preview_only,
        profit_guaranteed=False,
        live_approval_granted=False,
        repair_items=repair_items,
        blocked_items=blocked_items,
        ticket_preview=jsonable(preview),
        owner_warning=EXACT_OWNER_WARNING,
        live_warning=EXACT_LIVE_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaSupervisedLiveMicrotradeTicketPreviewResult) -> str:
    return "\n".join(
        (
            f"Ticket preview status: {result.classification}.",
            f"Sanitized local ticket id: {result.sanitized_local_ticket_id}.",
            "This is a preview only; no executable order function is present.",
            result.owner_warning,
            result.live_warning,
        )
    )


def to_markdown(result: OandaSupervisedLiveMicrotradeTicketPreviewResult) -> str:
    rows = [
        "# AIOS Forex OANDA Supervised Live Microtrade Ticket Preview V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Sanitized local ticket id: `{result.sanitized_local_ticket_id}`",
        f"- Instrument: `{result.instrument}`",
        f"- Direction: `{result.direction}`",
        f"- Order type: `{result.order_type}`",
        f"- Planned units: `{jsonable(result.planned_units)}`",
        f"- Max units: `{jsonable(result.max_units)}`",
        f"- Planned max loss: `{jsonable(result.planned_max_loss)}`",
        f"- Planned stop distance: `{jsonable(result.planned_stop_distance)}`",
        f"- Planned take-profit distance: `{jsonable(result.planned_take_profit_distance)}`",
        f"- Planned R risk: `{jsonable(result.planned_risk_r)}`",
        "- Preview only.",
        "- No profit guarantee.",
        "- No live approval.",
    ]
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaSupervisedLiveMicrotradeTicketPreviewInput | Mapping[str, Any],
) -> OandaSupervisedLiveMicrotradeTicketPreviewInput:
    if isinstance(value, OandaSupervisedLiveMicrotradeTicketPreviewInput):
        return value
    raw = dict(value)
    return OandaSupervisedLiveMicrotradeTicketPreviewInput(
        sanitized_local_ticket_id=str(raw.get("sanitized_local_ticket_id", "")),
        instrument=str(raw.get("instrument", "")),
        direction=str(raw.get("direction", "")),
        order_type=str(raw.get("order_type", "")),
        planned_units=_decimal(raw.get("planned_units", "0")),
        max_units=_decimal(raw.get("max_units", "0")),
        planned_max_loss=_decimal(raw.get("planned_max_loss", "0")),
        planned_stop_distance=_decimal(raw.get("planned_stop_distance", "0")),
        planned_take_profit_distance=_decimal(raw.get("planned_take_profit_distance", "0")),
        planned_risk_r=_decimal(raw.get("planned_risk_r", "0")),
        one_shot_only=bool(raw.get("one_shot_only", False)),
        no_compounding=bool(raw.get("no_compounding", False)),
        no_bank_movement=bool(raw.get("no_bank_movement", False)),
        no_autonomous_loop=bool(raw.get("no_autonomous_loop", False)),
        owner_final_approval_required=bool(raw.get("owner_final_approval_required", False)),
        preview_only=bool(raw.get("preview_only", False)),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _repair_items(active_input: OandaSupervisedLiveMicrotradeTicketPreviewInput) -> tuple[str, ...]:
    repairs: list[str] = []
    if not active_input.sanitized_local_ticket_id.startswith("LOCAL-"):
        repairs.append("sanitized_local_ticket_id")
    if active_input.planned_units <= Decimal("0"):
        repairs.append("planned_units_positive")
    if active_input.planned_units > Decimal("1"):
        repairs.append("planned_units_tiny")
    if active_input.max_units < active_input.planned_units or active_input.max_units > Decimal("1"):
        repairs.append("max_units_bounded")
    if active_input.planned_max_loss <= Decimal("0") or active_input.planned_max_loss > Decimal("1.00"):
        repairs.append("planned_max_loss_bounded")
    if active_input.planned_stop_distance <= Decimal("0"):
        repairs.append("planned_stop_distance_positive")
    if active_input.planned_take_profit_distance <= Decimal("0"):
        repairs.append("planned_take_profit_distance_positive")
    if active_input.planned_risk_r <= Decimal("0") or active_input.planned_risk_r > Decimal("1.00"):
        repairs.append("planned_risk_r_bounded")
    for field_name in (
        "one_shot_only",
        "no_compounding",
        "no_bank_movement",
        "no_autonomous_loop",
        "owner_final_approval_required",
        "preview_only",
    ):
        if not bool(getattr(active_input, field_name)):
            repairs.append(field_name)
    return tuple(repairs)


def _blocked_items(active_input: OandaSupervisedLiveMicrotradeTicketPreviewInput) -> tuple[str, ...]:
    blocked = [name for name, value in active_input.unsafe_flags.items() if bool(value)]
    if not active_input.owner_final_approval_required:
        blocked.append("owner_final_approval_required_false")
    return tuple(dict.fromkeys(blocked))


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


assert tuple(PROTECTED_FLAG_NAMES)

