from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


DEMO_OPERATOR_EXECUTION_TICKET_VERSION = "demo_operator_execution_ticket_v1"
DO_NOT_EXECUTE_WARNING = "Do not execute unless Anthony explicitly approves."

DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW = "DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW"
DEMO_OPERATOR_TICKET_BLOCKED_NO_ORDER_PLAN = "DEMO_OPERATOR_TICKET_BLOCKED_NO_ORDER_PLAN"
DEMO_OPERATOR_TICKET_BLOCKED_RISK = "DEMO_OPERATOR_TICKET_BLOCKED_RISK"
DEMO_OPERATOR_TICKET_BLOCKED_BROKER_STATE = "DEMO_OPERATOR_TICKET_BLOCKED_BROKER_STATE"
DEMO_OPERATOR_TICKET_BLOCKED_OWNER_APPROVAL_REQUIRED = "DEMO_OPERATOR_TICKET_BLOCKED_OWNER_APPROVAL_REQUIRED"


@dataclass(frozen=True)
class DemoOperatorTicketInput:
    selected_strategy: str
    supertrend_status: str
    instrument: str
    direction: str
    units: int
    stop_loss: Decimal
    take_profit: Decimal
    max_loss: Decimal
    expected_reward: Decimal
    reason_for_trade: str
    reason_not_to_trade: str
    checklist: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    owner_approval_required: bool
    order_plan_present: bool
    risk_ready: bool
    broker_state_ready: bool


@dataclass(frozen=True)
class DemoOperatorTicketResult:
    engine_version: str
    classification: str
    selected_strategy: str
    supertrend_status: str
    instrument: str
    direction: str
    units: int
    stop_loss: Decimal
    take_profit: Decimal
    max_loss: Decimal
    expected_reward: Decimal
    reason_for_trade: str
    reason_not_to_trade: str
    checklist: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    owner_approval_required: bool
    exact_warning: str
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool


def build_sample_operator_ticket_input() -> DemoOperatorTicketInput:
    return DemoOperatorTicketInput(
        selected_strategy="Supertrend",
        supertrend_status="SUPER_TREND_PROOF_REVIEW_READY",
        instrument="EUR_USD",
        direction="LONG",
        units=20000,
        stop_loss=Decimal("1.0950"),
        take_profit=Decimal("1.1100"),
        max_loss=Decimal("100.00"),
        expected_reward=Decimal("200.00"),
        reason_for_trade="Supertrend is the strongest deterministic local proof-review sample.",
        reason_not_to_trade="Execution is still blocked until Anthony explicitly approves a supervised demo action.",
        checklist=(
            "Confirm sanitized read-only broker snapshot.",
            "Confirm account readiness and no unknown exposure.",
            "Confirm stop loss, take profit, and duplicate-order guard.",
            "Confirm this is demo-only and supervised.",
        ),
        blocked_actions=(
            "broker action",
            "real money",
            "compounding",
            "bank movement",
            "live trading",
        ),
        owner_approval_required=True,
        order_plan_present=True,
        risk_ready=True,
        broker_state_ready=True,
    )


def build_blocked_operator_ticket_input() -> DemoOperatorTicketInput:
    sample = build_sample_operator_ticket_input()
    return _replace_input(sample, order_plan_present=False)


def build_demo_operator_execution_ticket(
    ticket_input: DemoOperatorTicketInput | Mapping[str, Any] | None = None,
) -> DemoOperatorTicketResult:
    active = _coerce_input(ticket_input or build_sample_operator_ticket_input())
    classification = _classify(active)
    return DemoOperatorTicketResult(
        engine_version=DEMO_OPERATOR_EXECUTION_TICKET_VERSION,
        classification=classification,
        selected_strategy=active.selected_strategy,
        supertrend_status=active.supertrend_status,
        instrument=active.instrument,
        direction=active.direction,
        units=active.units,
        stop_loss=active.stop_loss,
        take_profit=active.take_profit,
        max_loss=active.max_loss,
        expected_reward=active.expected_reward,
        reason_for_trade=active.reason_for_trade,
        reason_not_to_trade=active.reason_not_to_trade,
        checklist=active.checklist,
        blocked_actions=active.blocked_actions,
        owner_approval_required=True,
        exact_warning=DO_NOT_EXECUTE_WARNING,
        next_safe_action=_next_safe_action(classification),
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
    )


def demo_operator_ticket_to_jsonable_dict(result: DemoOperatorTicketResult) -> dict[str, Any]:
    return _json_value(result)


def demo_operator_ticket_to_operator_text(result: DemoOperatorTicketResult | None = None) -> str:
    active = result or build_demo_operator_execution_ticket()
    return (
        f"Operator ticket status: {active.classification}. {active.selected_strategy} "
        f"{active.direction} {active.instrument}, {active.units} units. {DO_NOT_EXECUTE_WARNING}"
    )


def demo_operator_ticket_to_markdown(result: DemoOperatorTicketResult | None = None) -> str:
    active = result or build_demo_operator_execution_ticket()
    checklist = "\n".join(f"- {item}" for item in active.checklist)
    blocked = "\n".join(f"- {item}" for item in active.blocked_actions)
    return "\n".join(
        [
            "# Demo Operator Execution Ticket V1",
            "",
            DO_NOT_EXECUTE_WARNING,
            "",
            f"- Status: {active.classification}",
            f"- Selected strategy: {active.selected_strategy}",
            f"- Supertrend status: {active.supertrend_status}",
            f"- Instrument: {active.instrument}",
            f"- Direction: {active.direction}",
            f"- Units: {active.units}",
            f"- Stop loss: {active.stop_loss}",
            f"- Take profit: {active.take_profit}",
            f"- Max loss: {active.max_loss}",
            f"- Expected reward: {active.expected_reward}",
            f"- Reason for trade: {active.reason_for_trade}",
            f"- Reason not to trade: {active.reason_not_to_trade}",
            "",
            "## Checklist",
            checklist,
            "",
            "## Blocked Actions",
            blocked,
            "",
            "No trade was placed.",
        ]
    )


def _classify(value: DemoOperatorTicketInput) -> str:
    if not value.order_plan_present:
        return DEMO_OPERATOR_TICKET_BLOCKED_NO_ORDER_PLAN
    if not value.risk_ready:
        return DEMO_OPERATOR_TICKET_BLOCKED_RISK
    if not value.broker_state_ready:
        return DEMO_OPERATOR_TICKET_BLOCKED_BROKER_STATE
    if not value.owner_approval_required:
        return DEMO_OPERATOR_TICKET_BLOCKED_OWNER_APPROVAL_REQUIRED
    return DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW:
        return "Anthony must review the ticket manually; Codex must not execute."
    return "Resolve the ticket blocker before any owner review."


def _replace_input(value: DemoOperatorTicketInput, **updates: Any) -> DemoOperatorTicketInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoOperatorTicketInput(**raw)


def _coerce_input(value: DemoOperatorTicketInput | Mapping[str, Any]) -> DemoOperatorTicketInput:
    if isinstance(value, DemoOperatorTicketInput):
        return value
    raw = dict(value)
    for name in ("stop_loss", "take_profit", "max_loss", "expected_reward"):
        raw[name] = _to_decimal(raw[name])
    raw["checklist"] = tuple(raw["checklist"])
    raw["blocked_actions"] = tuple(raw["blocked_actions"])
    return DemoOperatorTicketInput(**raw)


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if is_dataclass(value):
        return {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value
