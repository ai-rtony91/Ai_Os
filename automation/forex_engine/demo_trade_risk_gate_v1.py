from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


DEMO_TRADE_RISK_GATE_VERSION = "demo_trade_risk_gate_v1"

DEMO_RISK_REVIEW_READY = "DEMO_RISK_REVIEW_READY"
DEMO_RISK_BLOCKED_MAX_RISK = "DEMO_RISK_BLOCKED_MAX_RISK"
DEMO_RISK_BLOCKED_DAILY_LOSS = "DEMO_RISK_BLOCKED_DAILY_LOSS"
DEMO_RISK_BLOCKED_OPEN_TRADES = "DEMO_RISK_BLOCKED_OPEN_TRADES"
DEMO_RISK_BLOCKED_PENDING_ORDERS = "DEMO_RISK_BLOCKED_PENDING_ORDERS"
DEMO_RISK_BLOCKED_SPREAD = "DEMO_RISK_BLOCKED_SPREAD"
DEMO_RISK_BLOCKED_MISSING_STOP_LOSS = "DEMO_RISK_BLOCKED_MISSING_STOP_LOSS"
DEMO_RISK_BLOCKED_MISSING_TAKE_PROFIT = "DEMO_RISK_BLOCKED_MISSING_TAKE_PROFIT"
DEMO_RISK_BLOCKED_DUPLICATE_ORDER = "DEMO_RISK_BLOCKED_DUPLICATE_ORDER"
DEMO_RISK_BLOCKED_KILL_SWITCH = "DEMO_RISK_BLOCKED_KILL_SWITCH"
DEMO_RISK_BLOCKED_MARKET_HOURS = "DEMO_RISK_BLOCKED_MARKET_HOURS"
DEMO_RISK_BLOCKED_STRATEGY_NOT_READY = "DEMO_RISK_BLOCKED_STRATEGY_NOT_READY"


@dataclass(frozen=True)
class DemoTradeRiskConfig:
    reserved: str = "local_only_review"


@dataclass(frozen=True)
class DemoTradeRiskInput:
    max_risk_per_trade: Decimal
    proposed_risk_per_trade: Decimal
    max_daily_loss: Decimal
    current_daily_loss: Decimal
    max_open_trades: int
    current_open_trades: int
    max_pending_orders: int
    current_pending_orders: int
    max_spread: Decimal
    current_spread: Decimal
    stop_loss_present: bool
    take_profit_present: bool
    duplicate_order_guard_clear: bool
    kill_switch_clear: bool
    market_hours_clear: bool
    instrument_verified: bool
    strategy_review_ready: bool


@dataclass(frozen=True)
class DemoTradeRiskResult:
    engine_version: str
    classification: str
    risk_review_allowed: bool
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    blockers: tuple[str, ...]
    next_safe_action: str
    risk_input: DemoTradeRiskInput


def build_sample_valid_risk_input() -> DemoTradeRiskInput:
    return DemoTradeRiskInput(
        max_risk_per_trade=Decimal("100.00"),
        proposed_risk_per_trade=Decimal("100.00"),
        max_daily_loss=Decimal("250.00"),
        current_daily_loss=Decimal("0.00"),
        max_open_trades=1,
        current_open_trades=0,
        max_pending_orders=1,
        current_pending_orders=0,
        max_spread=Decimal("1.5"),
        current_spread=Decimal("0.8"),
        stop_loss_present=True,
        take_profit_present=True,
        duplicate_order_guard_clear=True,
        kill_switch_clear=True,
        market_hours_clear=True,
        instrument_verified=True,
        strategy_review_ready=True,
    )


def build_sample_blocked_risk_input() -> DemoTradeRiskInput:
    sample = build_sample_valid_risk_input()
    return _replace_risk(sample, proposed_risk_per_trade=Decimal("150.00"))


def evaluate_demo_trade_risk(
    risk_input: DemoTradeRiskInput | Mapping[str, Any] | None = None,
) -> DemoTradeRiskResult:
    active = _coerce_input(risk_input or build_sample_valid_risk_input())
    classification = _classify(active)
    blockers = _blockers(classification)
    return DemoTradeRiskResult(
        engine_version=DEMO_TRADE_RISK_GATE_VERSION,
        classification=classification,
        risk_review_allowed=classification == DEMO_RISK_REVIEW_READY,
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        blockers=tuple(blockers),
        next_safe_action=_next_safe_action(classification),
        risk_input=active,
    )


def demo_trade_risk_to_jsonable_dict(result: DemoTradeRiskResult) -> dict[str, Any]:
    return _json_value(result)


def demo_trade_risk_to_operator_text(result: DemoTradeRiskResult | None = None) -> str:
    active = result or evaluate_demo_trade_risk()
    if active.risk_review_allowed:
        return "Risk gate is review-ready. This does not approve execution and no trade was placed."
    return f"Risk gate is blocked: {'; '.join(active.blockers)}. No trade was placed."


def _classify(value: DemoTradeRiskInput) -> str:
    if value.proposed_risk_per_trade > value.max_risk_per_trade:
        return DEMO_RISK_BLOCKED_MAX_RISK
    if value.current_daily_loss >= value.max_daily_loss:
        return DEMO_RISK_BLOCKED_DAILY_LOSS
    if value.current_open_trades >= value.max_open_trades:
        return DEMO_RISK_BLOCKED_OPEN_TRADES
    if value.current_pending_orders >= value.max_pending_orders:
        return DEMO_RISK_BLOCKED_PENDING_ORDERS
    if value.current_spread > value.max_spread:
        return DEMO_RISK_BLOCKED_SPREAD
    if not value.stop_loss_present:
        return DEMO_RISK_BLOCKED_MISSING_STOP_LOSS
    if not value.take_profit_present:
        return DEMO_RISK_BLOCKED_MISSING_TAKE_PROFIT
    if not value.duplicate_order_guard_clear:
        return DEMO_RISK_BLOCKED_DUPLICATE_ORDER
    if not value.kill_switch_clear:
        return DEMO_RISK_BLOCKED_KILL_SWITCH
    if not value.market_hours_clear or not value.instrument_verified:
        return DEMO_RISK_BLOCKED_MARKET_HOURS
    if not value.strategy_review_ready:
        return DEMO_RISK_BLOCKED_STRATEGY_NOT_READY
    return DEMO_RISK_REVIEW_READY


def _blockers(classification: str) -> list[str]:
    if classification == DEMO_RISK_REVIEW_READY:
        return []
    return [classification.lower()]


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_RISK_REVIEW_READY:
        return "Continue to position sizing; keep demo execution locked."
    return "Resolve the risk blocker before building an operator demo ticket."


def _replace_risk(value: DemoTradeRiskInput, **updates: Any) -> DemoTradeRiskInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoTradeRiskInput(**raw)


def _coerce_input(value: DemoTradeRiskInput | Mapping[str, Any]) -> DemoTradeRiskInput:
    if isinstance(value, DemoTradeRiskInput):
        return value
    raw = dict(value)
    for name in (
        "max_risk_per_trade",
        "proposed_risk_per_trade",
        "max_daily_loss",
        "current_daily_loss",
        "max_spread",
        "current_spread",
    ):
        raw[name] = _to_decimal(raw[name])
    return DemoTradeRiskInput(**raw)


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
