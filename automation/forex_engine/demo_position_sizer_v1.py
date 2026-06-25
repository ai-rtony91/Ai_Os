from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from typing import Any, Mapping


DEMO_POSITION_SIZER_VERSION = "demo_position_sizer_v1"

DEMO_POSITION_SIZE_READY = "DEMO_POSITION_SIZE_READY"
DEMO_POSITION_SIZE_BLOCKED_INVALID_BALANCE = "DEMO_POSITION_SIZE_BLOCKED_INVALID_BALANCE"
DEMO_POSITION_SIZE_BLOCKED_INVALID_RISK = "DEMO_POSITION_SIZE_BLOCKED_INVALID_RISK"
DEMO_POSITION_SIZE_BLOCKED_INVALID_STOP_DISTANCE = "DEMO_POSITION_SIZE_BLOCKED_INVALID_STOP_DISTANCE"
DEMO_POSITION_SIZE_BLOCKED_BELOW_MIN_UNITS = "DEMO_POSITION_SIZE_BLOCKED_BELOW_MIN_UNITS"
DEMO_POSITION_SIZE_BLOCKED_ABOVE_MAX_UNITS = "DEMO_POSITION_SIZE_BLOCKED_ABOVE_MAX_UNITS"
DEMO_POSITION_SIZE_BLOCKED_BAD_REWARD_RISK = "DEMO_POSITION_SIZE_BLOCKED_BAD_REWARD_RISK"


@dataclass(frozen=True)
class DemoPositionSizerConfig:
    min_reward_to_risk: Decimal = Decimal("1.5")


@dataclass(frozen=True)
class DemoPositionSizerInput:
    balance: Decimal
    risk_percent: Decimal
    stop_distance_pips: Decimal
    pip_value_per_unit: Decimal
    min_units: int
    max_units: int
    instrument: str
    direction: str
    entry_price: Decimal
    stop_loss_price: Decimal
    take_profit_price: Decimal
    config: DemoPositionSizerConfig = DemoPositionSizerConfig()


@dataclass(frozen=True)
class DemoPositionSizerResult:
    engine_version: str
    sizing_status: str
    position_size_review_allowed: bool
    proposed_units: int
    risk_amount: Decimal
    estimated_loss_at_stop: Decimal
    estimated_reward_at_target: Decimal
    max_loss: Decimal
    expected_reward: Decimal
    reward_to_risk: Decimal
    blockers: tuple[str, ...]
    next_safe_action: str
    sizing_input: DemoPositionSizerInput
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool


def build_sample_position_size_input() -> DemoPositionSizerInput:
    return DemoPositionSizerInput(
        balance=Decimal("10000.00"),
        risk_percent=Decimal("0.01"),
        stop_distance_pips=Decimal("50"),
        pip_value_per_unit=Decimal("0.0001"),
        min_units=1000,
        max_units=50000,
        instrument="EUR_USD",
        direction="LONG",
        entry_price=Decimal("1.1000"),
        stop_loss_price=Decimal("1.0950"),
        take_profit_price=Decimal("1.1100"),
    )


def build_sample_blocked_position_size_input() -> DemoPositionSizerInput:
    sample = build_sample_position_size_input()
    return _replace_input(sample, risk_percent=Decimal("0"))


