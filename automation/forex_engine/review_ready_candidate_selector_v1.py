"""Local-only selector for AI_OS Forex review-ready candidates.

This module evaluates multiple candidate evidence records through the existing
candidate-to-gate bridge, ranks only bridge-approved candidates, and selects one
candidate for operator review. It does not read credentials, read .env files,
call brokers, place orders, start automation, or enable live trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal, getcontext
from enum import Enum
from typing import Any, Mapping, Sequence

from automation.forex_engine.candidate_evidence_intake_v1 import (
    CandidateEvidenceIntakeConfig,
    RawCandidateEvidence,
)
from automation.forex_engine.candidate_to_gate_bridge_v1 import (
    CANDIDATE_TO_GATE_BLOCKED_GATE_REJECTED,
    CANDIDATE_TO_GATE_BLOCKED_INTAKE,
    CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW,
    CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED,
    CANDIDATE_TO_GATE_REVIEW_READY,
    CandidateToGateBridgeConfig,
    CandidateToGateBridgeInput,
    CandidateToGateBridgeResult,
    bridge_candidate_evidence_to_gate,
    result_to_jsonable_dict as bridge_result_to_jsonable_dict,
)
from automation.forex_engine.loss_to_next_profit_candidate_gate_v1 import (
    LossReviewConfig,
    Trade334LossEvidence,
)


getcontext().prec = 28

REVIEW_READY_CANDIDATE_SELECTED = "REVIEW_READY_CANDIDATE_SELECTED"
REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY = (
    "REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY"
)
REVIEW_READY_CANDIDATE_BLOCKED_ALL_INTAKE = (
    "REVIEW_READY_CANDIDATE_BLOCKED_ALL_INTAKE"
)
REVIEW_READY_CANDIDATE_BLOCKED_ALL_GATE = "REVIEW_READY_CANDIDATE_BLOCKED_ALL_GATE"
REVIEW_READY_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED = (
    "REVIEW_READY_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED"
)

VALID_CLASSIFICATIONS = {
    REVIEW_READY_CANDIDATE_SELECTED,
    REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY,
    REVIEW_READY_CANDIDATE_BLOCKED_ALL_INTAKE,
    REVIEW_READY_CANDIDATE_BLOCKED_ALL_GATE,
    REVIEW_READY_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED,
}

SELECTED_OPERATOR_ANSWER_TEMPLATE = (
    "Review-ready candidate selected for operator review: {candidate_id}. "
    "This is review-ready only. No next demo trade, real money, broker action, "
    "or compounding is approved."
)
NONE_READY_OPERATOR_ANSWER = (
    "No review-ready Forex candidate is selected. All candidates are blocked "
    "by intake or gate checks. No next demo trade, real money, broker action, "
    "or compounding is allowed."
)

REVIEW_READY_GATE_BLOCKERS = {
    CANDIDATE_TO_GATE_BLOCKED_GATE_REJECTED,
    CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW,
}


def _review_complete_trade_334_loss() -> Trade334LossEvidence:
    return Trade334LossEvidence(
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
        loss_review_completed=True,
    )


@dataclass(frozen=True)
class ReviewReadyCandidateSelectorConfig:
    """Configuration for bridge evaluation and deterministic scoring."""

    bridge_config: CandidateToGateBridgeConfig = field(
        default_factory=CandidateToGateBridgeConfig
    )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ReviewReadyCandidateSelectorConfig":
        bridge_raw = raw.get("bridge_config", raw)
        if isinstance(bridge_raw, CandidateToGateBridgeConfig):
            bridge_config = bridge_raw
        elif isinstance(bridge_raw, Mapping):
            bridge_config = CandidateToGateBridgeConfig.from_mapping(bridge_raw)
        else:
            bridge_config = CandidateToGateBridgeConfig()
        return cls(bridge_config=bridge_config)


@dataclass(frozen=True)
class ReviewReadyCandidateSelectorInput:
    """Input envelope for selecting from multiple candidate evidence records."""

    candidate_evidence_records: Sequence[
        RawCandidateEvidence | Mapping[str, Any] | None
    ] = field(default_factory=tuple)
    trade_334_loss: Trade334LossEvidence = field(
        default_factory=_review_complete_trade_334_loss
    )
    config: ReviewReadyCandidateSelectorConfig = field(
        default_factory=ReviewReadyCandidateSelectorConfig
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "candidate_evidence_records", tuple(self.candidate_evidence_records)
        )


@dataclass(frozen=True)
class CandidateSelectionRecord:
    """Per-candidate selector evidence and bridge result."""

    original_index: int
    candidate_id: str
    bridge_classification: str
    intake_classification: str
    gate_classification: str
    review_ready: bool
    score: Decimal | None
    rank: int | None
    expectancy: Decimal
    profit_factor: Decimal
    max_drawdown: Decimal
    total_trades: int
    consecutive_losses: int
    win_rate: Decimal
    score_components: Mapping[str, Any]
    blockers: tuple[str, ...]
    bridge_result: CandidateToGateBridgeResult


@dataclass(frozen=True)
class ReviewReadyCandidateSelectorResult:
    """Final selector decision for operator review only."""

    classification: str
    selector_classification: str
    selected_candidate_id: str
    selected_candidate: CandidateSelectionRecord | None
    rankings: tuple[CandidateSelectionRecord, ...]
    candidate_records: tuple[CandidateSelectionRecord, ...]
    candidate_review_allowed: bool
    next_demo_trade_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    broker_action_allowed: bool
    live_trading_allowed: bool
    owner_approval_required: bool
    operator_answer: str
    blockers: tuple[str, ...]
    permissions: Mapping[str, bool]
    next_safe_action: str

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification}")
        if self.selector_classification != self.classification:
            raise ValueError("selector_classification must match classification")


def build_sample_mixed_selector_input() -> ReviewReadyCandidateSelectorInput:
    """Return a mixed sample where the stronger review-ready candidate wins."""

    return ReviewReadyCandidateSelectorInput(
        candidate_evidence_records=(
            {
                "candidate_id": "NONE",
                "symbol": "EUR_USD",
                "evidence_source": "synthetic_incomplete_selector_sample",
                "total_trades": 1,
                "wins": 0,
                "losses": 1,
                "realized_pl_total": Decimal("-0.10"),
                "expectancy": Decimal("-0.10"),
                "profit_factor": Decimal("0"),
                "max_drawdown": Decimal("0.001"),
                "consecutive_losses": 1,
            },
            {
                "candidate_id": "weak-negative-expectancy",
                "strategy_name": "paper_long_run_supervisor_v2",
                "symbol": "EUR_USD",
                "direction": "LONG",
                "timeframe": "DEMO_REVIEW",
                "evidence_source": "synthetic_negative_expectancy_sample",
                "total_trades": 25,
                "wins": 10,
                "losses": 15,
                "realized_pl_total": Decimal("-4.00"),
                "expectancy": Decimal("-0.16"),
                "profit_factor": Decimal("1.10"),
                "max_drawdown": Decimal("0.030"),
                "consecutive_losses": 2,
                "average_win": Decimal("0.80"),
                "average_loss": Decimal("-0.75"),
                "sample_depth_sufficient": True,
                "walk_forward_gate_cleared": True,
                "risk_controls_present": True,
                "stop_loss_required": True,
                "take_profit_required": True,
                "kill_switch_clear": True,
                "daily_loss_limit_clear": True,
            },
            _review_ready_candidate_a(),
            _review_ready_candidate_b(),
        )
    )


def build_sample_all_blocked_selector_input() -> ReviewReadyCandidateSelectorInput:
    """Return a sample where no candidate is eligible for operator review."""

    return ReviewReadyCandidateSelectorInput(
        candidate_evidence_records=(
            {
                "candidate_id": "NONE",
                "symbol": "EUR_USD",
                "evidence_source": "synthetic_incomplete_selector_sample",
                "total_trades": 1,
                "wins": 0,
                "losses": 1,
                "realized_pl_total": Decimal("-0.10"),
                "expectancy": Decimal("-0.10"),
                "profit_factor": Decimal("0"),
                "max_drawdown": Decimal("0.001"),
                "consecutive_losses": 1,
            },
            {
                "candidate_id": "weak-negative-expectancy",
                "strategy_name": "paper_long_run_supervisor_v2",
                "symbol": "EUR_USD",
                "direction": "LONG",
                "timeframe": "DEMO_REVIEW",
                "evidence_source": "synthetic_negative_expectancy_sample",
                "total_trades": 25,
                "wins": 10,
                "losses": 15,
                "realized_pl_total": Decimal("-4.00"),
                "expectancy": Decimal("-0.16"),
                "profit_factor": Decimal("1.10"),
                "max_drawdown": Decimal("0.030"),
                "consecutive_losses": 2,
                "average_win": Decimal("0.80"),
                "average_loss": Decimal("-0.75"),
                "sample_depth_sufficient": True,
                "walk_forward_gate_cleared": True,
                "risk_controls_present": True,
                "stop_loss_required": True,
                "take_profit_required": True,
                "kill_switch_clear": True,
                "daily_loss_limit_clear": True,
            },
            {
                "candidate_id": "weak-low-profit-factor",
                "strategy_name": "paper_long_run_supervisor_v2",
                "symbol": "EUR_USD",
                "direction": "LONG",
                "timeframe": "DEMO_REVIEW",
                "evidence_source": "synthetic_low_profit_factor_sample",
                "total_trades": 30,
                "wins": 17,
                "losses": 13,
                "realized_pl_total": Decimal("3.00"),
                "expectancy": Decimal("0.10"),
                "profit_factor": Decimal("1.30"),
                "max_drawdown": Decimal("0.025"),
                "consecutive_losses": 2,
                "average_win": Decimal("1.00"),
                "average_loss": Decimal("-0.80"),
                "sample_depth_sufficient": True,
                "walk_forward_gate_cleared": True,
                "risk_controls_present": True,
                "stop_loss_required": True,
                "take_profit_required": True,
                "kill_switch_clear": True,
                "daily_loss_limit_clear": True,
            },
        ),
        config=ReviewReadyCandidateSelectorConfig(
            bridge_config=CandidateToGateBridgeConfig(
                intake_config=CandidateEvidenceIntakeConfig(
                    minimum_profit_factor=Decimal("1.25")
                ),
                gate_config=LossReviewConfig(minimum_profit_factor=Decimal("1.50")),
            )
        ),
    )


def select_review_ready_candidate(
    selector_input: ReviewReadyCandidateSelectorInput | Mapping[str, Any] | None = None,
) -> ReviewReadyCandidateSelectorResult:
    """Evaluate, rank, and select one bridge-approved review candidate."""

    active_input = _coerce_input(selector_input)
    candidate_records = tuple(
        _evaluate_candidate(index, candidate, active_input)
        for index, candidate in enumerate(active_input.candidate_evidence_records)
    )
    ranked_records = _rank_review_ready_records(candidate_records)
    ranked_by_index = {record.original_index: record for record in ranked_records}
    candidate_records = tuple(
        ranked_by_index.get(record.original_index, record)
        for record in candidate_records
    )
    selected_candidate = ranked_records[0] if ranked_records else None
    classification = _classify(candidate_records, ranked_records)
    selected_candidate_id = (
        selected_candidate.candidate_id if selected_candidate is not None else "NONE"
    )
    permissions = _permissions(candidate_review_allowed=selected_candidate is not None)

    return ReviewReadyCandidateSelectorResult(
        classification=classification,
        selector_classification=classification,
        selected_candidate_id=selected_candidate_id,
        selected_candidate=selected_candidate,
        rankings=ranked_records,
        candidate_records=candidate_records,
        candidate_review_allowed=selected_candidate is not None,
        next_demo_trade_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        broker_action_allowed=False,
        live_trading_allowed=False,
        owner_approval_required=True,
        operator_answer=_operator_answer(classification, selected_candidate_id),
        blockers=_selector_blockers(candidate_records),
        permissions=permissions,
        next_safe_action=_next_safe_action(classification),
    )


def result_to_operator_text(result: ReviewReadyCandidateSelectorResult) -> str:
    """Format deterministic operator-readable selector output."""

    lines = [
        "AIOS Forex Review-Ready Candidate Selector V1",
        f"selector_classification: {result.selector_classification}",
        f"selected_candidate_id: {result.selected_candidate_id}",
        f"candidate_review_allowed: {_bool_text(result.candidate_review_allowed)}",
        f"next_demo_trade_allowed: {_bool_text(result.next_demo_trade_allowed)}",
        f"real_money_allowed: {_bool_text(result.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(result.compounding_allowed)}",
        f"broker_action_allowed: {_bool_text(result.broker_action_allowed)}",
        f"live_trading_allowed: {_bool_text(result.live_trading_allowed)}",
        f"owner_approval_required: {_bool_text(result.owner_approval_required)}",
        f"operator_answer: {result.operator_answer}",
        "rankings:",
    ]
    if result.rankings:
        lines.extend(
            (
                f"- rank {record.rank}: {record.candidate_id} "
                f"score={_json_value(record.score)}"
            )
            for record in result.rankings
        )
    else:
        lines.append("- none")
    lines.append("blocked_candidates:")
    blocked_records = [record for record in result.candidate_records if not record.review_ready]
    if blocked_records:
        for record in blocked_records:
            blocker_text = "; ".join(record.blockers) if record.blockers else "blocked"
            lines.append(f"- {record.candidate_id}: {record.bridge_classification}: {blocker_text}")
    else:
        lines.append("- none")
    lines.append(f"next_safe_action: {result.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: ReviewReadyCandidateSelectorResult) -> dict[str, Any]:
    """Return deterministic JSON-safe selector data."""

    return {
        "classification": result.classification,
        "selector_classification": result.selector_classification,
        "selected_candidate_id": result.selected_candidate_id,
        "selected_candidate": _selection_record_to_jsonable(result.selected_candidate),
        "rankings": [_selection_record_to_jsonable(record) for record in result.rankings],
        "candidate_records": [
            _selection_record_to_jsonable(record) for record in result.candidate_records
        ],
        "permissions": dict(result.permissions),
        "candidate_review_allowed": result.candidate_review_allowed,
        "next_demo_trade_allowed": result.next_demo_trade_allowed,
        "real_money_allowed": result.real_money_allowed,
        "compounding_allowed": result.compounding_allowed,
        "broker_action_allowed": result.broker_action_allowed,
        "live_trading_allowed": result.live_trading_allowed,
        "owner_approval_required": result.owner_approval_required,
        "operator_answer": result.operator_answer,
        "blockers": list(result.blockers),
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


def _review_ready_candidate_a() -> dict[str, Any]:
    return {
        "candidate_id": "c1-eur-buy-review-ready",
        "strategy_name": "paper_long_run_supervisor_v2",
        "symbol": "EUR_USD",
        "direction": "LONG",
        "timeframe": "DEMO_REVIEW",
        "evidence_source": "synthetic_review_ready_sample_a",
        "total_trades": 25,
        "wins": 16,
        "losses": 9,
        "realized_pl_total": Decimal("12.50"),
        "expectancy": Decimal("0.50"),
        "profit_factor": Decimal("1.60"),
        "max_drawdown": Decimal("0.025"),
        "consecutive_losses": 2,
        "average_win": Decimal("1.20"),
        "average_loss": Decimal("-0.75"),
        "sample_depth_sufficient": True,
        "walk_forward_gate_cleared": True,
        "risk_controls_present": True,
        "stop_loss_required": True,
        "take_profit_required": True,
        "kill_switch_clear": True,
        "daily_loss_limit_clear": True,
    }


def _review_ready_candidate_b() -> dict[str, Any]:
    return {
        "candidate_id": "c2-eur-buy-stronger-review-ready",
        "strategy_name": "paper_long_run_supervisor_v2",
        "symbol": "EUR_USD",
        "direction": "LONG",
        "timeframe": "DEMO_REVIEW",
        "evidence_source": "synthetic_review_ready_sample_b",
        "total_trades": 40,
        "wins": 27,
        "losses": 13,
        "realized_pl_total": Decimal("28.00"),
        "expectancy": Decimal("0.70"),
        "profit_factor": Decimal("1.90"),
        "max_drawdown": Decimal("0.020"),
        "consecutive_losses": 2,
        "average_win": Decimal("1.35"),
        "average_loss": Decimal("-0.65"),
        "sample_depth_sufficient": True,
        "walk_forward_gate_cleared": True,
        "risk_controls_present": True,
        "stop_loss_required": True,
        "take_profit_required": True,
        "kill_switch_clear": True,
        "daily_loss_limit_clear": True,
    }


def _coerce_input(
    raw: ReviewReadyCandidateSelectorInput | Mapping[str, Any] | None,
) -> ReviewReadyCandidateSelectorInput:
    if isinstance(raw, ReviewReadyCandidateSelectorInput):
        return raw
    if raw is None:
        return build_sample_all_blocked_selector_input()
    if isinstance(raw, Mapping):
        candidates = raw.get(
            "candidate_evidence_records",
            raw.get("candidate_records", raw.get("candidates", ())),
        )
        if candidates is None:
            candidates = ()
        if isinstance(candidates, Mapping):
            candidates = (candidates,)
        config_raw = raw.get("config", raw)
        if isinstance(config_raw, ReviewReadyCandidateSelectorConfig):
            config = config_raw
        elif isinstance(config_raw, Mapping):
            config = ReviewReadyCandidateSelectorConfig.from_mapping(config_raw)
        else:
            config = ReviewReadyCandidateSelectorConfig()
        trade_raw = raw.get("trade_334_loss", raw.get("trade_334", {}))
        if isinstance(trade_raw, Trade334LossEvidence):
            trade_334_loss = trade_raw
        elif isinstance(trade_raw, Mapping):
            trade_334_loss = Trade334LossEvidence.from_mapping(trade_raw)
        else:
            trade_334_loss = _review_complete_trade_334_loss()
        return ReviewReadyCandidateSelectorInput(
            candidate_evidence_records=tuple(candidates),
            trade_334_loss=trade_334_loss,
            config=config,
        )
    raise TypeError("unsupported review-ready selector input")


def _evaluate_candidate(
    index: int,
    candidate: RawCandidateEvidence | Mapping[str, Any] | None,
    selector_input: ReviewReadyCandidateSelectorInput,
) -> CandidateSelectionRecord:
    bridge_result = bridge_candidate_evidence_to_gate(
        CandidateToGateBridgeInput(
            candidate_evidence=candidate,
            trade_334_loss=selector_input.trade_334_loss,
            config=selector_input.config.bridge_config,
        )
    )
    normalized = bridge_result.intake_result.normalized_candidate
    review_ready = bridge_result.classification == CANDIDATE_TO_GATE_REVIEW_READY
    score = None
    score_components: Mapping[str, Any] = {}
    if review_ready:
        score, score_components = _score_candidate(
            normalized,
            selector_input.config,
        )
    win_rate = _win_rate(normalized.wins, normalized.total_trades)
    return CandidateSelectionRecord(
        original_index=index,
        candidate_id=normalized.candidate_id,
        bridge_classification=bridge_result.bridge_classification,
        intake_classification=bridge_result.intake_classification,
        gate_classification=bridge_result.gate_classification,
        review_ready=review_ready,
        score=score,
        rank=None,
        expectancy=normalized.expectancy,
        profit_factor=normalized.profit_factor,
        max_drawdown=normalized.max_drawdown,
        total_trades=normalized.total_trades,
        consecutive_losses=normalized.consecutive_losses,
        win_rate=win_rate,
        score_components=score_components,
        blockers=tuple(bridge_result.blockers),
        bridge_result=bridge_result,
    )


def _score_candidate(
    candidate: Any,
    config: ReviewReadyCandidateSelectorConfig,
) -> tuple[Decimal, Mapping[str, Any]]:
    minimum_sample = Decimal(config.bridge_config.intake_config.minimum_sample_size)
    minimum_profit_factor = config.bridge_config.intake_config.minimum_profit_factor
    sample_gap = max(Decimal("0"), minimum_sample - Decimal(candidate.total_trades))
    profit_factor_gap = max(
        Decimal("0"), minimum_profit_factor - candidate.profit_factor
    )
    win_rate = _win_rate(candidate.wins, candidate.total_trades)
    components = {
        "expectancy_reward": candidate.expectancy * Decimal("100"),
        "profit_factor_reward": candidate.profit_factor * Decimal("50"),
        "total_trades_reward": Decimal(candidate.total_trades),
        "win_rate_reward": win_rate * Decimal("25"),
        "drawdown_penalty": candidate.max_drawdown * Decimal("1000"),
        "consecutive_loss_penalty": Decimal(candidate.consecutive_losses) * Decimal("10"),
        "low_sample_penalty": sample_gap * Decimal("5"),
        "low_profit_factor_penalty": profit_factor_gap * Decimal("50"),
        "walk_forward_reward": _bool_reward(candidate.walk_forward_gate_cleared, "10"),
        "sample_depth_reward": _bool_reward(candidate.sample_depth_sufficient, "10"),
        "risk_controls_reward": _bool_reward(candidate.risk_controls_present, "10"),
        "stop_loss_reward": _bool_reward(candidate.stop_loss_required, "5"),
        "take_profit_reward": _bool_reward(candidate.take_profit_required, "5"),
        "kill_switch_reward": _bool_reward(candidate.kill_switch_clear, "5"),
        "daily_loss_limit_reward": _bool_reward(candidate.daily_loss_limit_clear, "5"),
    }
    score = (
        components["expectancy_reward"]
        + components["profit_factor_reward"]
        + components["total_trades_reward"]
        + components["win_rate_reward"]
        - components["drawdown_penalty"]
        - components["consecutive_loss_penalty"]
        - components["low_sample_penalty"]
        - components["low_profit_factor_penalty"]
        + components["walk_forward_reward"]
        + components["sample_depth_reward"]
        + components["risk_controls_reward"]
        + components["stop_loss_reward"]
        + components["take_profit_reward"]
        + components["kill_switch_reward"]
        + components["daily_loss_limit_reward"]
    )
    components = {**components, "score": score}
    return score, components


def _rank_review_ready_records(
    records: Sequence[CandidateSelectionRecord],
) -> tuple[CandidateSelectionRecord, ...]:
    ready_records = [record for record in records if record.review_ready]
    ready_records.sort(
        key=lambda record: (
            -(record.score if record.score is not None else Decimal("-Infinity")),
            -record.expectancy,
            -record.profit_factor,
            record.max_drawdown,
            -record.total_trades,
            record.candidate_id,
            record.original_index,
        )
    )
    return tuple(
        replace(record, rank=index)
        for index, record in enumerate(ready_records, start=1)
    )


def _classify(
    records: Sequence[CandidateSelectionRecord],
    ranked_records: Sequence[CandidateSelectionRecord],
) -> str:
    if ranked_records:
        return REVIEW_READY_CANDIDATE_SELECTED
    if not records:
        return REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY
    bridge_classifications = {record.bridge_classification for record in records}
    if bridge_classifications == {CANDIDATE_TO_GATE_BLOCKED_INTAKE}:
        return REVIEW_READY_CANDIDATE_BLOCKED_ALL_INTAKE
    if bridge_classifications == {CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED}:
        return REVIEW_READY_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED
    if bridge_classifications <= REVIEW_READY_GATE_BLOCKERS:
        return REVIEW_READY_CANDIDATE_BLOCKED_ALL_GATE
    return REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY


def _operator_answer(classification: str, selected_candidate_id: str) -> str:
    if classification == REVIEW_READY_CANDIDATE_SELECTED:
        return SELECTED_OPERATOR_ANSWER_TEMPLATE.format(
            candidate_id=selected_candidate_id
        )
    if classification == REVIEW_READY_CANDIDATE_BLOCKED_ALL_INTAKE:
        return (
            "No review-ready Forex candidate is selected. Every candidate is "
            "blocked by intake. No next demo trade, real money, broker action, "
            "or compounding is allowed."
        )
    if classification == REVIEW_READY_CANDIDATE_BLOCKED_ALL_GATE:
        return (
            "No review-ready Forex candidate is selected. Every candidate is "
            "blocked by gate checks. No next demo trade, real money, broker "
            "action, or compounding is allowed."
        )
    if classification == REVIEW_READY_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED:
        return (
            "No review-ready Forex candidate is selected. Owner approval evidence "
            "is incomplete. No next demo trade, real money, broker action, or "
            "compounding is allowed."
        )
    return NONE_READY_OPERATOR_ANSWER


def _next_safe_action(classification: str) -> str:
    if classification == REVIEW_READY_CANDIDATE_SELECTED:
        return (
            "Prepare an operator review packet for the selected candidate; do "
            "not place a trade or enable real money."
        )
    return (
        "Repair blocked candidate evidence and rerun the selector before any "
        "operator review or next-trade request."
    )


def _selector_blockers(records: Sequence[CandidateSelectionRecord]) -> tuple[str, ...]:
    blockers: list[str] = []
    for record in records:
        if record.review_ready:
            continue
        if record.blockers:
            blockers.extend(
                f"{record.candidate_id}: {blocker}" for blocker in record.blockers
            )
        else:
            blockers.append(
                f"{record.candidate_id}: {record.bridge_classification}"
            )
    if not records:
        blockers.append("no candidate evidence records were provided")
    return tuple(blockers)


def _permissions(*, candidate_review_allowed: bool) -> dict[str, bool]:
    return {
        "candidate_review_allowed": candidate_review_allowed,
        "next_demo_trade_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "broker_action_allowed": False,
        "live_trading_allowed": False,
        "owner_approval_required": True,
    }


def _selection_record_to_jsonable(
    record: CandidateSelectionRecord | None,
) -> dict[str, Any] | None:
    if record is None:
        return None
    return {
        "original_index": record.original_index,
        "candidate_id": record.candidate_id,
        "bridge_classification": record.bridge_classification,
        "intake_classification": record.intake_classification,
        "gate_classification": record.gate_classification,
        "review_ready": record.review_ready,
        "score": _json_value(record.score),
        "rank": record.rank,
        "expectancy": _json_value(record.expectancy),
        "profit_factor": _json_value(record.profit_factor),
        "max_drawdown": _json_value(record.max_drawdown),
        "total_trades": record.total_trades,
        "consecutive_losses": record.consecutive_losses,
        "win_rate": _json_value(record.win_rate),
        "score_components": _json_value(record.score_components),
        "blockers": list(record.blockers),
        "bridge_result": bridge_result_to_jsonable_dict(record.bridge_result),
    }


def _win_rate(wins: int, total_trades: int) -> Decimal:
    if total_trades <= 0:
        return Decimal("0")
    return Decimal(wins) / Decimal(total_trades)


def _bool_reward(value: bool, reward: str) -> Decimal:
    return Decimal(reward) if value else Decimal("0")


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
