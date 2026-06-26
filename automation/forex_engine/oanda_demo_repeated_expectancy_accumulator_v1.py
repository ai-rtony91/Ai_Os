from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping

from automation.forex_engine.oanda_demo_expectancy_sample_intake_v1 import (
    EXACT_EXPECTANCY_WARNING_TEXT,
    OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED,
    PROTECTED_PERMISSION_DEFAULTS,
    build_sample_insufficient_expectancy_inputs,
    build_sample_losing_expectancy_inputs,
    build_sample_strong_expectancy_inputs,
    build_sample_unsafe_expectancy_inputs,
    build_sample_weak_mixed_expectancy_inputs,
    intake_oanda_demo_expectancy_sample,
    oanda_demo_expectancy_sample_intake_to_jsonable_dict,
)
from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    EXACT_OWNER_WARNING_TEXT,
    RESULT_BUCKET_BREAKEVEN,
    RESULT_BUCKET_LOSS,
    RESULT_BUCKET_PROFIT,
)


VERSION = "oanda_demo_repeated_expectancy_accumulator_v1"
OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_VERSION = VERSION

OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG"
)
OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_REVIEWABLE = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_REVIEWABLE"
)
OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK"
)
OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING"
)
OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED = (
    "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED"
)


@dataclass(frozen=True)
class OandaDemoRepeatedExpectancyAccumulatorConfig:
    min_review_sample_size: int = 5
    min_strong_sample_size: int = 10
    min_profit_factor_review: Decimal = Decimal("1.10")
    min_profit_factor_strong: Decimal = Decimal("1.50")
    min_average_r_review: Decimal = Decimal("0.05")
    min_average_r_strong: Decimal = Decimal("0.20")


@dataclass(frozen=True)
class OandaDemoRepeatedExpectancyAccumulatorInput:
    sample_intake_result: Mapping[str, Any]


@dataclass(frozen=True)
class OandaDemoRepeatedExpectancyAccumulatorResult:
    version: str
    classification: str
    intake_status: str
    result_count: int
    profit_count: int
    loss_count: int
    breakeven_count: int
    win_rate: Decimal
    loss_rate: Decimal
    breakeven_rate: Decimal
    total_realized_pl: Decimal
    average_realized_pl: Decimal
    gross_profit: Decimal
    gross_loss_abs: Decimal
    profit_factor: Decimal | None
    expectancy_per_trade: Decimal
    total_r: Decimal
    average_r: Decimal
    best_r: Decimal | None
    worst_r: Decimal | None
    average_win: Decimal
    average_loss_abs: Decimal
    max_observed_loss: Decimal
    positive_expectancy: bool
    profitable_sample: bool
    loss_dominated_sample: bool
    strategy_id: str
    candidate_id: str
    instrument: str
    sample_items: tuple[Mapping[str, Any], ...]
    blockers: tuple[str, ...]
    owner_warning: str
    expectancy_warning: str
    next_safe_action: str
    permissions: Mapping[str, bool]
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


def build_sample_strong_accumulator_input() -> OandaDemoRepeatedExpectancyAccumulatorInput:
    return _accumulator_input(build_sample_strong_expectancy_inputs())


def build_sample_weak_accumulator_input() -> OandaDemoRepeatedExpectancyAccumulatorInput:
    return _accumulator_input(build_sample_weak_mixed_expectancy_inputs())


def build_sample_insufficient_accumulator_input() -> OandaDemoRepeatedExpectancyAccumulatorInput:
    return _accumulator_input(build_sample_insufficient_expectancy_inputs())


def build_sample_losing_accumulator_input() -> OandaDemoRepeatedExpectancyAccumulatorInput:
    return _accumulator_input(build_sample_losing_expectancy_inputs())


def build_sample_unsafe_accumulator_input() -> OandaDemoRepeatedExpectancyAccumulatorInput:
    return _accumulator_input(build_sample_unsafe_expectancy_inputs())