def calculate_demo_position_size(
    sizing_input: DemoPositionSizerInput | Mapping[str, Any] | None = None,
) -> DemoPositionSizerResult:
    active = _coerce_input(sizing_input or build_sample_position_size_input())
    risk_amount = max(active.balance * active.risk_percent, Decimal("0"))
    raw_units = Decimal("0")
    if active.stop_distance_pips > 0 and active.pip_value_per_unit > 0:
        raw_units = risk_amount / (active.stop_distance_pips * active.pip_value_per_unit)
    proposed_units = int(raw_units.to_integral_value(rounding=ROUND_FLOOR))
    estimated_loss = (Decimal(proposed_units) * active.stop_distance_pips * active.pip_value_per_unit).quantize(
        Decimal("0.01")
    )
    reward_to_risk = _reward_to_risk(active)
    estimated_reward = (estimated_loss * reward_to_risk).quantize(Decimal("0.01"))
    status = _classify(active, proposed_units, reward_to_risk)
    return DemoPositionSizerResult(
        engine_version=DEMO_POSITION_SIZER_VERSION,
        sizing_status=status,
        position_size_review_allowed=status == DEMO_POSITION_SIZE_READY,
        proposed_units=proposed_units if status != DEMO_POSITION_SIZE_BLOCKED_INVALID_STOP_DISTANCE else 0,
        risk_amount=risk_amount.quantize(Decimal("0.01")),
        estimated_loss_at_stop=estimated_loss,
        estimated_reward_at_target=estimated_reward,
        max_loss=estimated_loss,
        expected_reward=estimated_reward,
        reward_to_risk=reward_to_risk,
        blockers=tuple([] if status == DEMO_POSITION_SIZE_READY else [status.lower()]),
        next_safe_action=_next_safe_action(status),
        sizing_input=active,
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
    )


def demo_position_size_to_jsonable_dict(result: DemoPositionSizerResult) -> dict[str, Any]:
    return _json_value(result)


def demo_position_size_to_operator_text(result: DemoPositionSizerResult | None = None) -> str:
    active = result or calculate_demo_position_size()
    if active.position_size_review_allowed:
        return (
            f"Position size is review-ready at {active.proposed_units} units, "
            f"with max loss {active.max_loss} and expected reward {active.expected_reward}. No trade was placed."
        )
    return f"Position sizing is blocked: {'; '.join(active.blockers)}. No trade was placed."


def _classify(value: DemoPositionSizerInput, units: int, reward_to_risk: Decimal) -> str:
    if value.balance <= 0:
        return DEMO_POSITION_SIZE_BLOCKED_INVALID_BALANCE
    if value.risk_percent <= 0:
        return DEMO_POSITION_SIZE_BLOCKED_INVALID_RISK
    if value.stop_distance_pips <= 0 or value.pip_value_per_unit <= 0:
        return DEMO_POSITION_SIZE_BLOCKED_INVALID_STOP_DISTANCE
    if units < value.min_units:
        return DEMO_POSITION_SIZE_BLOCKED_BELOW_MIN_UNITS
    if units > value.max_units:
        return DEMO_POSITION_SIZE_BLOCKED_ABOVE_MAX_UNITS
    if reward_to_risk < value.config.min_reward_to_risk:
        return DEMO_POSITION_SIZE_BLOCKED_BAD_REWARD_RISK
    return DEMO_POSITION_SIZE_READY


def _reward_to_risk(value: DemoPositionSizerInput) -> Decimal:
    risk = abs(value.entry_price - value.stop_loss_price)
    reward = abs(value.take_profit_price - value.entry_price)
    if risk <= 0:
        return Decimal("0")
    return (reward / risk).quantize(Decimal("0.01"))


def _next_safe_action(status: str) -> str:
    if status == DEMO_POSITION_SIZE_READY:
        return "Continue to local order plan review; do not place an order."
    return "Fix position sizing before preparing the operator ticket."


def _replace_input(value: DemoPositionSizerInput, **updates: Any) -> DemoPositionSizerInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoPositionSizerInput(**raw)


def _coerce_input(value: DemoPositionSizerInput | Mapping[str, Any]) -> DemoPositionSizerInput:
    if isinstance(value, DemoPositionSizerInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoPositionSizerConfig())
    if not isinstance(config, DemoPositionSizerConfig):
        config = DemoPositionSizerConfig(**dict(config))
    raw["config"] = config
    for name in (
        "balance",
        "risk_percent",
        "stop_distance_pips",
        "pip_value_per_unit",
        "entry_price",
        "stop_loss_price",
        "take_profit_price",
    ):
        raw[name] = _to_decimal(raw[name])
    return DemoPositionSizerInput(**raw)


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
