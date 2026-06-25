"""Local-only bridge from candidate evidence intake to next-candidate gate.

This module orchestrates existing AI_OS Forex review components. It does not
read credentials, read .env files, call brokers, place orders, start automation,
or enable live trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping

from automation.forex_engine.candidate_evidence_intake_v1 import (
    CANDIDATE_EVIDENCE_REVIEW_READY,
    CandidateEvidenceIntakeConfig,
    CandidateEvidenceIntakeResult,
    NormalizedCandidateEvidence,
    RawCandidateEvidence,
    build_sample_incomplete_candidate,
    build_sample_review_ready_candidate,
    evaluate_candidate_evidence_intake,
    result_to_jsonable_dict as intake_result_to_jsonable_dict,
)
from automation.forex_engine.loss_to_next_profit_candidate_gate_v1 import (
    NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW,
    NEXT_PROFIT_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED,
    NEXT_PROFIT_CANDIDATE_REVIEW_READY,
    LossReviewConfig,
    LossToNextProfitCandidateInput,
    LossToNextProfitCandidateResult,
    NextProfitCandidateEvidence,
    Trade334LossEvidence,
    evaluate_loss_to_next_profit_candidate_gate,
    result_to_jsonable_dict as gate_result_to_jsonable_dict,
)


CANDIDATE_TO_GATE_REVIEW_READY = "CANDIDATE_TO_GATE_REVIEW_READY"
CANDIDATE_TO_GATE_BLOCKED_INTAKE = "CANDIDATE_TO_GATE_BLOCKED_INTAKE"
CANDIDATE_TO_GATE_BLOCKED_CONVERSION = "CANDIDATE_TO_GATE_BLOCKED_CONVERSION"
CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW = "CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW"
CANDIDATE_TO_GATE_BLOCKED_GATE_REJECTED = (
    "CANDIDATE_TO_GATE_BLOCKED_GATE_REJECTED"
)
CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED = (
    "CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED"
)

VALID_CLASSIFICATIONS = {
    CANDIDATE_TO_GATE_REVIEW_READY,
    CANDIDATE_TO_GATE_BLOCKED_INTAKE,
    CANDIDATE_TO_GATE_BLOCKED_CONVERSION,
    CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW,
    CANDIDATE_TO_GATE_BLOCKED_GATE_REJECTED,
    CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED,
}

INTAKE_BLOCKED_OPERATOR_ANSWER = (
    "Candidate evidence intake blocked the bridge. Evidence is not "
    "review-ready, so it cannot be sent to the next-profit-candidate gate. "
    "No next demo trade, real money, broker action, or compounding is allowed."
)

REVIEW_READY_OPERATOR_ANSWER = (
    "Candidate evidence intake passed and the next-profit-candidate gate "
    "accepted the candidate for review. This is review-ready only. No next "
    "demo trade, real money, broker action, or compounding is approved."
)


@dataclass(frozen=True)
class CandidateToGateBridgeConfig:
    """Configuration passed through to intake and gate components."""

    intake_config: CandidateEvidenceIntakeConfig = field(
        default_factory=CandidateEvidenceIntakeConfig
    )
    gate_config: LossReviewConfig = field(default_factory=LossReviewConfig)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CandidateToGateBridgeConfig":
        intake_raw = raw.get("intake_config", raw)
        gate_raw = raw.get("gate_config", raw)
        if not isinstance(intake_raw, Mapping):
            intake_raw = {}
        if not isinstance(gate_raw, Mapping):
            gate_raw = {}
        return cls(
            intake_config=CandidateEvidenceIntakeConfig.from_mapping(intake_raw),
            gate_config=LossReviewConfig.from_mapping(gate_raw),
        )


@dataclass(frozen=True)
class CandidateToGateBridgeInput:
    """Input envelope for bridging candidate evidence into the gate."""

    candidate_evidence: RawCandidateEvidence | Mapping[str, Any] | None = None
    trade_334_loss: Trade334LossEvidence = field(
        default_factory=Trade334LossEvidence
    )
    config: CandidateToGateBridgeConfig = field(
        default_factory=CandidateToGateBridgeConfig
    )


@dataclass(frozen=True)
class CandidateToGateBridgeResult:
    """Combined bridge, intake, and gate result for operator review."""

    classification: str
    bridge_classification: str
    intake_classification: str
    gate_classification: str
    candidate_review_allowed: bool
    next_demo_trade_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    broker_action_allowed: bool
    live_trading_allowed: bool
    owner_approval_required: bool
    operator_answer: str
    blockers: tuple[str, ...]
    intake_result: CandidateEvidenceIntakeResult
    gate_result: LossToNextProfitCandidateResult | None
    converted_candidate: NextProfitCandidateEvidence | None
    permissions: Mapping[str, bool]
    next_safe_action: str

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification}")
        if self.bridge_classification != self.classification:
            raise ValueError("bridge_classification must match classification")


def build_sample_incomplete_bridge_input() -> CandidateToGateBridgeInput:
    """Return an incomplete candidate bridge sample that stops at intake."""

    return CandidateToGateBridgeInput(
        candidate_evidence=build_sample_incomplete_candidate(),
        trade_334_loss=_trade_334_acknowledged_for_review(
            loss_review_completed=False
        ),
    )


def build_sample_review_ready_bridge_input() -> CandidateToGateBridgeInput:
    """Return a review-ready bridge sample with trade 334 context reviewed."""

    return CandidateToGateBridgeInput(
        candidate_evidence=build_sample_review_ready_candidate(),
        trade_334_loss=_trade_334_acknowledged_for_review(
            loss_review_completed=True
        ),
    )


def bridge_candidate_evidence_to_gate(
    bridge_input: CandidateToGateBridgeInput | Mapping[str, Any] | None = None,
) -> CandidateToGateBridgeResult:
    """Run intake, convert normalized evidence, and evaluate the gate."""

    active_input = _coerce_input(bridge_input)
    intake_result = evaluate_candidate_evidence_intake(
        active_input.candidate_evidence,
        config=active_input.config.intake_config,
    )

    if intake_result.classification != CANDIDATE_EVIDENCE_REVIEW_READY:
        blockers = _prefix_blockers("intake", intake_result.blockers)
        return _result(
            classification=CANDIDATE_TO_GATE_BLOCKED_INTAKE,
            intake_result=intake_result,
            gate_result=None,
            converted_candidate=None,
            blockers=blockers,
        )

    try:
        converted_candidate = _convert_to_gate_candidate(
            intake_result.normalized_candidate
        )
    except (TypeError, ValueError) as exc:
        return _result(
            classification=CANDIDATE_TO_GATE_BLOCKED_CONVERSION,
            intake_result=intake_result,
            gate_result=None,
            converted_candidate=None,
            blockers=(f"conversion failed: {exc}",),
        )

    gate_input = LossToNextProfitCandidateInput(
        trade_334_loss=active_input.trade_334_loss,
        candidate=converted_candidate,
        config=active_input.config.gate_config,
        next_demo_trade_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        owner_approval_required=True,
        broker_action_allowed=False,
        live_trading_allowed=False,
    )
    gate_result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    if gate_result.classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY:
        classification = CANDIDATE_TO_GATE_REVIEW_READY
    elif gate_result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW:
        classification = CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW
    elif (
        gate_result.classification
        == NEXT_PROFIT_CANDIDATE_BLOCKED_OWNER_APPROVAL_REQUIRED
    ):
        classification = CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED
    else:
        classification = CANDIDATE_TO_GATE_BLOCKED_GATE_REJECTED

    return _result(
        classification=classification,
        intake_result=intake_result,
        gate_result=gate_result,
        converted_candidate=converted_candidate,
        blockers=_combined_blockers(intake_result, gate_result),
    )


def result_to_operator_text(result: CandidateToGateBridgeResult) -> str:
    """Format deterministic operator-readable bridge output."""

    lines = [
        "AIOS Forex Candidate To Gate Bridge V1",
        f"bridge_classification: {result.bridge_classification}",
        f"intake_classification: {result.intake_classification}",
        f"gate_classification: {result.gate_classification}",
        f"candidate_review_allowed: {_bool_text(result.candidate_review_allowed)}",
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
    lines.append("converted_candidate:")
    if result.converted_candidate is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- candidate_id: {result.converted_candidate.candidate_id}",
                f"- strategy_name: {result.converted_candidate.strategy_name}",
                f"- symbol: {result.converted_candidate.symbol}",
                f"- direction: {result.converted_candidate.direction}",
                f"- total_trades: {result.converted_candidate.total_trades}",
                f"- expectancy: {_json_value(result.converted_candidate.expectancy)}",
                (
                    "- profit_factor: "
                    f"{_json_value(result.converted_candidate.profit_factor)}"
                ),
                (
                    "- max_drawdown: "
                    f"{_json_value(result.converted_candidate.max_drawdown)}"
                ),
            ]
        )
    lines.append(f"next_safe_action: {result.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: CandidateToGateBridgeResult) -> dict[str, Any]:
    """Return deterministic JSON-safe bridge data."""

    return {
        "classification": result.classification,
        "bridge_classification": result.bridge_classification,
        "intake_classification": result.intake_classification,
        "gate_classification": result.gate_classification,
        "intake": intake_result_to_jsonable_dict(result.intake_result),
        "gate": (
            gate_result_to_jsonable_dict(result.gate_result)
            if result.gate_result is not None
            else None
        ),
        "converted_candidate": _converted_candidate_to_jsonable(
            result.converted_candidate
        ),
        "blockers": list(result.blockers),
        "permissions": dict(result.permissions),
        "candidate_review_allowed": result.candidate_review_allowed,
        "next_demo_trade_allowed": result.next_demo_trade_allowed,
        "real_money_allowed": result.real_money_allowed,
        "compounding_allowed": result.compounding_allowed,
        "broker_action_allowed": result.broker_action_allowed,
        "live_trading_allowed": result.live_trading_allowed,
        "owner_approval_required": result.owner_approval_required,
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
    raw: CandidateToGateBridgeInput | Mapping[str, Any] | None,
) -> CandidateToGateBridgeInput:
    if isinstance(raw, CandidateToGateBridgeInput):
        return raw
    if raw is None:
        return build_sample_incomplete_bridge_input()
    if isinstance(raw, Mapping):
        config_raw = raw.get("config", raw)
        if not isinstance(config_raw, Mapping):
            config_raw = {}
        trade_raw = raw.get("trade_334_loss", raw.get("trade_334", {}))
        if isinstance(trade_raw, Trade334LossEvidence):
            trade_334_loss = trade_raw
        elif isinstance(trade_raw, Mapping):
            trade_334_loss = Trade334LossEvidence.from_mapping(trade_raw)
        else:
            trade_334_loss = Trade334LossEvidence()
        return CandidateToGateBridgeInput(
            candidate_evidence=raw.get(
                "candidate_evidence",
                raw.get("candidate", raw.get("raw_candidate_evidence")),
            ),
            trade_334_loss=trade_334_loss,
            config=CandidateToGateBridgeConfig.from_mapping(config_raw),
        )
    raise TypeError("unsupported candidate-to-gate bridge input")


def _convert_to_gate_candidate(
    candidate: NormalizedCandidateEvidence,
) -> NextProfitCandidateEvidence:
    return NextProfitCandidateEvidence(
        candidate_id=candidate.candidate_id,
        strategy_name=candidate.strategy_name,
        symbol=candidate.symbol,
        direction=candidate.direction,
        total_trades=candidate.total_trades,
        wins=candidate.wins,
        losses=candidate.losses,
        expectancy=candidate.expectancy,
        profit_factor=candidate.profit_factor,
        max_drawdown=candidate.max_drawdown,
        consecutive_losses=candidate.consecutive_losses,
        walk_forward_gate_cleared=candidate.walk_forward_gate_cleared,
        sample_depth_sufficient=candidate.sample_depth_sufficient,
        risk_controls_present=candidate.risk_controls_present,
        stop_loss_required=candidate.stop_loss_required,
        take_profit_required=candidate.take_profit_required,
        kill_switch_clear=candidate.kill_switch_clear,
        daily_loss_limit_clear=candidate.daily_loss_limit_clear,
    )


def _trade_334_acknowledged_for_review(
    *,
    loss_review_completed: bool,
) -> Trade334LossEvidence:
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
        loss_review_completed=loss_review_completed,
    )


def _result(
    *,
    classification: str,
    intake_result: CandidateEvidenceIntakeResult,
    gate_result: LossToNextProfitCandidateResult | None,
    converted_candidate: NextProfitCandidateEvidence | None,
    blockers: tuple[str, ...],
) -> CandidateToGateBridgeResult:
    candidate_review_allowed = classification == CANDIDATE_TO_GATE_REVIEW_READY
    permissions = {
        "candidate_review_allowed": candidate_review_allowed,
        "next_demo_trade_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "broker_action_allowed": False,
        "live_trading_allowed": False,
        "owner_approval_required": True,
    }
    return CandidateToGateBridgeResult(
        classification=classification,
        bridge_classification=classification,
        intake_classification=intake_result.classification,
        gate_classification=(
            gate_result.classification
            if gate_result is not None
            else "NOT_RUN_INTAKE_BLOCKED"
        ),
        candidate_review_allowed=candidate_review_allowed,
        next_demo_trade_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        broker_action_allowed=False,
        live_trading_allowed=False,
        owner_approval_required=True,
        operator_answer=_operator_answer(classification),
        blockers=tuple(blockers),
        intake_result=intake_result,
        gate_result=gate_result,
        converted_candidate=converted_candidate,
        permissions=permissions,
        next_safe_action=_next_safe_action(classification),
    )


def _combined_blockers(
    intake_result: CandidateEvidenceIntakeResult,
    gate_result: LossToNextProfitCandidateResult,
) -> tuple[str, ...]:
    blockers = list(_prefix_blockers("intake", intake_result.blockers))
    blockers.extend(_prefix_blockers("gate", gate_result.blockers))
    return tuple(blockers)


def _prefix_blockers(prefix: str, blockers: tuple[str, ...]) -> tuple[str, ...]:
    if not blockers:
        return ()
    return tuple(f"{prefix}: {blocker}" for blocker in blockers)


def _operator_answer(classification: str) -> str:
    if classification == CANDIDATE_TO_GATE_REVIEW_READY:
        return REVIEW_READY_OPERATOR_ANSWER
    if classification == CANDIDATE_TO_GATE_BLOCKED_INTAKE:
        return INTAKE_BLOCKED_OPERATOR_ANSWER
    if classification == CANDIDATE_TO_GATE_BLOCKED_CONVERSION:
        return (
            "Candidate evidence intake passed, but bridge conversion failed. "
            "No next demo trade, real money, broker action, or compounding is allowed."
        )
    if classification == CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW:
        return (
            "Candidate evidence reached the gate, but trade 334 loss review is "
            "not clear. No next demo trade, real money, broker action, or "
            "compounding is allowed."
        )
    if classification == CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED:
        return (
            "Candidate evidence reached the gate, but owner approval evidence "
            "is incomplete. No next demo trade, real money, broker action, or "
            "compounding is allowed."
        )
    return (
        "Candidate evidence reached the gate, but the gate rejected review. "
        "No next demo trade, real money, broker action, or compounding is allowed."
    )


def _next_safe_action(classification: str) -> str:
    if classification == CANDIDATE_TO_GATE_REVIEW_READY:
        return (
            "Prepare an operator review packet; do not place a trade or enable "
            "real money."
        )
    if classification == CANDIDATE_TO_GATE_BLOCKED_INTAKE:
        return "Repair candidate intake evidence before sending it to the gate."
    if classification == CANDIDATE_TO_GATE_BLOCKED_CONVERSION:
        return "Repair candidate conversion fields before gate review."
    if classification == CANDIDATE_TO_GATE_BLOCKED_LOSS_REVIEW:
        return "Complete trade 334 loss review before candidate gate review."
    if classification == CANDIDATE_TO_GATE_BLOCKED_OWNER_APPROVAL_REQUIRED:
        return "Record owner approval requirement before any next action."
    return "Repair gate blockers before operator review."


def _converted_candidate_to_jsonable(
    candidate: NextProfitCandidateEvidence | None,
) -> dict[str, Any] | None:
    if candidate is None:
        return None
    return {
        "candidate_id": candidate.candidate_id,
        "strategy_name": candidate.strategy_name,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "total_trades": candidate.total_trades,
        "wins": candidate.wins,
        "losses": candidate.losses,
        "expectancy": _json_value(candidate.expectancy),
        "profit_factor": _json_value(candidate.profit_factor),
        "max_drawdown": _json_value(candidate.max_drawdown),
        "consecutive_losses": candidate.consecutive_losses,
        "walk_forward_gate_cleared": candidate.walk_forward_gate_cleared,
        "sample_depth_sufficient": candidate.sample_depth_sufficient,
        "risk_controls_present": candidate.risk_controls_present,
        "stop_loss_required": candidate.stop_loss_required,
        "take_profit_required": candidate.take_profit_required,
        "kill_switch_clear": candidate.kill_switch_clear,
        "daily_loss_limit_clear": candidate.daily_loss_limit_clear,
    }


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