def build_oanda_demo_repeated_expectancy_accumulator(
    accumulator_input: OandaDemoRepeatedExpectancyAccumulatorInput | Mapping[str, Any] | None = None,
    config: OandaDemoRepeatedExpectancyAccumulatorConfig | None = None,
) -> OandaDemoRepeatedExpectancyAccumulatorResult:
    active_input = _coerce_input(accumulator_input or build_sample_strong_accumulator_input())
    active_config = config or OandaDemoRepeatedExpectancyAccumulatorConfig()
    intake = dict(active_input.sample_intake_result)
    items = tuple(dict(item) for item in intake.get("sample_items", ()))
    blocked = intake.get("classification") != OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED
    metrics = _metrics(items)
    classification = (
        OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED
        if blocked
        else _classification(metrics, active_config)
    )
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoRepeatedExpectancyAccumulatorResult(
        version=VERSION,
        classification=classification,
        intake_status=str(intake.get("classification", "")),
        result_count=metrics["result_count"],
        profit_count=metrics["profit_count"],
        loss_count=metrics["loss_count"],
        breakeven_count=metrics["breakeven_count"],
        win_rate=metrics["win_rate"],
        loss_rate=metrics["loss_rate"],
        breakeven_rate=metrics["breakeven_rate"],
        total_realized_pl=metrics["total_realized_pl"],
        average_realized_pl=metrics["average_realized_pl"],
        gross_profit=metrics["gross_profit"],
        gross_loss_abs=metrics["gross_loss_abs"],
        profit_factor=metrics["profit_factor"],
        expectancy_per_trade=metrics["expectancy_per_trade"],
        total_r=metrics["total_r"],
        average_r=metrics["average_r"],
        best_r=metrics["best_r"],
        worst_r=metrics["worst_r"],
        average_win=metrics["average_win"],
        average_loss_abs=metrics["average_loss_abs"],
        max_observed_loss=metrics["max_observed_loss"],
        positive_expectancy=metrics["expectancy_per_trade"] > Decimal("0"),
        profitable_sample=metrics["total_realized_pl"] > Decimal("0"),
        loss_dominated_sample=metrics["loss_count"] > metrics["profit_count"],
        strategy_id=str(intake.get("strategy_id", "")),
        candidate_id=str(intake.get("candidate_id", "")),
        instrument=str(intake.get("instrument", "")),
        sample_items=items if not blocked else tuple(),
        blockers=tuple(intake.get("blockers", ())) if blocked else tuple(),
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        expectancy_warning=EXACT_EXPECTANCY_WARNING_TEXT,
        next_safe_action=_next_safe_action(classification),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict(
    result: OandaDemoRepeatedExpectancyAccumulatorResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "classification": result.classification,
        "intake_status": result.intake_status,
        "result_count": result.result_count,
        "profit_count": result.profit_count,
        "loss_count": result.loss_count,
        "breakeven_count": result.breakeven_count,
        "win_rate": _json_value(result.win_rate),
        "loss_rate": _json_value(result.loss_rate),
        "breakeven_rate": _json_value(result.breakeven_rate),
        "total_realized_pl": _json_value(result.total_realized_pl),
        "average_realized_pl": _json_value(result.average_realized_pl),
        "gross_profit": _json_value(result.gross_profit),
        "gross_loss_abs": _json_value(result.gross_loss_abs),
        "profit_factor": _json_value(result.profit_factor),
        "expectancy_per_trade": _json_value(result.expectancy_per_trade),
        "total_r": _json_value(result.total_r),
        "average_r": _json_value(result.average_r),
        "best_r": _json_value(result.best_r),
        "worst_r": _json_value(result.worst_r),
        "average_win": _json_value(result.average_win),
        "average_loss_abs": _json_value(result.average_loss_abs),
        "max_observed_loss": _json_value(result.max_observed_loss),
        "positive_expectancy": result.positive_expectancy,
        "profitable_sample": result.profitable_sample,
        "loss_dominated_sample": result.loss_dominated_sample,
        "strategy_id": result.strategy_id,
        "candidate_id": result.candidate_id,
        "instrument": result.instrument,
        "sample_items": _json_value(result.sample_items),
        "blockers": list(result.blockers),
        "owner_warning": result.owner_warning,
        "expectancy_warning": result.expectancy_warning,
        "next_safe_action": result.next_safe_action,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
        "mutates_existing_ledger_file": False,
        "preview_only": True,
    }


def oanda_demo_repeated_expectancy_accumulator_to_operator_text(
    result: OandaDemoRepeatedExpectancyAccumulatorResult,
) -> str:
    return "\n".join(
        (
            f"Repeated expectancy accumulator status: {result.classification}.",
            f"Results: {result.result_count}; win rate: {_json_value(result.win_rate)}.",
            f"Profit factor: {_json_value(result.profit_factor)}; average R: {_json_value(result.average_r)}.",
            "Repeated expectancy proof is not live execution authority.",
            "No trade placed by this packet.",
            "No broker call made by this packet.",
        )
    )


def oanda_demo_repeated_expectancy_accumulator_to_markdown(
    result: OandaDemoRepeatedExpectancyAccumulatorResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Repeated Expectancy Accumulator V1",
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Result count: `{result.result_count}`",
        f"- Win rate: `{_json_value(result.win_rate)}`",
        f"- Profit factor: `{_json_value(result.profit_factor)}`",
        f"- Expectancy per trade: `{_json_value(result.expectancy_per_trade)}`",
        f"- Average R: `{_json_value(result.average_r)}`",
        "",
        "## Safety",
        "- Repeated expectancy proof is not live execution authority.",
        "- No trade placed by this packet.",
        "- No broker call made by this packet.",
        "- All protected permission flags remain false.",
    ]
    return "\n".join(lines) + "\n"


def _accumulator_input(sample_input: Any) -> OandaDemoRepeatedExpectancyAccumulatorInput:
    intake = intake_oanda_demo_expectancy_sample(sample_input)
    return OandaDemoRepeatedExpectancyAccumulatorInput(
        sample_intake_result=oanda_demo_expectancy_sample_intake_to_jsonable_dict(intake)
    )


def _coerce_input(
    accumulator_input: OandaDemoRepeatedExpectancyAccumulatorInput | Mapping[str, Any],
) -> OandaDemoRepeatedExpectancyAccumulatorInput:
    if isinstance(accumulator_input, OandaDemoRepeatedExpectancyAccumulatorInput):
        return accumulator_input
    raw = dict(accumulator_input)
    return OandaDemoRepeatedExpectancyAccumulatorInput(
        sample_intake_result=raw.get("sample_intake_result", {})
    )


def _metrics(items: tuple[Mapping[str, Any], ...]) -> dict[str, Any]:
    result_count = len(items)
    profits = [_decimal(item.get("realized_pl")) for item in items if item.get("result_bucket") == RESULT_BUCKET_PROFIT]
    losses = [_decimal(item.get("realized_pl")) for item in items if item.get("result_bucket") == RESULT_BUCKET_LOSS]
    breakevens = [item for item in items if item.get("result_bucket") == RESULT_BUCKET_BREAKEVEN]
    realized_values = [_decimal(item.get("realized_pl")) for item in items]
    r_values = [_decimal(item.get("realized_r_multiple")) for item in items]
    gross_profit = sum(profits, Decimal("0"))
    gross_loss_abs = abs(sum(losses, Decimal("0")))
    total_realized_pl = sum(realized_values, Decimal("0"))
    total_r = sum(r_values, Decimal("0"))
    return {
        "result_count": result_count,
        "profit_count": len(profits),
        "loss_count": len(losses),
        "breakeven_count": len(breakevens),
        "win_rate": _rate(len(profits), result_count),
        "loss_rate": _rate(len(losses), result_count),
        "breakeven_rate": _rate(len(breakevens), result_count),
        "total_realized_pl": _q(total_realized_pl),
        "average_realized_pl": _average(total_realized_pl, result_count),
        "gross_profit": _q(gross_profit),
        "gross_loss_abs": _q(gross_loss_abs),
        "profit_factor": _profit_factor(gross_profit, gross_loss_abs),
        "expectancy_per_trade": _average(total_realized_pl, result_count),
        "total_r": _q(total_r),
        "average_r": _average(total_r, result_count),
        "best_r": max(r_values).quantize(Decimal("0.0001")) if r_values else None,
        "worst_r": min(r_values).quantize(Decimal("0.0001")) if r_values else None,
        "average_win": _average(gross_profit, len(profits)),
        "average_loss_abs": _average(gross_loss_abs, len(losses)),
        "max_observed_loss": _q(abs(min(losses))) if losses else Decimal("0.0000"),
    }


def _classification(
    metrics: Mapping[str, Any],
    config: OandaDemoRepeatedExpectancyAccumulatorConfig,
) -> str:
    result_count = int(metrics["result_count"])
    expectancy = _decimal(metrics["expectancy_per_trade"])
    average_r = _decimal(metrics["average_r"])
    profit_factor = metrics["profit_factor"]
    loss_count = int(metrics["loss_count"])
    if expectancy < Decimal("0") or (
        loss_count > 0 and profit_factor is not None and profit_factor < Decimal("1")
    ):
        return OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING
    if (
        expectancy > Decimal("0")
        and profit_factor is not None
        and profit_factor >= config.min_profit_factor_strong
        and result_count >= config.min_strong_sample_size
        and average_r >= config.min_average_r_strong
    ):
        return OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG
    if (
        expectancy > Decimal("0")
        and profit_factor is not None
        and profit_factor >= config.min_profit_factor_review
        and result_count >= config.min_review_sample_size
        and average_r >= config.min_average_r_review
    ):
        return OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_REVIEWABLE
    return OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK


def _next_safe_action(classification: str) -> str:
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG:
        return "Send the repeated expectancy metrics to sufficiency review."
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED:
        return "Repair the sample intake before expectancy metrics are reviewed."
    if classification == OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING:
        return "Route the losing sample to review and next profit candidate analysis."
    return "Collect or review more demo evidence before owner proof review."


def _rate(count: int, total: int) -> Decimal:
    if total <= 0:
        return Decimal("0.0000")
    return (Decimal(count) / Decimal(total)).quantize(Decimal("0.0001"))


def _average(total: Decimal, count: int) -> Decimal:
    if count <= 0:
        return Decimal("0.0000")
    return (total / Decimal(count)).quantize(Decimal("0.0001"))


def _profit_factor(gross_profit: Decimal, gross_loss_abs: Decimal) -> Decimal | None:
    if gross_loss_abs == Decimal("0"):
        return None
    return (gross_profit / gross_loss_abs).quantize(Decimal("0.0001"))


def _decimal(value: Any) -> Decimal:
    return Decimal(str(value))


def _q(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.0001"))


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_json_value(child) for child in value]
    if isinstance(value, list):
        return [_json_value(child) for child in value]
    return value
