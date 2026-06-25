"""Local-only Forex loss review to next profit candidate gate.

This gate turns trade 334 loss evidence and candidate evidence into a governed
next-candidate decision. It never calls brokers, reads credentials, reads .env
files, places orders, mutates repo state, or enables live trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Any, Mapping


getcontext().prec = 28

NEXT_PROFIT_CANDIDATE_REVIEW_READY = "NEXT_PROFIT_CANDIDATE_REVIEW_READY"
NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW = (
    "NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW"
)
NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN = (
    "NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN"
)
NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE = (
    "NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE"
)
NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS = (
    "NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS"
)
NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE = (
    "NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE"
)
NEXT_PROFIT_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED = (
    "NEXT_PROFIT_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED"
)

VALID_CLASSIFICATIONS = {
    NEXT_PROFIT_CANDIDATE_REVIEW_READY,
    NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW,
    NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN,
    NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE,
    NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS,
    NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE,
    NEXT_PROFIT_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED,
}

SAMPLE_OPERATOR_ANSWER = (
    "Trade 334 loss review is required before the next profit candidate can be "
    "approved. AIOS has demo execution proof, but profit is not proven. No "
    "next trade, real money, or compounding is allowed until candidate evidence "
    "clears sample depth, expectancy, profit factor, drawdown, walk-forward, "
    "and risk gates."
)


@dataclass(frozen=True)
class LossReviewConfig:
    """Thresholds for approving a next profit candidate for review."""

    minimum_sample_size: int = 20
    minimum_profit_factor: Decimal | str | int | float = Decimal("1.25")
    maximum_drawdown_allowed: Decimal | str | int | float = Decimal("0.05")
    maximum_consecutive_losses_allowed: int = 3

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

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "LossReviewConfig":
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
        )


@dataclass(frozen=True)
class Trade334LossEvidence:
    """Evidence describing why trade 334 blocks the next candidate."""

    trade_id: str | int = 334
    close_reason: str = "STOP_LOSS_ORDER"
    realized_pl_total: Decimal | str | int | float = Decimal("-0.0010")
    pl_capture_classification: str = "FILLED_TRADE_PL_NEGATIVE"
    profit_claimed: bool = False
    stop_loss_used: bool = True
    take_profit_order_cancelled_after_stop: bool = True
    open_trade_count: int = 0
    open_position_count: int = 0
    pending_order_count: int = 0
    loss_acknowledged: bool = True
    loss_review_completed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "trade_id", str(self.trade_id))
        object.__setattr__(self, "close_reason", str(self.close_reason))
        object.__setattr__(
            self, "realized_pl_total", _to_decimal(self.realized_pl_total)
        )
        object.__setattr__(
            self, "pl_capture_classification", str(self.pl_capture_classification)
        )
        object.__setattr__(self, "profit_claimed", _to_bool(self.profit_claimed))
        object.__setattr__(self, "stop_loss_used", _to_bool(self.stop_loss_used))
        object.__setattr__(
            self,
            "take_profit_order_cancelled_after_stop",
            _to_bool(self.take_profit_order_cancelled_after_stop),
        )
        object.__setattr__(
            self, "open_trade_count", _to_non_negative_int(self.open_trade_count)
        )
        object.__setattr__(
            self,
            "open_position_count",
            _to_non_negative_int(self.open_position_count),
        )
        object.__setattr__(
            self, "pending_order_count", _to_non_negative_int(self.pending_order_count)
        )
        object.__setattr__(
            self, "loss_acknowledged", _to_bool(self.loss_acknowledged)
        )
        object.__setattr__(
            self, "loss_review_completed", _to_bool(self.loss_review_completed)
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Trade334LossEvidence":
        return cls(
            trade_id=raw.get("trade_id", 334),
            close_reason=raw.get("close_reason", "STOP_LOSS_ORDER"),
            realized_pl_total=raw.get("realized_pl_total", "-0.0010"),
            pl_capture_classification=raw.get(
                "pl_capture_classification", "FILLED_TRADE_PL_NEGATIVE"
            ),
            profit_claimed=raw.get("profit_claimed", False),
            stop_loss_used=raw.get("stop_loss_used", True),
            take_profit_order_cancelled_after_stop=raw.get(
                "take_profit_order_cancelled_after_stop", True
            ),
            open_trade_count=raw.get("open_trade_count", raw.get("openTradeCount", 0)),
            open_position_count=raw.get(
                "open_position_count", raw.get("openPositionCount", 0)
            ),
            pending_order_count=raw.get(
                "pending_order_count", raw.get("pendingOrderCount", 0)
            ),
            loss_acknowledged=raw.get("loss_acknowledged", True),
            loss_review_completed=raw.get("loss_review_completed", False),
        )


@dataclass(frozen=True)
class NextProfitCandidateEvidence:
    """Candidate evidence reviewed after the trade 334 loss gate."""

    candidate_id: str = "NONE"
    strategy_name: str = "UNKNOWN"
    symbol: str = "EUR_USD"
    direction: str = "UNKNOWN"
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    expectancy: Decimal | str | int | float = Decimal("0")
    profit_factor: Decimal | str | int | float = Decimal("0")
    max_drawdown: Decimal | str | int | float = Decimal("0")
    consecutive_losses: int = 0
    walk_forward_gate_cleared: bool = False
    sample_depth_sufficient: bool = False
    risk_controls_present: bool = False
    stop_loss_required: bool = True
    take_profit_required: bool = True
    kill_switch_clear: bool = False
    daily_loss_limit_clear: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_id", str(self.candidate_id))
        object.__setattr__(self, "strategy_name", str(self.strategy_name))
        object.__setattr__(self, "symbol", str(self.symbol))
        object.__setattr__(self, "direction", str(self.direction))
        object.__setattr__(self, "total_trades", _to_non_negative_int(self.total_trades))
        object.__setattr__(self, "wins", _to_non_negative_int(self.wins))
        object.__setattr__(self, "losses", _to_non_negative_int(self.losses))
        object.__setattr__(self, "expectancy", _to_decimal(self.expectancy))
        object.__setattr__(self, "profit_factor", _to_decimal(self.profit_factor))
        object.__setattr__(self, "max_drawdown", abs(_to_decimal(self.max_drawdown)))
        object.__setattr__(
            self, "consecutive_losses", _to_non_negative_int(self.consecutive_losses)
        )
        object.__setattr__(
            self,
            "walk_forward_gate_cleared",
            _to_bool(self.walk_forward_gate_cleared),
        )
        object.__setattr__(
            self, "sample_depth_sufficient", _to_bool(self.sample_depth_sufficient)
        )
        object.__setattr__(
            self, "risk_controls_present", _to_bool(self.risk_controls_present)
        )
        object.__setattr__(
            self, "stop_loss_required", _to_bool(self.stop_loss_required)
        )
        object.__setattr__(
            self, "take_profit_required", _to_bool(self.take_profit_required)
        )
        object.__setattr__(
            self, "kill_switch_clear", _to_bool(self.kill_switch_clear)
        )
        object.__setattr__(
            self, "daily_loss_limit_clear", _to_bool(self.daily_loss_limit_clear)
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "NextProfitCandidateEvidence":
        return cls(
            candidate_id=raw.get("candidate_id", "NONE"),
            strategy_name=raw.get("strategy_name", "UNKNOWN"),
            symbol=raw.get("symbol", "EUR_USD"),
            direction=raw.get("direction", "UNKNOWN"),
            total_trades=raw.get("total_trades", 0),
            wins=raw.get("wins", 0),
            losses=raw.get("losses", 0),
            expectancy=raw.get("expectancy", "0"),
            profit_factor=raw.get("profit_factor", "0"),
            max_drawdown=raw.get("max_drawdown", "0"),
            consecutive_losses=raw.get("consecutive_losses", 0),
            walk_forward_gate_cleared=raw.get("walk_forward_gate_cleared", False),
            sample_depth_sufficient=raw.get("sample_depth_sufficient", False),
            risk_controls_present=raw.get("risk_controls_present", False),
            stop_loss_required=raw.get("stop_loss_required", True),
            take_profit_required=raw.get("take_profit_required", True),
            kill_switch_clear=raw.get("kill_switch_clear", False),
            daily_loss_limit_clear=raw.get("daily_loss_limit_clear", False),
        )


@dataclass(frozen=True)
class LossToNextProfitCandidateInput:
    """Input envelope for the next profit candidate gate."""

    trade_334_loss: Trade334LossEvidence = field(default_factory=Trade334LossEvidence)
    candidate: NextProfitCandidateEvidence = field(
        default_factory=NextProfitCandidateEvidence
    )
    config: LossReviewConfig = field(default_factory=LossReviewConfig)
    next_demo_trade_allowed: bool = False
    real_money_allowed: bool = False
    compounding_allowed: bool = False
    owner_approval_required: bool = True
    broker_action_allowed: bool = False
    live_trading_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "next_demo_trade_allowed", _to_bool(self.next_demo_trade_allowed)
        )
        object.__setattr__(
            self, "real_money_allowed", _to_bool(self.real_money_allowed)
        )
        object.__setattr__(
            self, "compounding_allowed", _to_bool(self.compounding_allowed)
        )
        object.__setattr__(
            self, "owner_approval_required", _to_bool(self.owner_approval_required)
        )
        object.__setattr__(
            self, "broker_action_allowed", _to_bool(self.broker_action_allowed)
        )
        object.__setattr__(
            self, "live_trading_allowed", _to_bool(self.live_trading_allowed)
        )


@dataclass(frozen=True)
class LossToNextProfitCandidateResult:
    """Decision and permissions returned by the gate."""

    classification: str
    next_demo_trade_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    broker_action_allowed: bool
    live_trading_allowed: bool
    owner_approval_required: bool
    operator_answer: str
    blockers: tuple[str, ...]
    trade_334_metrics: Mapping[str, Any]
    candidate_metrics: Mapping[str, Any]
    permissions: Mapping[str, bool]
    next_safe_action: str

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification}")


def build_sample_trade_334_input() -> LossToNextProfitCandidateInput:
    """Return the intentionally blocked trade 334 sample."""

    return LossToNextProfitCandidateInput(
        trade_334_loss=Trade334LossEvidence(
            trade_id=334,
            close_reason="STOP_LOSS_ORDER",
            realized_pl_total=Decimal("-0.0010"),
            pl_capture_classification="FILLED_TRADE_PL_NEGATIVE",
            profit_claimed=False,
            stop_loss_used=True,
            take_profit_order_cancelled_after_stop=True,
            open_trade_count=0,
            open_position_count=0,
            pending_order_count=0,
            loss_acknowledged=True,
            loss_review_completed=False,
        ),
        candidate=NextProfitCandidateEvidence(
            candidate_id="NONE",
            strategy_name="UNKNOWN",
            symbol="EUR_USD",
            direction="UNKNOWN",
            total_trades=1,
            wins=0,
            losses=1,
            expectancy=Decimal("-0.0010"),
            profit_factor=Decimal("0"),
            max_drawdown=Decimal("0.0010"),
            consecutive_losses=1,
            walk_forward_gate_cleared=False,
            sample_depth_sufficient=False,
            risk_controls_present=True,
            stop_loss_required=True,
            take_profit_required=True,
            kill_switch_clear=True,
            daily_loss_limit_clear=True,
        ),
        config=LossReviewConfig(
            minimum_sample_size=20,
            minimum_profit_factor=Decimal("1.25"),
            maximum_drawdown_allowed=Decimal("0.05"),
            maximum_consecutive_losses_allowed=3,
        ),
        next_demo_trade_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        owner_approval_required=True,
        broker_action_allowed=False,
        live_trading_allowed=False,
    )


def evaluate_loss_to_next_profit_candidate_gate(
    gate_input: LossToNextProfitCandidateInput | Mapping[str, Any] | None = None,
) -> LossToNextProfitCandidateResult:
    """Evaluate whether a next profit candidate is ready for owner review."""

    active_input = _coerce_input(gate_input)
    trade = active_input.trade_334_loss
    candidate = active_input.candidate
    config = active_input.config

    trade_metrics = _trade_metrics(trade)
    candidate_metrics = _candidate_metrics(candidate, config)

    classification, blockers = _classify(active_input)
    next_demo_trade_allowed = (
        classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY
        and active_input.next_demo_trade_allowed
        and not active_input.broker_action_allowed
        and not active_input.live_trading_allowed
    )
    real_money_allowed = (
        classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY
        and active_input.real_money_allowed
        and active_input.live_trading_allowed
        and active_input.broker_action_allowed
        and not active_input.owner_approval_required
    )
    compounding_allowed = (
        classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY
        and active_input.compounding_allowed
        and real_money_allowed
    )
    broker_action_allowed = (
        classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY
        and real_money_allowed
        and active_input.broker_action_allowed
    )
    live_trading_allowed = (
        classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY
        and real_money_allowed
        and active_input.live_trading_allowed
    )
    permissions = {
        "next_demo_trade_allowed": next_demo_trade_allowed,
        "real_money_allowed": real_money_allowed,
        "compounding_allowed": compounding_allowed,
        "owner_approval_required": active_input.owner_approval_required,
        "broker_action_allowed": broker_action_allowed,
        "live_trading_allowed": live_trading_allowed,
    }

    operator_answer = _operator_answer(classification, trade, blockers)
    return LossToNextProfitCandidateResult(
        classification=classification,
        next_demo_trade_allowed=next_demo_trade_allowed,
        real_money_allowed=real_money_allowed,
        compounding_allowed=compounding_allowed,
        broker_action_allowed=broker_action_allowed,
        live_trading_allowed=live_trading_allowed,
        owner_approval_required=active_input.owner_approval_required,
        operator_answer=operator_answer,
        blockers=tuple(blockers),
        trade_334_metrics=trade_metrics,
        candidate_metrics=candidate_metrics,
        permissions=permissions,
        next_safe_action=_next_safe_action(classification),
    )


def result_to_operator_text(result: LossToNextProfitCandidateResult) -> str:
    """Format deterministic operator-readable output."""

    lines = [
        "AIOS Forex Loss To Next Profit Candidate Gate V1",
        f"classification: {result.classification}",
        f"next_demo_trade_allowed: {_bool_text(result.next_demo_trade_allowed)}",
        f"real_money_allowed: {_bool_text(result.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(result.compounding_allowed)}",
        f"broker_action_allowed: {_bool_text(result.broker_action_allowed)}",
        f"live_trading_allowed: {_bool_text(result.live_trading_allowed)}",
        f"owner_approval_required: {_bool_text(result.owner_approval_required)}",
        f"operator_answer: {result.operator_answer}",
        "blockers:",
    ]
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")
    lines.extend(
        [
            "trade_334:",
            f"- trade_id: {result.trade_334_metrics['trade_id']}",
            f"- close_reason: {result.trade_334_metrics['close_reason']}",
            (
                "- realized_pl_total: "
                f"{_json_value(result.trade_334_metrics['realized_pl_total'])}"
            ),
            "candidate:",
            f"- candidate_id: {result.candidate_metrics['candidate_id']}",
            f"- expectancy: {_json_value(result.candidate_metrics['expectancy'])}",
            f"- profit_factor: {_json_value(result.candidate_metrics['profit_factor'])}",
            f"- max_drawdown: {_json_value(result.candidate_metrics['max_drawdown'])}",
            f"next_safe_action: {result.next_safe_action}",
        ]
    )
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: LossToNextProfitCandidateResult) -> dict[str, Any]:
    """Return deterministic JSON-safe result data."""

    return {
        "classification": result.classification,
        "blockers": list(result.blockers),
        "trade_334_metrics": _jsonable_mapping(result.trade_334_metrics),
        "candidate_metrics": _jsonable_mapping(result.candidate_metrics),
        "permissions": dict(result.permissions),
        "operator_answer": result.operator_answer,
        "next_safe_action": result.next_safe_action,
        "safety": {
            "local_only": True,
            "network_calls": False,
            "broker_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "repo_mutation": False,
            "order_placement": False,
            "live_trading_enablement": False,
        },
    }


def _coerce_input(
    raw: LossToNextProfitCandidateInput | Mapping[str, Any] | None,
) -> LossToNextProfitCandidateInput:
    if isinstance(raw, LossToNextProfitCandidateInput):
        return raw
    if raw is None:
        return LossToNextProfitCandidateInput()
    if isinstance(raw, Mapping):
        trade_raw = raw.get("trade_334_loss", raw.get("trade_334", raw))
        candidate_raw = raw.get("candidate", raw.get("candidate_evidence", raw))
        config_raw = raw.get("config", raw)
        if not isinstance(trade_raw, Mapping):
            trade_raw = {}
        if not isinstance(candidate_raw, Mapping):
            candidate_raw = {}
        if not isinstance(config_raw, Mapping):
            config_raw = {}
        return LossToNextProfitCandidateInput(
            trade_334_loss=Trade334LossEvidence.from_mapping(trade_raw),
            candidate=NextProfitCandidateEvidence.from_mapping(candidate_raw),
            config=LossReviewConfig.from_mapping(config_raw),
            next_demo_trade_allowed=raw.get("next_demo_trade_allowed", False),
            real_money_allowed=raw.get("real_money_allowed", False),
            compounding_allowed=raw.get("compounding_allowed", False),
            owner_approval_required=raw.get("owner_approval_required", True),
            broker_action_allowed=raw.get("broker_action_allowed", False),
            live_trading_allowed=raw.get("live_trading_allowed", False),
        )
    raise TypeError("unsupported loss-to-next-candidate input")


def _classify(
    gate_input: LossToNextProfitCandidateInput,
) -> tuple[str, list[str]]:
    trade = gate_input.trade_334_loss
    candidate = gate_input.candidate
    config = gate_input.config

    loss_blockers = _loss_review_blockers(trade)
    if loss_blockers:
        return NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW, loss_blockers

    if not _has_candidate(candidate):
        return (
            NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE,
            ["no next profit candidate is present for review"],
        )

    if candidate.total_trades < config.minimum_sample_size:
        return (
            NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE,
            [
                (
                    "candidate total trades "
                    f"{candidate.total_trades} below minimum sample size "
                    f"{config.minimum_sample_size}"
                )
            ],
        )
    if not candidate.sample_depth_sufficient:
        return (
            NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE,
            ["candidate sample depth is not sufficient"],
        )
    if candidate.expectancy <= Decimal("0"):
        return (
            NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN,
            [f"candidate expectancy {candidate.expectancy} is not positive"],
        )
    if candidate.profit_factor < config.minimum_profit_factor:
        return (
            NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN,
            [
                (
                    f"candidate profit factor {candidate.profit_factor} below "
                    f"minimum {config.minimum_profit_factor}"
                )
            ],
        )

    risk_blockers = _candidate_risk_blockers(gate_input)
    if risk_blockers:
        return NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS, risk_blockers

    if gate_input.owner_approval_required:
        return NEXT_PROFIT_CANDIDATE_REVIEW_READY, []
    return NEXT_PROFIT_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED, [
        "owner approval requirement is not recorded"
    ]


def _loss_review_blockers(trade: Trade334LossEvidence) -> list[str]:
    blockers: list[str] = []
    if trade.trade_id == "334" and trade.realized_pl_total < Decimal("0"):
        if not trade.loss_acknowledged:
            blockers.append("trade 334 loss has not been acknowledged")
        if not trade.loss_review_completed:
            blockers.append("trade 334 loss review is not complete")
    if trade.open_trade_count != 0:
        blockers.append("trade 334 open trade exposure remains")
    if trade.open_position_count != 0:
        blockers.append("trade 334 open position exposure remains")
    if trade.pending_order_count != 0:
        blockers.append("trade 334 pending order exposure remains")
    if trade.profit_claimed:
        blockers.append("trade 334 must not be treated as profitable")
    if not trade.stop_loss_used:
        blockers.append("trade 334 stop loss use is not proven")
    if not trade.take_profit_order_cancelled_after_stop:
        blockers.append("trade 334 take-profit cleanup is not proven")
    return blockers


def _candidate_risk_blockers(
    gate_input: LossToNextProfitCandidateInput,
) -> list[str]:
    candidate = gate_input.candidate
    trade = gate_input.trade_334_loss
    config = gate_input.config
    blockers: list[str] = []
    if candidate.max_drawdown > config.maximum_drawdown_allowed:
        blockers.append(
            (
                f"candidate max drawdown {candidate.max_drawdown} exceeds "
                f"maximum {config.maximum_drawdown_allowed}"
            )
        )
    if candidate.consecutive_losses > config.maximum_consecutive_losses_allowed:
        blockers.append("candidate consecutive losses exceed configured maximum")
    if not candidate.walk_forward_gate_cleared:
        blockers.append("candidate walk-forward gate is not cleared")
    if not candidate.risk_controls_present:
        blockers.append("candidate risk controls are missing")
    if not candidate.stop_loss_required:
        blockers.append("candidate stop loss requirement is not present")
    if not candidate.take_profit_required:
        blockers.append("candidate take profit requirement is not present")
    if not candidate.kill_switch_clear:
        blockers.append("candidate kill switch is not clear")
    if not candidate.daily_loss_limit_clear:
        blockers.append("candidate daily loss limit is not clear")
    if trade.open_trade_count != 0 or trade.open_position_count != 0:
        blockers.append("open exposure remains")
    if trade.pending_order_count != 0:
        blockers.append("pending order exposure remains")
    if gate_input.broker_action_allowed:
        blockers.append("broker action must stay disabled in this gate")
    if gate_input.live_trading_allowed:
        blockers.append("live trading must stay disabled in this gate")
    return blockers


def _operator_answer(
    classification: str, trade: Trade334LossEvidence, blockers: list[str]
) -> str:
    if (
        trade.trade_id == "334"
        and trade.realized_pl_total < Decimal("0")
        and classification == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW
    ):
        return SAMPLE_OPERATOR_ANSWER
    if classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY:
        return (
            "The next profit candidate is ready for owner review only. No real "
            "money, broker action, live trading, or compounding is allowed by "
            "this gate."
        )
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE:
        return (
            "Profit is not proven. No next profit candidate is present, so no "
            "next trade, real money, or compounding is allowed."
        )
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE:
        return (
            "Profit is not proven. Candidate sample depth is insufficient, so "
            "no next trade, real money, or compounding is allowed."
        )
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN:
        return (
            "Profit is not proven. Candidate expectancy or profit factor is too "
            "weak, so no next trade, real money, or compounding is allowed."
        )
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS:
        detail = blockers[0] if blockers else "risk limits are not clear"
        return (
            f"Profit is not proven. Candidate review is blocked because {detail}. "
            "No next trade, real money, broker action, or compounding is allowed."
        )
    return (
        "Owner approval evidence is incomplete. No next trade, real money, or "
        "compounding is allowed."
    )


def _next_safe_action(classification: str) -> str:
    if classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY:
        return (
            "Prepare an owner review packet for the candidate; do not place a "
            "trade or enable real money."
        )
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW:
        return "Complete trade 334 loss review before approving any next candidate."
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE:
        return "Find and document a candidate before requesting another demo trade."
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE:
        return "Collect deeper demo evidence before candidate review."
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN:
        return "Keep searching in demo until expectancy and profit factor improve."
    if classification == NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS:
        return "Repair candidate risk evidence before another demo trade review."
    return "Record owner approval evidence before any next action."


def _trade_metrics(trade: Trade334LossEvidence) -> dict[str, Any]:
    return {
        "trade_id": trade.trade_id,
        "close_reason": trade.close_reason,
        "realized_pl_total": trade.realized_pl_total,
        "pl_capture_classification": trade.pl_capture_classification,
        "profit_claimed": trade.profit_claimed,
        "stop_loss_used": trade.stop_loss_used,
        "take_profit_order_cancelled_after_stop": (
            trade.take_profit_order_cancelled_after_stop
        ),
        "open_trade_count": trade.open_trade_count,
        "open_position_count": trade.open_position_count,
        "pending_order_count": trade.pending_order_count,
        "loss_acknowledged": trade.loss_acknowledged,
        "loss_review_completed": trade.loss_review_completed,
    }


def _candidate_metrics(
    candidate: NextProfitCandidateEvidence, config: LossReviewConfig
) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "strategy_name": candidate.strategy_name,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "total_trades": candidate.total_trades,
        "wins": candidate.wins,
        "losses": candidate.losses,
        "expectancy": candidate.expectancy,
        "profit_factor": candidate.profit_factor,
        "minimum_profit_factor": config.minimum_profit_factor,
        "max_drawdown": candidate.max_drawdown,
        "maximum_drawdown_allowed": config.maximum_drawdown_allowed,
        "consecutive_losses": candidate.consecutive_losses,
        "maximum_consecutive_losses_allowed": (
            config.maximum_consecutive_losses_allowed
        ),
        "minimum_sample_size": config.minimum_sample_size,
        "walk_forward_gate_cleared": candidate.walk_forward_gate_cleared,
        "sample_depth_sufficient": candidate.sample_depth_sufficient,
        "risk_controls_present": candidate.risk_controls_present,
        "stop_loss_required": candidate.stop_loss_required,
        "take_profit_required": candidate.take_profit_required,
        "kill_switch_clear": candidate.kill_switch_clear,
        "daily_loss_limit_clear": candidate.daily_loss_limit_clear,
    }


def _has_candidate(candidate: NextProfitCandidateEvidence) -> bool:
    return candidate.candidate_id.strip().upper() not in {"", "NONE", "UNKNOWN"}


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


def _jsonable_mapping(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {key: _json_value(value) for key, value in raw.items()}


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
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
