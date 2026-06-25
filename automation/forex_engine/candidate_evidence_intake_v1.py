"""Local-only Forex candidate evidence intake for AI_OS.

This module normalizes candidate evidence for review. It does not read
credentials, read .env files, call brokers, place orders, start automation, or
enable live trading.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Any, Mapping


getcontext().prec = 28

CANDIDATE_EVIDENCE_REVIEW_READY = "CANDIDATE_EVIDENCE_REVIEW_READY"
CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY = (
    "CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY"
)
CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS = (
    "CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS"
)
CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS = (
    "CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS"
)
CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE = (
    "CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE"
)
CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY = (
    "CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY"
)
CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR = (
    "CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR"
)
CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN = (
    "CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN"
)
CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD = (
    "CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD"
)
CANDIDATE_EVIDENCE_BLOCKED_RISK_CONTROLS = (
    "CANDIDATE_EVIDENCE_BLOCKED_RISK_CONTROLS"
)

VALID_CLASSIFICATIONS = {
    CANDIDATE_EVIDENCE_REVIEW_READY,
    CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY,
    CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS,
    CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS,
    CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE,
    CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY,
    CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR,
    CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN,
    CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD,
    CANDIDATE_EVIDENCE_BLOCKED_RISK_CONTROLS,
}

INCOMPLETE_SAMPLE_OPERATOR_ANSWER = (
    "Candidate evidence is not review-ready. Identity and proof metrics are "
    "incomplete, profit is not proven, and no next demo trade, real money, or "
    "compounding is allowed."
)

IDENTITY_FIELDS = (
    "candidate_id",
    "strategy_name",
    "symbol",
    "direction",
    "timeframe",
    "evidence_source",
)
METRIC_FIELDS = (
    "total_trades",
    "wins",
    "losses",
    "realized_pl_total",
    "expectancy",
    "profit_factor",
    "max_drawdown",
    "consecutive_losses",
    "average_win",
    "average_loss",
)
PROOF_GATE_FIELDS = (
    "sample_depth_sufficient",
    "walk_forward_gate_cleared",
    "risk_controls_present",
    "stop_loss_required",
    "take_profit_required",
    "kill_switch_clear",
    "daily_loss_limit_clear",
)
PERMISSION_FIELDS = (
    "candidate_review_allowed",
    "next_demo_trade_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "broker_action_allowed",
    "live_trading_allowed",
    "owner_approval_required",
)


@dataclass(frozen=True)
class CandidateEvidenceIntakeConfig:
    """Thresholds used when deciding whether candidate evidence is review-ready."""

    minimum_sample_size: int = 20
    minimum_profit_factor: Decimal | str | int | float = Decimal("1.25")
    maximum_drawdown: Decimal | str | int | float = Decimal("0.05")
    maximum_consecutive_losses: int = 3

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "minimum_sample_size", _to_non_negative_int(self.minimum_sample_size)
        )
        object.__setattr__(
            self, "minimum_profit_factor", _to_decimal(self.minimum_profit_factor)
        )
        object.__setattr__(
            self, "maximum_drawdown", _to_decimal(self.maximum_drawdown)
        )
        object.__setattr__(
            self,
            "maximum_consecutive_losses",
            _to_non_negative_int(self.maximum_consecutive_losses),
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CandidateEvidenceIntakeConfig":
        return cls(
            minimum_sample_size=raw.get("minimum_sample_size", cls.minimum_sample_size),
            minimum_profit_factor=raw.get(
                "minimum_profit_factor", cls.minimum_profit_factor
            ),
            maximum_drawdown=raw.get(
                "maximum_drawdown",
                raw.get("maximum_drawdown_allowed", cls.maximum_drawdown),
            ),
            maximum_consecutive_losses=raw.get(
                "maximum_consecutive_losses",
                raw.get(
                    "maximum_consecutive_losses_allowed",
                    cls.maximum_consecutive_losses,
                ),
            ),
        )


@dataclass(frozen=True)
class RawCandidateEvidence:
    """Raw candidate evidence before deterministic normalization."""

    candidate_id: Any = None
    strategy_name: Any = None
    symbol: Any = None
    direction: Any = None
    timeframe: Any = None
    evidence_source: Any = None
    total_trades: Any = None
    wins: Any = None
    losses: Any = None
    realized_pl_total: Any = None
    expectancy: Any = None
    profit_factor: Any = None
    max_drawdown: Any = None
    consecutive_losses: Any = None
    average_win: Any = None
    average_loss: Any = None
    sample_depth_sufficient: Any = None
    walk_forward_gate_cleared: Any = None
    risk_controls_present: Any = None
    stop_loss_required: Any = None
    take_profit_required: Any = None
    kill_switch_clear: Any = None
    daily_loss_limit_clear: Any = None
    candidate_review_allowed: Any = None
    next_demo_trade_allowed: Any = None
    real_money_allowed: Any = None
    compounding_allowed: Any = None
    broker_action_allowed: Any = None
    live_trading_allowed: Any = None
    owner_approval_required: Any = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "RawCandidateEvidence":
        return cls(
            candidate_id=raw.get("candidate_id"),
            strategy_name=raw.get("strategy_name"),
            symbol=raw.get("symbol"),
            direction=raw.get("direction"),
            timeframe=raw.get("timeframe"),
            evidence_source=raw.get("evidence_source"),
            total_trades=raw.get("total_trades"),
            wins=raw.get("wins"),
            losses=raw.get("losses"),
            realized_pl_total=raw.get("realized_pl_total"),
            expectancy=raw.get("expectancy"),
            profit_factor=raw.get("profit_factor"),
            max_drawdown=raw.get("max_drawdown"),
            consecutive_losses=raw.get("consecutive_losses"),
            average_win=raw.get("average_win"),
            average_loss=raw.get("average_loss"),
            sample_depth_sufficient=raw.get("sample_depth_sufficient"),
            walk_forward_gate_cleared=raw.get("walk_forward_gate_cleared"),
            risk_controls_present=raw.get("risk_controls_present"),
            stop_loss_required=raw.get("stop_loss_required"),
            take_profit_required=raw.get("take_profit_required"),
            kill_switch_clear=raw.get("kill_switch_clear"),
            daily_loss_limit_clear=raw.get("daily_loss_limit_clear"),
            candidate_review_allowed=raw.get("candidate_review_allowed"),
            next_demo_trade_allowed=raw.get("next_demo_trade_allowed"),
            real_money_allowed=raw.get("real_money_allowed"),
            compounding_allowed=raw.get("compounding_allowed"),
            broker_action_allowed=raw.get("broker_action_allowed"),
            live_trading_allowed=raw.get("live_trading_allowed"),
            owner_approval_required=raw.get("owner_approval_required"),
        )


@dataclass(frozen=True)
class NormalizedCandidateEvidence:
    """Candidate evidence after deterministic defaulting and type coercion."""

    candidate_id: str = "NONE"
    strategy_name: str = "UNKNOWN"
    symbol: str = "UNKNOWN"
    direction: str = "UNKNOWN"
    timeframe: str = "UNKNOWN"
    evidence_source: str = "UNKNOWN"
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    realized_pl_total: Decimal = Decimal("0")
    expectancy: Decimal = Decimal("0")
    profit_factor: Decimal = Decimal("0")
    max_drawdown: Decimal = Decimal("0")
    consecutive_losses: int = 0
    average_win: Decimal = Decimal("0")
    average_loss: Decimal = Decimal("0")
    sample_depth_sufficient: bool = False
    walk_forward_gate_cleared: bool = False
    risk_controls_present: bool = False
    stop_loss_required: bool = False
    take_profit_required: bool = False
    kill_switch_clear: bool = False
    daily_loss_limit_clear: bool = False
    candidate_review_allowed: bool = False
    next_demo_trade_allowed: bool = False
    real_money_allowed: bool = False
    compounding_allowed: bool = False
    broker_action_allowed: bool = False
    live_trading_allowed: bool = False
    owner_approval_required: bool = True
    missing_fields: tuple[str, ...] = field(default_factory=tuple)
    invalid_fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CandidateEvidenceIntakeResult:
    """Operator-facing result of candidate evidence intake."""

    classification: str
    candidate_evidence_present: bool
    structurally_valid: bool
    complete_enough_for_review: bool
    candidate_review_allowed: bool
    next_demo_trade_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    broker_action_allowed: bool
    live_trading_allowed: bool
    owner_approval_required: bool
    operator_answer: str
    blockers: tuple[str, ...]
    missing_fields: tuple[str, ...]
    usable_metrics: Mapping[str, Any]
    normalized_candidate: NormalizedCandidateEvidence
    permissions: Mapping[str, bool]
    next_safe_action: str

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification}")


def build_sample_incomplete_candidate() -> RawCandidateEvidence:
    """Return the intentionally incomplete trade-334-context candidate."""

    return RawCandidateEvidence(
        candidate_id="NONE",
        strategy_name="UNKNOWN",
        symbol="EUR_USD",
        direction="UNKNOWN",
        timeframe="UNKNOWN",
        evidence_source="trade_334_loss_context",
        total_trades=1,
        wins=0,
        losses=1,
        realized_pl_total=Decimal("-0.0010"),
        expectancy=Decimal("-0.0010"),
        profit_factor=Decimal("0"),
        max_drawdown=Decimal("0.0010"),
        consecutive_losses=1,
        sample_depth_sufficient=False,
        walk_forward_gate_cleared=False,
        risk_controls_present=True,
        stop_loss_required=True,
        take_profit_required=True,
        kill_switch_clear=True,
        daily_loss_limit_clear=True,
    )


def build_sample_review_ready_candidate() -> RawCandidateEvidence:
    """Return a synthetic candidate that is review-ready but not trade-approved."""

    return RawCandidateEvidence(
        candidate_id="c1-eur-buy-review-ready",
        strategy_name="paper_long_run_supervisor_v2",
        symbol="EUR_USD",
        direction="LONG",
        timeframe="DEMO_REVIEW",
        evidence_source="synthetic_review_ready_sample",
        total_trades=25,
        wins=16,
        losses=9,
        realized_pl_total=Decimal("12.50"),
        expectancy=Decimal("0.50"),
        profit_factor=Decimal("1.60"),
        max_drawdown=Decimal("0.025"),
        consecutive_losses=2,
        average_win=Decimal("1.20"),
        average_loss=Decimal("-0.75"),
        sample_depth_sufficient=True,
        walk_forward_gate_cleared=True,
        risk_controls_present=True,
        stop_loss_required=True,
        take_profit_required=True,
        kill_switch_clear=True,
        daily_loss_limit_clear=True,
    )


def normalize_candidate_evidence(
    evidence: RawCandidateEvidence | NormalizedCandidateEvidence | Mapping[str, Any] | None,
) -> NormalizedCandidateEvidence:
    """Normalize raw evidence while preserving missing and invalid field evidence."""

    if isinstance(evidence, NormalizedCandidateEvidence):
        return evidence
    raw = _coerce_raw(evidence)
    missing_fields: list[str] = []
    invalid_fields: list[str] = []

    return NormalizedCandidateEvidence(
        candidate_id=_to_string(
            raw.candidate_id,
            field_name="candidate_id",
            default="NONE",
            missing_fields=missing_fields,
        ),
        strategy_name=_to_string(
            raw.strategy_name,
            field_name="strategy_name",
            default="UNKNOWN",
            missing_fields=missing_fields,
        ),
        symbol=_to_string(
            raw.symbol,
            field_name="symbol",
            default="UNKNOWN",
            missing_fields=missing_fields,
        ),
        direction=_to_string(
            raw.direction,
            field_name="direction",
            default="UNKNOWN",
            missing_fields=missing_fields,
        ),
        timeframe=_to_string(
            raw.timeframe,
            field_name="timeframe",
            default="UNKNOWN",
            missing_fields=missing_fields,
        ),
        evidence_source=_to_string(
            raw.evidence_source,
            field_name="evidence_source",
            default="UNKNOWN",
            missing_fields=missing_fields,
        ),
        total_trades=_to_int_or_default(
            raw.total_trades,
            field_name="total_trades",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        wins=_to_int_or_default(
            raw.wins,
            field_name="wins",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        losses=_to_int_or_default(
            raw.losses,
            field_name="losses",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        realized_pl_total=_to_decimal_or_default(
            raw.realized_pl_total,
            field_name="realized_pl_total",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        expectancy=_to_decimal_or_default(
            raw.expectancy,
            field_name="expectancy",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        profit_factor=_to_decimal_or_default(
            raw.profit_factor,
            field_name="profit_factor",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        max_drawdown=abs(
            _to_decimal_or_default(
                raw.max_drawdown,
                field_name="max_drawdown",
                missing_fields=missing_fields,
                invalid_fields=invalid_fields,
            )
        ),
        consecutive_losses=_to_int_or_default(
            raw.consecutive_losses,
            field_name="consecutive_losses",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        average_win=_to_decimal_or_default(
            raw.average_win,
            field_name="average_win",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        average_loss=_to_decimal_or_default(
            raw.average_loss,
            field_name="average_loss",
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        sample_depth_sufficient=_to_bool_or_default(
            raw.sample_depth_sufficient,
            field_name="sample_depth_sufficient",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        walk_forward_gate_cleared=_to_bool_or_default(
            raw.walk_forward_gate_cleared,
            field_name="walk_forward_gate_cleared",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        risk_controls_present=_to_bool_or_default(
            raw.risk_controls_present,
            field_name="risk_controls_present",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        stop_loss_required=_to_bool_or_default(
            raw.stop_loss_required,
            field_name="stop_loss_required",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        take_profit_required=_to_bool_or_default(
            raw.take_profit_required,
            field_name="take_profit_required",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        kill_switch_clear=_to_bool_or_default(
            raw.kill_switch_clear,
            field_name="kill_switch_clear",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        daily_loss_limit_clear=_to_bool_or_default(
            raw.daily_loss_limit_clear,
            field_name="daily_loss_limit_clear",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        candidate_review_allowed=_to_bool_or_default(
            raw.candidate_review_allowed,
            field_name="candidate_review_allowed",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        next_demo_trade_allowed=_to_bool_or_default(
            raw.next_demo_trade_allowed,
            field_name="next_demo_trade_allowed",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        real_money_allowed=_to_bool_or_default(
            raw.real_money_allowed,
            field_name="real_money_allowed",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        compounding_allowed=_to_bool_or_default(
            raw.compounding_allowed,
            field_name="compounding_allowed",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        broker_action_allowed=_to_bool_or_default(
            raw.broker_action_allowed,
            field_name="broker_action_allowed",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        live_trading_allowed=_to_bool_or_default(
            raw.live_trading_allowed,
            field_name="live_trading_allowed",
            default=False,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        owner_approval_required=_to_bool_or_default(
            raw.owner_approval_required,
            field_name="owner_approval_required",
            default=True,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
        ),
        missing_fields=tuple(missing_fields),
        invalid_fields=tuple(invalid_fields),
    )


def evaluate_candidate_evidence_intake(
    evidence: RawCandidateEvidence | NormalizedCandidateEvidence | Mapping[str, Any] | None = None,
    config: CandidateEvidenceIntakeConfig | Mapping[str, Any] | None = None,
) -> CandidateEvidenceIntakeResult:
    """Evaluate whether candidate evidence is ready for review only."""

    active_config = _coerce_config(config)
    normalized = normalize_candidate_evidence(evidence)
    candidate_evidence_present = _candidate_evidence_present(evidence, normalized)
    blockers: list[str] = []

    classification, blockers = _classify(normalized, active_config)
    structurally_valid = (
        not normalized.invalid_fields
        and normalized.wins + normalized.losses <= normalized.total_trades
    )
    candidate_review_allowed = classification == CANDIDATE_EVIDENCE_REVIEW_READY
    complete_enough_for_review = candidate_review_allowed
    permissions = {
        "candidate_review_allowed": candidate_review_allowed,
        "next_demo_trade_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "broker_action_allowed": False,
        "live_trading_allowed": False,
        "owner_approval_required": True,
    }

    return CandidateEvidenceIntakeResult(
        classification=classification,
        candidate_evidence_present=candidate_evidence_present,
        structurally_valid=structurally_valid,
        complete_enough_for_review=complete_enough_for_review,
        candidate_review_allowed=candidate_review_allowed,
        next_demo_trade_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        broker_action_allowed=False,
        live_trading_allowed=False,
        owner_approval_required=True,
        operator_answer=_operator_answer(classification),
        blockers=tuple(blockers),
        missing_fields=normalized.missing_fields,
        usable_metrics=_usable_metrics(normalized),
        normalized_candidate=normalized,
        permissions=permissions,
        next_safe_action=_next_safe_action(classification),
    )


def result_to_operator_text(result: CandidateEvidenceIntakeResult) -> str:
    """Format deterministic operator-readable output."""

    lines = [
        "AIOS Forex Candidate Evidence Intake V1",
        f"classification: {result.classification}",
        f"candidate_evidence_present: {_bool_text(result.candidate_evidence_present)}",
        f"structurally_valid: {_bool_text(result.structurally_valid)}",
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
    lines.extend(
        [
            "normalized_candidate:",
            f"- candidate_id: {result.normalized_candidate.candidate_id}",
            f"- strategy_name: {result.normalized_candidate.strategy_name}",
            f"- symbol: {result.normalized_candidate.symbol}",
            f"- direction: {result.normalized_candidate.direction}",
            f"- timeframe: {result.normalized_candidate.timeframe}",
            f"- total_trades: {result.normalized_candidate.total_trades}",
            f"- expectancy: {_json_value(result.normalized_candidate.expectancy)}",
            f"- profit_factor: {_json_value(result.normalized_candidate.profit_factor)}",
            f"- max_drawdown: {_json_value(result.normalized_candidate.max_drawdown)}",
            "missing_fields:",
        ]
    )
    if result.missing_fields:
        lines.extend(f"- {field_name}" for field_name in result.missing_fields)
    else:
        lines.append("- none")
    lines.append(f"next_safe_action: {result.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: CandidateEvidenceIntakeResult) -> dict[str, Any]:
    """Return deterministic JSON-safe result data."""

    return {
        "classification": result.classification,
        "candidate_evidence_present": result.candidate_evidence_present,
        "structurally_valid": result.structurally_valid,
        "complete_enough_for_review": result.complete_enough_for_review,
        "blockers": list(result.blockers),
        "missing_fields": list(result.missing_fields),
        "usable_metrics": _jsonable_mapping(result.usable_metrics),
        "normalized_candidate": _normalized_to_jsonable(result.normalized_candidate),
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


def _coerce_raw(
    evidence: RawCandidateEvidence | Mapping[str, Any] | None,
) -> RawCandidateEvidence:
    if isinstance(evidence, RawCandidateEvidence):
        return evidence
    if evidence is None:
        return RawCandidateEvidence()
    if isinstance(evidence, Mapping):
        candidate_raw = evidence.get("candidate", evidence.get("candidate_evidence", evidence))
        if not isinstance(candidate_raw, Mapping):
            candidate_raw = {}
        return RawCandidateEvidence.from_mapping(candidate_raw)
    raise TypeError("unsupported candidate evidence input")


def _coerce_config(
    config: CandidateEvidenceIntakeConfig | Mapping[str, Any] | None,
) -> CandidateEvidenceIntakeConfig:
    if isinstance(config, CandidateEvidenceIntakeConfig):
        return config
    if isinstance(config, Mapping):
        return CandidateEvidenceIntakeConfig.from_mapping(config)
    return CandidateEvidenceIntakeConfig()


def _classify(
    candidate: NormalizedCandidateEvidence,
    config: CandidateEvidenceIntakeConfig,
) -> tuple[str, list[str]]:
    identity_blockers = _identity_blockers(candidate)
    if identity_blockers:
        return CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY, identity_blockers

    metric_missing = [field_name for field_name in METRIC_FIELDS if field_name in candidate.missing_fields]
    if metric_missing:
        return (
            CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS,
            [f"candidate metric {field_name} is missing" for field_name in metric_missing],
        )

    metric_blockers = _metric_blockers(candidate)
    if metric_blockers:
        return CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS, metric_blockers

    if candidate.total_trades < config.minimum_sample_size:
        return (
            CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE,
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
            CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE,
            ["candidate sample depth is not sufficient"],
        )
    if candidate.expectancy <= Decimal("0"):
        return (
            CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY,
            [f"candidate expectancy {candidate.expectancy} is not positive"],
        )
    if candidate.profit_factor < config.minimum_profit_factor:
        return (
            CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR,
            [
                (
                    f"candidate profit factor {candidate.profit_factor} below "
                    f"minimum {config.minimum_profit_factor}"
                )
            ],
        )
    if candidate.max_drawdown > config.maximum_drawdown:
        return (
            CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN,
            [
                (
                    f"candidate max drawdown {candidate.max_drawdown} exceeds "
                    f"maximum {config.maximum_drawdown}"
                )
            ],
        )
    if not candidate.walk_forward_gate_cleared:
        return (
            CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD,
            ["candidate walk-forward gate is not cleared"],
        )

    risk_blockers = _risk_blockers(candidate, config)
    if risk_blockers:
        return CANDIDATE_EVIDENCE_BLOCKED_RISK_CONTROLS, risk_blockers

    return CANDIDATE_EVIDENCE_REVIEW_READY, []


def _identity_blockers(candidate: NormalizedCandidateEvidence) -> list[str]:
    blockers: list[str] = []
    if candidate.candidate_id.strip().upper() in {"", "NONE", "UNKNOWN"}:
        blockers.append("candidate_id is missing")
    for field_name in IDENTITY_FIELDS[1:]:
        value = str(getattr(candidate, field_name)).strip().upper()
        if value in {"", "NONE", "UNKNOWN"}:
            blockers.append(f"{field_name} is missing")
    return blockers


def _metric_blockers(candidate: NormalizedCandidateEvidence) -> list[str]:
    blockers = [f"candidate metric {field_name} is invalid" for field_name in candidate.invalid_fields if field_name in METRIC_FIELDS]
    if candidate.wins + candidate.losses > candidate.total_trades:
        blockers.append("wins plus losses exceed total trades")
    if candidate.profit_factor < Decimal("0"):
        blockers.append("profit factor is negative")
    if candidate.average_win < Decimal("0"):
        blockers.append("average win is negative")
    return blockers


def _risk_blockers(
    candidate: NormalizedCandidateEvidence,
    config: CandidateEvidenceIntakeConfig,
) -> list[str]:
    blockers: list[str] = []
    if candidate.consecutive_losses > config.maximum_consecutive_losses:
        blockers.append(
            (
                "candidate consecutive losses "
                f"{candidate.consecutive_losses} exceed maximum "
                f"{config.maximum_consecutive_losses}"
            )
        )
    if not candidate.risk_controls_present:
        blockers.append("candidate risk controls are missing")
    if not candidate.stop_loss_required:
        blockers.append("candidate stop loss requirement is missing")
    if not candidate.take_profit_required:
        blockers.append("candidate take profit requirement is missing")
    if not candidate.kill_switch_clear:
        blockers.append("candidate kill switch is not clear")
    if not candidate.daily_loss_limit_clear:
        blockers.append("candidate daily loss limit is not clear")
    if candidate.next_demo_trade_allowed:
        blockers.append("next demo trade permission must stay disabled")
    if candidate.real_money_allowed:
        blockers.append("real money permission must stay disabled")
    if candidate.compounding_allowed:
        blockers.append("compounding permission must stay disabled")
    if candidate.broker_action_allowed:
        blockers.append("broker action permission must stay disabled")
    if candidate.live_trading_allowed:
        blockers.append("live trading permission must stay disabled")
    if not candidate.owner_approval_required:
        blockers.append("owner approval requirement is not recorded")
    return blockers


def _operator_answer(classification: str) -> str:
    if classification == CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY:
        return INCOMPLETE_SAMPLE_OPERATOR_ANSWER
    if classification == CANDIDATE_EVIDENCE_REVIEW_READY:
        return (
            "Candidate evidence is review-ready for operator/gate review only. "
            "No next demo trade, real money, broker action, live trading, or "
            "compounding is allowed by this intake."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS:
        return (
            "Candidate evidence is not review-ready. Required proof metrics are "
            "missing, so no next demo trade, real money, or compounding is allowed."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS:
        return (
            "Candidate evidence is not structurally valid. Metric relationships "
            "must be repaired before review."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE:
        return (
            "Candidate evidence is not review-ready. Sample depth is insufficient, "
            "so no next demo trade, real money, or compounding is allowed."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY:
        return (
            "Candidate evidence is not review-ready. Expectancy is not positive, "
            "so profit is not proven."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR:
        return (
            "Candidate evidence is not review-ready. Profit factor is below the "
            "configured threshold."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN:
        return (
            "Candidate evidence is not review-ready. Drawdown is above the "
            "configured limit."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD:
        return (
            "Candidate evidence is not review-ready. Walk-forward proof is not "
            "cleared."
        )
    return (
        "Candidate evidence is not review-ready. Risk controls or protected "
        "permissions are not clear."
    )


def _next_safe_action(classification: str) -> str:
    if classification == CANDIDATE_EVIDENCE_REVIEW_READY:
        return (
            "Send the candidate to next-profit-candidate review; do not place a "
            "trade or enable real money."
        )
    if classification == CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY:
        return "Record candidate identity and complete proof metrics before review."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS:
        return "Add the missing candidate metrics before review."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS:
        return "Repair invalid metric relationships before review."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE:
        return "Collect deeper demo evidence before candidate review."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY:
        return "Keep searching in demo until expectancy is positive."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR:
        return "Keep searching in demo until profit factor clears the threshold."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN:
        return "Reduce candidate drawdown before review."
    if classification == CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD:
        return "Complete walk-forward proof before review."
    return "Repair candidate risk-control evidence before review."


def _candidate_evidence_present(
    raw: RawCandidateEvidence | NormalizedCandidateEvidence | Mapping[str, Any] | None,
    normalized: NormalizedCandidateEvidence,
) -> bool:
    if raw is None:
        return False
    if isinstance(raw, Mapping):
        candidate_raw = raw.get("candidate", raw.get("candidate_evidence", raw))
        return isinstance(candidate_raw, Mapping) and any(
            not _is_missing(value) for value in candidate_raw.values()
        )
    return any(
        str(getattr(normalized, field_name)).strip().upper()
        not in {"", "NONE", "UNKNOWN", "0", "FALSE"}
        for field_name in IDENTITY_FIELDS + METRIC_FIELDS + PROOF_GATE_FIELDS
    )


def _usable_metrics(candidate: NormalizedCandidateEvidence) -> dict[str, Any]:
    blocked_fields = set(candidate.missing_fields) | set(candidate.invalid_fields)
    return {
        field_name: getattr(candidate, field_name)
        for field_name in METRIC_FIELDS
        if field_name not in blocked_fields
    }


def _normalized_to_jsonable(candidate: NormalizedCandidateEvidence) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "strategy_name": candidate.strategy_name,
        "symbol": candidate.symbol,
        "direction": candidate.direction,
        "timeframe": candidate.timeframe,
        "evidence_source": candidate.evidence_source,
        "total_trades": candidate.total_trades,
        "wins": candidate.wins,
        "losses": candidate.losses,
        "realized_pl_total": _json_value(candidate.realized_pl_total),
        "expectancy": _json_value(candidate.expectancy),
        "profit_factor": _json_value(candidate.profit_factor),
        "max_drawdown": _json_value(candidate.max_drawdown),
        "consecutive_losses": candidate.consecutive_losses,
        "average_win": _json_value(candidate.average_win),
        "average_loss": _json_value(candidate.average_loss),
        "sample_depth_sufficient": candidate.sample_depth_sufficient,
        "walk_forward_gate_cleared": candidate.walk_forward_gate_cleared,
        "risk_controls_present": candidate.risk_controls_present,
        "stop_loss_required": candidate.stop_loss_required,
        "take_profit_required": candidate.take_profit_required,
        "kill_switch_clear": candidate.kill_switch_clear,
        "daily_loss_limit_clear": candidate.daily_loss_limit_clear,
        "candidate_review_allowed": candidate.candidate_review_allowed,
        "next_demo_trade_allowed": candidate.next_demo_trade_allowed,
        "real_money_allowed": candidate.real_money_allowed,
        "compounding_allowed": candidate.compounding_allowed,
        "broker_action_allowed": candidate.broker_action_allowed,
        "live_trading_allowed": candidate.live_trading_allowed,
        "owner_approval_required": candidate.owner_approval_required,
        "missing_fields": list(candidate.missing_fields),
        "invalid_fields": list(candidate.invalid_fields),
    }


def _to_string(
    value: Any,
    *,
    field_name: str,
    default: str,
    missing_fields: list[str],
) -> str:
    if _is_missing(value):
        missing_fields.append(field_name)
        return default
    return str(value).strip()


def _to_decimal_or_default(
    value: Any,
    *,
    field_name: str,
    missing_fields: list[str],
    invalid_fields: list[str],
) -> Decimal:
    if _is_missing(value):
        missing_fields.append(field_name)
        return Decimal("0")
    try:
        parsed = _to_decimal(value)
    except ValueError:
        invalid_fields.append(field_name)
        return Decimal("0")
    return parsed


def _to_int_or_default(
    value: Any,
    *,
    field_name: str,
    missing_fields: list[str],
    invalid_fields: list[str],
) -> int:
    if _is_missing(value):
        missing_fields.append(field_name)
        return 0
    try:
        parsed = _to_non_negative_int(value)
    except (TypeError, ValueError):
        invalid_fields.append(field_name)
        return 0
    return parsed


def _to_bool_or_default(
    value: Any,
    *,
    field_name: str,
    default: bool,
    missing_fields: list[str],
    invalid_fields: list[str],
) -> bool:
    if _is_missing(value):
        missing_fields.append(field_name)
        return default
    try:
        return _to_bool(value)
    except ValueError:
        invalid_fields.append(field_name)
        return default


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


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


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
