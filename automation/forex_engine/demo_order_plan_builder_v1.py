from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


DEMO_ORDER_PLAN_BUILDER_VERSION = "demo_order_plan_builder_v1"

DEMO_ORDER_PLAN_REVIEW_READY = "DEMO_ORDER_PLAN_REVIEW_READY"
DEMO_ORDER_PLAN_BLOCKED_ACCOUNT = "DEMO_ORDER_PLAN_BLOCKED_ACCOUNT"
DEMO_ORDER_PLAN_BLOCKED_RISK = "DEMO_ORDER_PLAN_BLOCKED_RISK"
DEMO_ORDER_PLAN_BLOCKED_POSITION_SIZE = "DEMO_ORDER_PLAN_BLOCKED_POSITION_SIZE"
DEMO_ORDER_PLAN_BLOCKED_STRATEGY = "DEMO_ORDER_PLAN_BLOCKED_STRATEGY"
DEMO_ORDER_PLAN_BLOCKED_OPERATOR_APPROVAL = "DEMO_ORDER_PLAN_BLOCKED_OPERATOR_APPROVAL"


@dataclass(frozen=True)
class DemoOrderPlanInput:
    strategy_id: str
    strategy_name: str
    supertrend_status: str
    instrument: str
    direction: str
    entry_type: str
    entry_price: Decimal
    stop_loss_price: Decimal
    take_profit_price: Decimal
    proposed_units: int
    risk_amount: Decimal
    estimated_reward: Decimal
    reward_to_risk: Decimal
    spread: Decimal
    max_spread: Decimal
    account_ready: bool
    risk_ready: bool
    position_size_ready: bool
    operator_review_required: bool


@dataclass(frozen=True)
class DemoOrderPlanResult:
    engine_version: str
    classification: str
    order_plan_review_allowed: bool
    strategy_id: str
    strategy_name: str
    supertrend_status: str
    instrument: str
    direction: str
    entry_type: str
    entry_price: Decimal
    stop_loss_price: Decimal
    take_profit_price: Decimal
    proposed_units: int
    risk_amount: Decimal
    max_loss: Decimal
    estimated_reward: Decimal
    expected_reward: Decimal
    reward_to_risk: Decimal
    spread: Decimal
    max_spread: Decimal
    operator_review_required: bool
    blockers: tuple[str, ...]
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool


def build_sample_demo_order_plan_input() -> DemoOrderPlanInput:
    return DemoOrderPlanInput(
        strategy_id="supertrend",
        strategy_name="Supertrend",
        supertrend_status="SUPER_TREND_PROOF_REVIEW_READY",
        instrument="EUR_USD",
        direction="LONG",
        entry_type="operator_review_market_entry",
        entry_price=Decimal("1.1000"),
        stop_loss_price=Decimal("1.0950"),
        take_profit_price=Decimal("1.1100"),
        proposed_units=20000,
        risk_amount=Decimal("100.00"),
        estimated_reward=Decimal("200.00"),
        reward_to_risk=Decimal("2.00"),
        spread=Decimal("0.8"),
        max_spread=Decimal("1.5"),
        account_ready=True,
        risk_ready=True,
        position_size_ready=True,
        operator_review_required=True,
    )


def build_sample_blocked_demo_order_plan_input() -> DemoOrderPlanInput:
    sample = build_sample_demo_order_plan_input()
    return _replace_input(sample, account_ready=False)


