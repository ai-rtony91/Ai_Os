"""Deterministic local Forex profit validation for AI_OS.

This module evaluates demo trade evidence only. It does not read credentials,
read .env files, call brokers, place orders, start automation, or enable live
trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Any, Mapping


getcontext().prec = 28

PROFIT_VALIDATION_PASS = "PROFIT_VALIDATION_PASS"
PROFIT_VALIDATION_CONTINUE_DEMO = "PROFIT_VALIDATION_CONTINUE_DEMO"
PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW = "PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW"
PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY = (
    "PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY"
)
PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE = (
    "PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE"
)
PROFIT_VALIDATION_BLOCKED_DRAWDOWN = "PROFIT_VALIDATION_BLOCKED_DRAWDOWN"
PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE = (
    "PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE"
)
PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED = (
    "PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED"
)

VALID_CLASSIFICATIONS = (
    PROFIT_VALIDATION_PASS,
    PROFIT_VALIDATION_CONTINUE_DEMO,
    PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW,
    PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY,
    PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE,
    PROFIT_VALIDATION_BLOCKED_DRAWDOWN,
    PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE,
    PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED,
)

SAMPLE_334_OPERATOR_ANSWER = (
    "Profit is not proven. Trade 334 closed by stop loss with negative "
    "realized P/L. AIOS must continue demo profit validation and loss review "
    "before Anthony funds real money or allows compounding."
)


@dataclass(frozen=True)
class ProfitValidationConfig:
    """Risk and profitability thresholds for the validation gate."""

    minimum_sample_size: int = 20
    minimum_profit_factor: Decimal | str | int | float = Decimal("1.25")
    maximum_drawdown_allowed: Decimal | str | int | float = Decimal("0.05")
    maximum_consecutive_losses_allowed: int = 3
    stop_loss_required: bool = True
    take_profit_required: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "minimum_sample_size", _to_non_negative_int(self.minimum_sample_size)
        )
        object.__setattr__(
            self, "minimum_profit_factor", _to_decimal(self.minimum_profit_factor)
        )
        object.__setattr__(
            self,
            "maximum_drawdown_allowed",
            _to_decimal(self.maximum_drawdown_allowed),
        )
        object.__setattr__(
            self,
            "maximum_consecutive_losses_allowed",
            _to_non_negative_int(self.maximum_consecutive_losses_allowed),
        )
        object.__setattr__(self, "stop_loss_required", _to_bool(self.stop_loss_required))
        object.__setattr__(
            self, "take_profit_required", _to_bool(self.take_profit_required)
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProfitValidationConfig":
        return cls(
            minimum_sample_size=raw.get("minimum_sample_size", cls.minimum_sample_size),
            minimum_profit_factor=raw.get(
                "minimum_profit_factor", cls.minimum_profit_factor
            ),
            maximum_drawdown_allowed=raw.get(
                "maximum_drawdown_allowed",
                raw.get("max_allowed_drawdown", cls.maximum_drawdown_allowed),
            ),
            maximum_consecutive_losses_allowed=raw.get(
                "maximum_consecutive_losses_allowed",
                raw.get(
                    "max_allowed_consecutive_losses",
                    cls.maximum_consecutive_losses_allowed,
                ),
            ),
            stop_loss_required=raw.get("stop_loss_required", cls.stop_loss_required),
            take_profit_required=raw.get("take_profit_required", cls.take_profit_required),
        )


@dataclass(frozen=True)
class TradeEvidence:
    """Closed-trade and aggregate demo evidence inspected by the gate."""

    trade_id: str | int | None = None
    close_reason: str = ""
    pl_capture_classification: str = ""
    profit_claimed: bool = False
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    realized_pl_total: Decimal | str | int | float = Decimal("0")
    average_win: Decimal | str | int | float = Decimal("0")
    average_loss: Decimal | str | int | float = Decimal("0")
    max_drawdown: Decimal | str | int | float = Decimal("0")
    consecutive_losses: int = 0
    open_trades: int = 0
    open_positions: int = 0
    pending_orders: int = 0
    stop_loss_present: bool = False
    take_profit_present: bool = False
    daily_loss_limit_clear: bool = False
    kill_switch_clear: bool = False
    owner_approval_required: bool = True
    owner_approved: bool = False
    live_trading_allowed: bool = False
    compounding_requested: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "trade_id", _string_or_none(self.trade_id))
        object.__setattr__(self, "close_reason", str(self.close_reason))
        object.__setattr__(
            self, "pl_capture_classification", str(self.pl_capture_classification)
        )
        object.__setattr__(self, "profit_claimed", _to_bool(self.profit_claimed))
        object.__setattr__(self, "total_trades", _to_non_negative_int(self.total_trades))
        object.__setattr__(self, "wins", _to_non_negative_int(self.wins))
        object.__setattr__(self, "losses", _to_non_negative_int(self.losses))
        object.__setattr__(
            self, "realized_pl_total", _to_decimal(self.realized_pl_total)
        )
        object.__setattr__(self, "average_win", abs(_to_decimal(self.average_win)))
        object.__setattr__(self, "average_loss", abs(_to_decimal(self.average_loss)))
        object.__setattr__(self, "max_drawdown", abs(_to_decimal(self.max_drawdown)))
        object.__setattr__(
            self, "consecutive_losses", _to_non_negative_int(self.consecutive_losses)
        )
        object.__setattr__(self, "open_trades", _to_non_negative_int(self.open_trades))
        object.__setattr__(
            self, "open_positions", _to_non_negative_int(self.open_positions)
        )
        object.__setattr__(
            self, "pending_orders", _to_non_negative_int(self.pending_orders)
        )
        object.__setattr__(
            self, "stop_loss_present", _to_bool(self.stop_loss_present)
        )
        object.__setattr__(
            self, "take_profit_present", _to_bool(self.take_profit_present)
        )
        object.__setattr__(
            self, "daily_loss_limit_clear", _to_bool(self.daily_loss_limit_clear)
        )
        object.__setattr__(
            self, "kill_switch_clear", _to_bool(self.kill_switch_clear)
        )
        object.__setattr__(
            self, "owner_approval_required", _to_bool(self.owner_approval_required)
        )
        object.__setattr__(self, "owner_approved", _to_bool(self.owner_approved))
        object.__setattr__(
            self, "live_trading_allowed", _to_bool(self.live_trading_allowed)
        )
        object.__setattr__(
            self, "compounding_requested", _to_bool(self.compounding_requested)
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TradeEvidence":
        return cls(
            trade_id=raw.get("trade_id"),
            close_reason=raw.get("close_reason", ""),
            pl_capture_classification=raw.get("pl_capture_classification", ""),
            profit_claimed=raw.get("profit_claimed", False),
            total_trades=raw.get("total_trades", raw.get("trade_count", 0)),
            wins=raw.get("wins", 0),
            losses=raw.get("losses", 0),
            realized_pl_total=raw.get("realized_pl_total", "0"),
            average_win=raw.get("average_win", raw.get("avg_win", "0")),
            average_loss=raw.get("average_loss", raw.get("avg_loss", "0")),
            max_drawdown=raw.get("max_drawdown", "0"),
            consecutive_losses=raw.get("consecutive_losses", 0),
            open_trades=raw.get("open_trades", raw.get("openTradeCount", 0)),
            open_positions=raw.get("open_positions", raw.get("openPositionCount", 0)),
            pending_orders=raw.get("pending_orders", raw.get("pendingOrderCount", 0)),
            stop_loss_present=raw.get("stop_loss_present", False),
            take_profit_present=raw.get("take_profit_present", False),
            daily_loss_limit_clear=raw.get("daily_loss_limit_clear", False),
            kill_switch_clear=raw.get("kill_switch_clear", False),
            owner_approval_required=raw.get("owner_approval_required", True),
            owner_approved=raw.get("owner_approved", False),
            live_trading_allowed=raw.get("live_trading_allowed", False),
            compounding_requested=raw.get("compounding_requested", False),
        )


@dataclass(frozen=True)
class ProfitValidationInput:
    """Full input envelope for a deterministic validation run."""

    evidence: TradeEvidence = field(default_factory=TradeEvidence)
    config: ProfitValidationConfig = field(default_factory=ProfitValidationConfig)


@dataclass(frozen=True)
class ProfitValidationResult:
    """Operator-facing result of the profit validation gate."""

    classification: str
    profitability_proven: bool
    real_money_allowed: bool
    next_trade_allowed: bool
    compounding_allowed: bool
    operator_answer: str
    blockers: tuple[str, ...]
    metrics: Mapping[str, Any]
    permissions: Mapping[str, bool]
    next_safe_action: str

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification}")


def build_sample_trade_334_input() -> ProfitValidationInput:
    """Return the built-in evidence for trade 334."""

    return ProfitValidationInput(
        config=ProfitValidationConfig(
            minimum_sample_size=20,
            minimum_profit_factor=Decimal("1.25"),
            maximum_drawdown_allowed=Decimal("0.05"),
            maximum_consecutive_losses_allowed=3,
            stop_loss_required=True,
            take_profit_required=True,
        ),
        evidence=TradeEvidence(
            trade_id=334,
            close_reason="STOP_LOSS_ORDER",
            realized_pl_total=Decimal("-0.0010"),
            pl_capture_classification="FILLED_TRADE_PL_NEGATIVE",
            profit_claimed=False,
            total_trades=1,
            wins=0,
            losses=1,
            average_win=Decimal("0"),
            average_loss=Decimal("0.0010"),
            max_drawdown=Decimal("0.0010"),
            consecutive_losses=1,
            open_trades=0,
            open_positions=0,
            pending_orders=0,
            stop_loss_present=True,
            take_profit_present=True,
            kill_switch_clear=True,
            daily_loss_limit_clear=True,
            owner_approval_required=True,
            owner_approved=False,
            live_trading_allowed=False,
            compounding_requested=False,
        ),
    )


def evaluate_profit_validation_loop(
    validation_input: ProfitValidationInput | TradeEvidence | Mapping[str, Any] | None = None,
    config: ProfitValidationConfig | Mapping[str, Any] | None = None,
) -> ProfitValidationResult:
    """Evaluate demo evidence and return one governed classification."""

    run_input = _coerce_input(validation_input, config)
    evidence = run_input.evidence
    active_config = run_input.config

    average_win = evidence.average_win
    average_loss = evidence.average_loss
    expectancy = _calculate_expectancy(evidence)
    profit_factor = _calculate_profit_factor(evidence)
    no_open_exposure = evidence.open_trades == 0 and evidence.open_positions == 0
    no_pending_exposure = evidence.pending_orders == 0
    stop_loss_satisfied = (
        evidence.stop_loss_present or not active_config.stop_loss_required
    )
    take_profit_satisfied = (
        evidence.take_profit_present or not active_config.take_profit_required
    )

    metrics = {
        "trade_id": evidence.trade_id,
        "close_reason": evidence.close_reason,
        "pl_capture_classification": evidence.pl_capture_classification,
        "profit_claimed": evidence.profit_claimed,
        "total_trades": evidence.total_trades,
        "wins": evidence.wins,
        "losses": evidence.losses,
        "realized_pl_total": evidence.realized_pl_total,
        "average_win": average_win,
        "average_loss": average_loss,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown": evidence.max_drawdown,
        "max_allowed_drawdown": active_config.maximum_drawdown_allowed,
        "consecutive_losses": evidence.consecutive_losses,
        "max_allowed_consecutive_losses": (
            active_config.maximum_consecutive_losses_allowed
        ),
        "open_trades": evidence.open_trades,
        "open_positions": evidence.open_positions,
        "pending_orders": evidence.pending_orders,
        "stop_loss_present": evidence.stop_loss_present,
        "take_profit_present": evidence.take_profit_present,
        "daily_loss_limit_clear": evidence.daily_loss_limit_clear,
        "kill_switch_clear": evidence.kill_switch_clear,
        "owner_approval_required": evidence.owner_approval_required,
        "owner_approved": evidence.owner_approved,
        "live_trading_allowed": evidence.live_trading_allowed,
        "compounding_requested": evidence.compounding_requested,
        "minimum_sample_size": active_config.minimum_sample_size,
        "minimum_profit_factor": active_config.minimum_profit_factor,
    }

    risk_blockers = _risk_blockers(
        evidence=evidence,
        config=active_config,
        no_open_exposure=no_open_exposure,
        no_pending_exposure=no_pending_exposure,
        stop_loss_satisfied=stop_loss_satisfied,
        take_profit_satisfied=take_profit_satisfied,
    )

    realized_loss_blocked = evidence.realized_pl_total < Decimal("0")
    sample_size_passed = evidence.total_trades >= active_config.minimum_sample_size
    expectancy_passed = expectancy > Decimal("0")
    profit_factor_passed = profit_factor >= active_config.minimum_profit_factor
    drawdown_passed = evidence.max_drawdown <= active_config.maximum_drawdown_allowed
    consecutive_loss_passed = (
        evidence.consecutive_losses
        <= active_config.maximum_consecutive_losses_allowed
    )

    profitability_proven = (
        evidence.realized_pl_total > Decimal("0")
        and sample_size_passed
        and expectancy_passed
        and profit_factor_passed
        and drawdown_passed
        and consecutive_loss_passed
        and not risk_blockers
    )
    compounding_allowed = (
        expectancy_passed
        and profit_factor_passed
        and sample_size_passed
        and drawdown_passed
        and consecutive_loss_passed
        and no_open_exposure
        and no_pending_exposure
        and evidence.kill_switch_clear
        and evidence.daily_loss_limit_clear
        and stop_loss_satisfied
        and take_profit_satisfied
        and profitability_proven
    )
    real_money_allowed = (
        profitability_proven
        and compounding_allowed
        and evidence.live_trading_allowed
        and evidence.owner_approved
        and not risk_blockers
    )

    classification, blockers = _classify(
        evidence=evidence,
        config=active_config,
        expectancy=expectancy,
        profit_factor=profit_factor,
        risk_blockers=risk_blockers,
        realized_loss_blocked=realized_loss_blocked,
        sample_size_passed=sample_size_passed,
        expectancy_passed=expectancy_passed,
        profit_factor_passed=profit_factor_passed,
        drawdown_passed=drawdown_passed,
        consecutive_loss_passed=consecutive_loss_passed,
        profitability_proven=profitability_proven,
        compounding_allowed=compounding_allowed,
    )
    next_trade_allowed = _next_trade_allowed(classification)
    operator_answer = _operator_answer(
        classification=classification,
        evidence=evidence,
        blockers=blockers,
        profitability_proven=profitability_proven,
    )
    permissions = {
        "profitability_proven": profitability_proven,
        "real_money_allowed": real_money_allowed,
        "next_trade_allowed": next_trade_allowed,
        "compounding_allowed": compounding_allowed,
        "owner_approval_required": evidence.owner_approval_required,
        "owner_approved": evidence.owner_approved,
        "live_trading_allowed": evidence.live_trading_allowed,
    }

    return ProfitValidationResult(
        classification=classification,
        profitability_proven=profitability_proven,
        real_money_allowed=real_money_allowed,
        next_trade_allowed=next_trade_allowed,
        compounding_allowed=compounding_allowed,
        operator_answer=operator_answer,
        blockers=tuple(blockers),
        metrics=metrics,
        permissions=permissions,
        next_safe_action=_next_safe_action(classification),
    )


def result_to_operator_text(result: ProfitValidationResult) -> str:
    """Format a deterministic operator-readable summary."""

    lines = [
        "AIOS Forex Profit Validation Loop V1",
        f"classification: {result.classification}",
        f"profitability_proven: {_bool_text(result.profitability_proven)}",
        f"real_money_allowed: {_bool_text(result.real_money_allowed)}",
        f"next_trade_allowed: {_bool_text(result.next_trade_allowed)}",
        f"compounding_allowed: {_bool_text(result.compounding_allowed)}",
        f"operator_answer: {result.operator_answer}",
        "blockers:",
    ]
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")
    lines.extend(
        [
            "metrics:",
            f"- trade_id: {result.metrics.get('trade_id')}",
            f"- realized_pl_total: {_json_value(result.metrics.get('realized_pl_total'))}",
            f"- expectancy: {_json_value(result.metrics.get('expectancy'))}",
            f"- profit_factor: {_json_value(result.metrics.get('profit_factor'))}",
            f"- max_drawdown: {_json_value(result.metrics.get('max_drawdown'))}",
            f"next_safe_action: {result.next_safe_action}",
        ]
    )
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: ProfitValidationResult) -> dict[str, Any]:
    """Convert a result into deterministic JSON-safe data."""

    return {
        "classification": result.classification,
        "blockers": list(result.blockers),
        "metrics": _jsonable_mapping(result.metrics),
        "operator_answer": result.operator_answer,
        "permissions": dict(result.permissions),
        "profitability_proven": result.profitability_proven,
        "real_money_allowed": result.real_money_allowed,
        "next_trade_allowed": result.next_trade_allowed,
        "compounding_allowed": result.compounding_allowed,
        "next_safe_action": result.next_safe_action,
        "safety": {
            "local_only": True,
            "broker_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "network_calls": False,
            "order_placement": False,
            "live_trading_enablement": False,
            "repo_mutation": False,
        },
    }


def _coerce_input(
    validation_input: ProfitValidationInput | TradeEvidence | Mapping[str, Any] | None,
    config: ProfitValidationConfig | Mapping[str, Any] | None,
) -> ProfitValidationInput:
    if isinstance(config, ProfitValidationConfig):
        active_config = config
    elif isinstance(config, Mapping):
        active_config = ProfitValidationConfig.from_mapping(config)
    elif isinstance(validation_input, Mapping):
        active_config = ProfitValidationConfig.from_mapping(validation_input)
    elif isinstance(validation_input, ProfitValidationInput):
        active_config = validation_input.config
    else:
        active_config = ProfitValidationConfig()

    if isinstance(validation_input, ProfitValidationInput):
        if config is None:
            return validation_input
        return ProfitValidationInput(evidence=validation_input.evidence, config=active_config)
    if isinstance(validation_input, TradeEvidence):
        return ProfitValidationInput(evidence=validation_input, config=active_config)
    if isinstance(validation_input, Mapping):
        return ProfitValidationInput(
            evidence=TradeEvidence.from_mapping(validation_input),
            config=active_config,
        )
    return ProfitValidationInput(evidence=TradeEvidence(), config=active_config)


def _classify(
    *,
    evidence: TradeEvidence,
    config: ProfitValidationConfig,
    expectancy: Decimal,
    profit_factor: Decimal,
    risk_blockers: list[str],
    realized_loss_blocked: bool,
    sample_size_passed: bool,
    expectancy_passed: bool,
    profit_factor_passed: bool,
    drawdown_passed: bool,
    consecutive_loss_passed: bool,
    profitability_proven: bool,
    compounding_allowed: bool,
) -> tuple[str, list[str]]:
    if realized_loss_blocked:
        return (
            PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW,
            [
                "negative realized P/L requires loss review",
                "profit validation must continue in demo",
            ],
        )
    if risk_blockers:
        return PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE, risk_blockers
    if not sample_size_passed:
        return (
            PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE,
            [
                (
                    "total trades "
                    f"{evidence.total_trades} below minimum sample size "
                    f"{config.minimum_sample_size}"
                )
            ],
        )
    if not expectancy_passed:
        return (
            PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY,
            [f"expectancy {expectancy} is not positive"],
        )
    if not drawdown_passed:
        return (
            PROFIT_VALIDATION_BLOCKED_DRAWDOWN,
            [
                (
                    f"max drawdown {evidence.max_drawdown} exceeds maximum "
                    f"{config.maximum_drawdown_allowed}"
                )
            ],
        )
    if not consecutive_loss_passed:
        return (
            PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE,
            [
                (
                    "consecutive losses "
                    f"{evidence.consecutive_losses} exceed maximum "
                    f"{config.maximum_consecutive_losses_allowed}"
                )
            ],
        )
    if not profit_factor_passed:
        return (
            PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED,
            [
                (
                    f"profit factor {profit_factor} below minimum "
                    f"{config.minimum_profit_factor}"
                )
            ],
        )
    if profitability_proven and compounding_allowed:
        return PROFIT_VALIDATION_PASS, []
    return (
        PROFIT_VALIDATION_CONTINUE_DEMO,
        ["continue demo validation until all profit and compounding gates pass"],
    )


def _risk_blockers(
    *,
    evidence: TradeEvidence,
    config: ProfitValidationConfig,
    no_open_exposure: bool,
    no_pending_exposure: bool,
    stop_loss_satisfied: bool,
    take_profit_satisfied: bool,
) -> list[str]:
    blockers: list[str] = []
    if evidence.wins + evidence.losses > evidence.total_trades:
        blockers.append("wins plus losses exceed total trades")
    if not no_open_exposure:
        blockers.append("open trade or position exposure remains")
    if not no_pending_exposure:
        blockers.append("pending order exposure remains")
    if not stop_loss_satisfied:
        blockers.append("stop loss protection is missing")
    if not take_profit_satisfied:
        blockers.append("take profit protection is missing")
    if not evidence.daily_loss_limit_clear:
        blockers.append("daily loss limit is not clear")
    if not evidence.kill_switch_clear:
        blockers.append("kill switch is not clear")
    if (
        evidence.consecutive_losses
        > config.maximum_consecutive_losses_allowed
    ):
        blockers.append(
            "consecutive losses exceed the configured maximum"
        )
    return blockers


def _operator_answer(
    *,
    classification: str,
    evidence: TradeEvidence,
    blockers: list[str],
    profitability_proven: bool,
) -> str:
    if _is_trade_334(evidence):
        return SAMPLE_334_OPERATOR_ANSWER
    if classification == PROFIT_VALIDATION_PASS and profitability_proven:
        return (
            "Demo profit validation passed local thresholds. Real money still "
            "requires separate governed live permission and recorded Anthony "
            "approval before any funding, broker action, or compounding."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW:
        return (
            "Profit is not proven. A closed trade has negative realized P/L, "
            "so AIOS must continue demo profit validation and loss review before "
            "Anthony funds real money or allows compounding."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE:
        return (
            "Profit is not proven. AIOS needs a larger governed demo sample "
            "before Anthony funds real money or allows compounding."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY:
        return (
            "Profit is not proven. Expectancy is not positive, so Anthony must "
            "not fund real money or allow compounding."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_DRAWDOWN:
        return (
            "Profit is not proven. Drawdown is above the configured limit, so "
            "Anthony must not fund real money or allow compounding."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED:
        return (
            "Profit is not proven enough for compounding. AIOS must keep "
            "compounding disabled until profit factor and all compounding gates pass."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE:
        detail = blockers[0] if blockers else "risk controls failed"
        return (
            f"Profit is not proven. AIOS risk-control evidence is blocked by {detail}. "
            "Anthony must not fund real money, allow compounding, or enable live trading."
        )
    return (
        "Profit is not proven. AIOS must continue demo validation before Anthony "
        "funds real money or allows compounding."
    )


def _next_trade_allowed(classification: str) -> bool:
    return classification in {
        PROFIT_VALIDATION_PASS,
        PROFIT_VALIDATION_CONTINUE_DEMO,
        PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE,
        PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED,
    }


def _next_safe_action(classification: str) -> str:
    if classification == PROFIT_VALIDATION_PASS:
        return (
            "Prepare an owner review packet; do not fund, trade live, or compound "
            "without separate Anthony approval."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW:
        return (
            "Complete loss review and continue demo validation before funding, "
            "live trading, or compounding."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE:
        return (
            "Continue collecting governed demo evidence until the minimum sample "
            "size is met."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY:
        return (
            "Keep real money and compounding blocked until expectancy becomes "
            "positive under risk controls."
        )
    if classification == PROFIT_VALIDATION_BLOCKED_DRAWDOWN:
        return "Reduce drawdown before any funding or compounding review."
    if classification == PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED:
        return "Keep compounding disabled and continue demo validation."
    if classification == PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE:
        return "Stop and repair risk-control evidence before any next trade."
    return "Continue demo validation under existing risk controls."


def _calculate_expectancy(evidence: TradeEvidence) -> Decimal:
    if evidence.total_trades == 0:
        return Decimal("0")
    total = Decimal(evidence.total_trades)
    win_probability = Decimal(evidence.wins) / total
    loss_probability = Decimal(evidence.losses) / total
    return (win_probability * evidence.average_win) - (
        loss_probability * evidence.average_loss
    )


def _calculate_profit_factor(evidence: TradeEvidence) -> Decimal:
    gross_wins = Decimal(evidence.wins) * evidence.average_win
    gross_losses = Decimal(evidence.losses) * evidence.average_loss
    if gross_losses == Decimal("0"):
        if gross_wins > Decimal("0"):
            return Decimal("Infinity")
        return Decimal("0")
    return gross_wins / gross_losses


def _is_trade_334(evidence: TradeEvidence) -> bool:
    return (
        evidence.trade_id == "334"
        and evidence.close_reason.upper() == "STOP_LOSS_ORDER"
        and evidence.pl_capture_classification.upper() == "FILLED_TRADE_PL_NEGATIVE"
    )


def _to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise ValueError("boolean is not valid decimal evidence")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal evidence: {value!r}") from exc


def _to_non_negative_int(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("boolean is not valid integer evidence")
    parsed = int(value)
    if parsed < 0:
        raise ValueError(f"expected non-negative integer evidence, got {value!r}")
    return parsed


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "clear", "approved"}:
            return True
        if lowered in {"false", "0", "no", "n", "blocked", "failed"}:
            return False
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    raise ValueError(f"invalid boolean evidence: {value!r}")


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _jsonable_mapping(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {key: _json_value(value) for key, value in raw.items()}


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value.is_infinite():
            return "Infinity"
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return _jsonable_mapping(value)
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