def build_demo_order_plan(
    order_plan_input: DemoOrderPlanInput | Mapping[str, Any] | None = None,
) -> DemoOrderPlanResult:
    active = _coerce_input(order_plan_input or build_sample_demo_order_plan_input())
    classification = _classify(active)
    return DemoOrderPlanResult(
        engine_version=DEMO_ORDER_PLAN_BUILDER_VERSION,
        classification=classification,
        order_plan_review_allowed=classification == DEMO_ORDER_PLAN_REVIEW_READY,
        strategy_id=active.strategy_id,
        strategy_name=active.strategy_name,
        supertrend_status=active.supertrend_status,
        instrument=active.instrument,
        direction=active.direction,
        entry_type=active.entry_type,
        entry_price=active.entry_price,
        stop_loss_price=active.stop_loss_price,
        take_profit_price=active.take_profit_price,
        proposed_units=active.proposed_units,
        risk_amount=active.risk_amount,
        max_loss=active.risk_amount,
        estimated_reward=active.estimated_reward,
        expected_reward=active.estimated_reward,
        reward_to_risk=active.reward_to_risk,
        spread=active.spread,
        max_spread=active.max_spread,
        operator_review_required=active.operator_review_required,
        blockers=tuple([] if classification == DEMO_ORDER_PLAN_REVIEW_READY else [classification.lower()]),
        next_safe_action=_next_safe_action(classification),
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
    )


def demo_order_plan_to_jsonable_dict(result: DemoOrderPlanResult) -> dict[str, Any]:
    return _json_value(result)


def demo_order_plan_to_operator_text(result: DemoOrderPlanResult | None = None) -> str:
    active = result or build_demo_order_plan()
    if active.order_plan_review_allowed:
        return (
            f"Demo order plan is ready for owner review: {active.strategy_name} {active.direction} "
            f"{active.instrument}, {active.proposed_units} units. No trade was placed."
        )
    return f"Demo order plan is blocked: {'; '.join(active.blockers)}. No trade was placed."


def demo_order_plan_to_markdown(result: DemoOrderPlanResult | None = None) -> str:
    active = result or build_demo_order_plan()
    return "\n".join(
        [
            "# Demo Order Plan V1",
            "",
            "No trade was placed. This is a local-only review package.",
            "",
            f"- Status: {active.classification}",
            f"- Strategy: {active.strategy_name}",
            f"- Supertrend status: {active.supertrend_status}",
            f"- Instrument: {active.instrument}",
            f"- Direction: {active.direction}",
            f"- Entry: {active.entry_type} at {active.entry_price}",
            f"- Stop loss: {active.stop_loss_price}",
            f"- Take profit: {active.take_profit_price}",
            f"- Proposed units: {active.proposed_units}",
            f"- Max loss: {active.max_loss}",
            f"- Expected reward: {active.expected_reward}",
            f"- Reward-to-risk: {active.reward_to_risk}",
            f"- Operator review required: {active.operator_review_required}",
            f"- Broker action allowed: {active.broker_action_allowed}",
        ]
    )


def _classify(value: DemoOrderPlanInput) -> str:
    if not value.account_ready:
        return DEMO_ORDER_PLAN_BLOCKED_ACCOUNT
    if not value.risk_ready:
        return DEMO_ORDER_PLAN_BLOCKED_RISK
    if not value.position_size_ready:
        return DEMO_ORDER_PLAN_BLOCKED_POSITION_SIZE
    if not value.strategy_id or "PROOF_REVIEW_READY" not in value.supertrend_status:
        return DEMO_ORDER_PLAN_BLOCKED_STRATEGY
    if not value.operator_review_required:
        return DEMO_ORDER_PLAN_BLOCKED_OPERATOR_APPROVAL
    return DEMO_ORDER_PLAN_REVIEW_READY


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_ORDER_PLAN_REVIEW_READY:
        return "Prepare the owner execution ticket; do not execute without Anthony's explicit approval."
    return "Resolve the blocked plan gate before preparing an execution ticket."


def _replace_input(value: DemoOrderPlanInput, **updates: Any) -> DemoOrderPlanInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoOrderPlanInput(**raw)


def _coerce_input(value: DemoOrderPlanInput | Mapping[str, Any]) -> DemoOrderPlanInput:
    if isinstance(value, DemoOrderPlanInput):
        return value
    raw = dict(value)
    for name in (
        "entry_price",
        "stop_loss_price",
        "take_profit_price",
        "risk_amount",
        "estimated_reward",
        "reward_to_risk",
        "spread",
        "max_spread",
    ):
        raw[name] = _to_decimal(raw[name])
    return DemoOrderPlanInput(**raw)


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
