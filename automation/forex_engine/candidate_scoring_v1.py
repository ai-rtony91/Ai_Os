"""Deterministic local scoring for Forex review-ready candidates.

The scorer ranks local candidate dictionaries before supervised demo review.
It performs no file reads, network calls, broker calls, credential access,
account lookup, order placement, scheduling, or runtime mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


CANDIDATE_SCORING_VERSION = "candidate_scoring_v1"

REVIEW_READY = "REVIEW_READY"
REQUIRE_MORE_EVIDENCE = "REQUIRE_MORE_EVIDENCE"
REJECT = "REJECT"
BLOCKED_BY_RISK = "BLOCKED_BY_RISK"
BLOCKED_BY_EVIDENCE = "BLOCKED_BY_EVIDENCE"
BLOCKED_BY_DEMO_READINESS = "BLOCKED_BY_DEMO_READINESS"

VALID_DECISIONS = frozenset(
    (
        REVIEW_READY,
        REQUIRE_MORE_EVIDENCE,
        REJECT,
        BLOCKED_BY_RISK,
        BLOCKED_BY_EVIDENCE,
        BLOCKED_BY_DEMO_READINESS,
    )
)

SCORE_DIMENSIONS = (
    "expectancy_score",
    "profit_factor_score",
    "drawdown_score",
    "sample_size_score",
    "recency_score",
    "regime_alignment_score",
    "risk_quality_score",
    "evidence_quality_score",
    "demo_readiness_score",
    "operator_confidence_score",
)

DEFAULT_DIMENSION_WEIGHTS = {
    "expectancy_score": Decimal("0.16"),
    "profit_factor_score": Decimal("0.12"),
    "drawdown_score": Decimal("0.12"),
    "sample_size_score": Decimal("0.10"),
    "recency_score": Decimal("0.08"),
    "regime_alignment_score": Decimal("0.10"),
    "risk_quality_score": Decimal("0.12"),
    "evidence_quality_score": Decimal("0.08"),
    "demo_readiness_score": Decimal("0.07"),
    "operator_confidence_score": Decimal("0.05"),
}

DECISION_PRIORITY = {
    REVIEW_READY: 0,
    REQUIRE_MORE_EVIDENCE: 1,
    BLOCKED_BY_DEMO_READINESS: 2,
    BLOCKED_BY_EVIDENCE: 3,
    BLOCKED_BY_RISK: 4,
    REJECT: 5,
}

SAFETY_FLAGS = {
    "network_used": False,
    "broker_called": False,
    "credentials_read": False,
    "account_ids_read": False,
    "orders_placed": False,
    "demo_execution_allowed": False,
    "live_trading_allowed": False,
    "autonomous_runtime_started": False,
}


@dataclass(frozen=True)
class CandidateScoringConfig:
    """Thresholds used by the deterministic candidate scoring engine."""

    review_ready_threshold: Decimal = Decimal("75")
    min_sample_size: int = 30
    target_expectancy: Decimal = Decimal("0.50")
    target_profit_factor: Decimal = Decimal("2.00")
    excellent_drawdown: Decimal = Decimal("0.02")
    max_drawdown_allowed: Decimal = Decimal("0.15")
    fresh_evidence_days: Decimal = Decimal("7")
    stale_evidence_days: Decimal = Decimal("30")


@dataclass(frozen=True)
class CandidateScoreResult:
    """Scored candidate result returned by the engine."""

    candidate_id: str
    total_score: float
    normalized_score: float
    rank: int
    decision: str
    decision_reasons: tuple[str, ...]
    blockers: tuple[str, ...]
    score_breakdown: Mapping[str, float]
    recommended_next_action: str

    def __post_init__(self) -> None:
        if self.decision not in VALID_DECISIONS:
            raise ValueError(f"invalid decision: {self.decision}")
        missing = [name for name in SCORE_DIMENSIONS if name not in self.score_breakdown]
        if missing:
            raise ValueError(f"score_breakdown missing dimensions: {missing}")
        if not self.decision_reasons:
            raise ValueError("decision_reasons must not be empty")


def score_candidates(
    candidates: Sequence[Mapping[str, Any]] | None,
    *,
    config: CandidateScoringConfig | None = None,
) -> list[CandidateScoreResult]:
    """Score and rank candidate dictionaries.

    Invalid or empty input returns an empty list. Ranking is deterministic:
    decision priority, higher normalized score, higher total score, then
    lexicographically smallest candidate ID.
    """

    active_config = config or CandidateScoringConfig()
    if not candidates:
        return []

    results: list[CandidateScoreResult] = []
    for index, candidate in enumerate(candidates):
        if isinstance(candidate, Mapping):
            results.append(
                score_candidate(candidate, config=active_config, input_index=index)
            )

    ranked = sorted(results, key=_ranking_key)
    return [replace(result, rank=rank) for rank, result in enumerate(ranked, 1)]


def score_candidate(
    candidate: Mapping[str, Any],
    *,
    config: CandidateScoringConfig | None = None,
    input_index: int = 0,
) -> CandidateScoreResult:
    """Score one candidate without assigning final list rank."""

    active_config = config or CandidateScoringConfig()
    candidate_id = _candidate_id(candidate, input_index)
    metrics = _extract_metrics(candidate)
    breakdown = _score_breakdown(metrics, active_config)
    total = _weighted_total(breakdown)
    normalized = _clamp_decimal(total)
    decision, reasons, blockers = _classify_candidate(
        metrics,
        normalized,
        active_config,
    )
    return CandidateScoreResult(
        candidate_id=candidate_id,
        total_score=_decimal_float(total),
        normalized_score=_decimal_float(normalized),
        rank=0,
        decision=decision,
        decision_reasons=tuple(reasons),
        blockers=tuple(blockers),
        score_breakdown={key: _decimal_float(value) for key, value in breakdown.items()},
        recommended_next_action=_recommended_next_action(decision),
    )


def candidate_score_to_jsonable_dict(result: CandidateScoreResult) -> dict[str, Any]:
    """Return a deterministic JSON-safe score result."""

    return {
        "candidate_id": result.candidate_id,
        "total_score": result.total_score,
        "normalized_score": result.normalized_score,
        "rank": result.rank,
        "decision": result.decision,
        "decision_reasons": list(result.decision_reasons),
        "blockers": list(result.blockers),
        "score_breakdown": dict(result.score_breakdown),
        "recommended_next_action": result.recommended_next_action,
        "safety": dict(SAFETY_FLAGS),
    }


def candidate_scores_to_jsonable_dict(
    results: Sequence[CandidateScoreResult],
) -> dict[str, Any]:
    """Return a JSON-safe ranked result envelope."""

    return {
        "engine_version": CANDIDATE_SCORING_VERSION,
        "candidate_count": len(results),
        "results": [candidate_score_to_jsonable_dict(result) for result in results],
        "safety": dict(SAFETY_FLAGS),
    }


def _candidate_id(candidate: Mapping[str, Any], input_index: int) -> str:
    raw = _text(_first(candidate, "candidate_id", "id"))
    return raw if raw else f"candidate-{input_index:06d}"


def _extract_metrics(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "expectancy": _decimal_or_none(candidate.get("expectancy")),
        "profit_factor": _decimal_or_none(candidate.get("profit_factor")),
        "max_drawdown": _decimal_or_none(
            _first(candidate, "max_drawdown", "drawdown")
        ),
        "sample_size": _int_or_none(
            _first(candidate, "sample_size", "total_trades", "closed_trade_count")
        ),
        "evidence_age_days": _decimal_or_none(
            _first(candidate, "evidence_age_days", "age_days", "recency_days")
        ),
        "expectancy_score": _score_or_none(candidate.get("expectancy_score")),
        "profit_factor_score": _score_or_none(candidate.get("profit_factor_score")),
        "drawdown_score": _score_or_none(candidate.get("drawdown_score")),
        "sample_size_score": _score_or_none(candidate.get("sample_size_score")),
        "recency_score": _score_or_none(candidate.get("recency_score")),
        "regime_alignment_score": _score_or_none(
            _first(candidate, "regime_alignment_score", "regime_score")
        ),
        "risk_quality_score": _score_or_none(
            _first(candidate, "risk_quality_score", "risk_score")
        ),
        "evidence_quality_score": _score_or_none(
            _first(candidate, "evidence_quality_score", "evidence_score")
        ),
        "demo_readiness_score": _score_or_none(
            _first(candidate, "demo_readiness_score", "demo_score")
        ),
        "operator_confidence_score": _score_or_none(
            _first(candidate, "operator_confidence_score", "confidence_score")
        ),
        "evidence_present": _optional_bool(
            _first(candidate, "evidence_present", "has_evidence")
        ),
        "required_evidence_complete": _optional_bool(
            _first(candidate, "required_evidence_complete", "evidence_complete")
        ),
        "demo_readiness": _optional_bool(
            _first(candidate, "demo_readiness", "demo_ready")
        ),
        "risk_controls_present": _optional_bool(candidate.get("risk_controls_present")),
        "risk_blocked": _truthy(candidate.get("risk_blocked")),
    }


def _score_breakdown(
    metrics: Mapping[str, Any],
    config: CandidateScoringConfig,
) -> dict[str, Decimal]:
    return {
        "expectancy_score": _score_or_derived(
            metrics["expectancy_score"],
            _score_expectancy(metrics["expectancy"], config),
        ),
        "profit_factor_score": _score_or_derived(
            metrics["profit_factor_score"],
            _score_profit_factor(metrics["profit_factor"], config),
        ),
        "drawdown_score": _score_or_derived(
            metrics["drawdown_score"],
            _score_drawdown(metrics["max_drawdown"], config),
        ),
        "sample_size_score": _score_or_derived(
            metrics["sample_size_score"],
            _score_sample_size(metrics["sample_size"], config),
        ),
        "recency_score": _score_or_derived(
            metrics["recency_score"],
            _score_recency(metrics["evidence_age_days"], config),
        ),
        "regime_alignment_score": _score_or_derived(
            metrics["regime_alignment_score"],
            Decimal("0"),
        ),
        "risk_quality_score": _score_or_derived(
            metrics["risk_quality_score"],
            _score_risk_quality(metrics),
        ),
        "evidence_quality_score": _score_or_derived(
            metrics["evidence_quality_score"],
            _score_evidence_quality(metrics),
        ),
        "demo_readiness_score": _score_or_derived(
            metrics["demo_readiness_score"],
            _score_demo_readiness(metrics),
        ),
        "operator_confidence_score": _score_or_derived(
            metrics["operator_confidence_score"],
            Decimal("0"),
        ),
    }


def _score_expectancy(
    expectancy: Decimal | None,
    config: CandidateScoringConfig,
) -> Decimal:
    if expectancy is None or expectancy <= Decimal("0"):
        return Decimal("0")
    return _clamp_decimal((expectancy / config.target_expectancy) * Decimal("100"))


def _score_profit_factor(
    profit_factor: Decimal | None,
    config: CandidateScoringConfig,
) -> Decimal:
    if profit_factor is None or profit_factor <= Decimal("1"):
        return Decimal("0")
    denominator = config.target_profit_factor - Decimal("1")
    return _clamp_decimal(((profit_factor - Decimal("1")) / denominator) * Decimal("100"))


def _score_drawdown(
    max_drawdown: Decimal | None,
    config: CandidateScoringConfig,
) -> Decimal:
    if max_drawdown is None or max_drawdown < Decimal("0"):
        return Decimal("0")
    if max_drawdown <= config.excellent_drawdown:
        return Decimal("100")
    if max_drawdown >= config.max_drawdown_allowed:
        return Decimal("0")
    range_width = config.max_drawdown_allowed - config.excellent_drawdown
    used = max_drawdown - config.excellent_drawdown
    return _clamp_decimal(Decimal("100") - ((used / range_width) * Decimal("100")))


def _score_sample_size(
    sample_size: int | None,
    config: CandidateScoringConfig,
) -> Decimal:
    if sample_size is None or sample_size <= 0:
        return Decimal("0")
    return _clamp_decimal(
        (Decimal(sample_size) / Decimal(config.min_sample_size)) * Decimal("100")
    )


def _score_recency(
    evidence_age_days: Decimal | None,
    config: CandidateScoringConfig,
) -> Decimal:
    if evidence_age_days is None or evidence_age_days < Decimal("0"):
        return Decimal("0")
    if evidence_age_days <= config.fresh_evidence_days:
        return Decimal("100")
    if evidence_age_days >= config.stale_evidence_days:
        return Decimal("0")
    range_width = config.stale_evidence_days - config.fresh_evidence_days
    used = evidence_age_days - config.fresh_evidence_days
    return _clamp_decimal(Decimal("100") - ((used / range_width) * Decimal("100")))


def _score_risk_quality(metrics: Mapping[str, Any]) -> Decimal:
    risk_controls_present = metrics["risk_controls_present"]
    if risk_controls_present is True:
        return Decimal("100")
    if risk_controls_present is False:
        return Decimal("0")
    return Decimal("0")


def _score_evidence_quality(metrics: Mapping[str, Any]) -> Decimal:
    if metrics["required_evidence_complete"] is True:
        return Decimal("100")
    if metrics["evidence_present"] is True:
        return Decimal("75")
    return Decimal("0")


def _score_demo_readiness(metrics: Mapping[str, Any]) -> Decimal:
    if metrics["demo_readiness"] is True:
        return Decimal("100")
    if metrics["demo_readiness"] is False:
        return Decimal("0")
    return Decimal("0")


def _weighted_total(breakdown: Mapping[str, Decimal]) -> Decimal:
    total = Decimal("0")
    for dimension in SCORE_DIMENSIONS:
        total += breakdown[dimension] * DEFAULT_DIMENSION_WEIGHTS[dimension]
    return _clamp_decimal(total)


def _classify_candidate(
    metrics: Mapping[str, Any],
    normalized_score: Decimal,
    config: CandidateScoringConfig,
) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    blockers: list[str] = []

    expectancy = metrics["expectancy"]
    max_drawdown = metrics["max_drawdown"]
    sample_size = metrics["sample_size"]
    evidence_age_days = metrics["evidence_age_days"]

    if expectancy is not None and expectancy < Decimal("0"):
        reasons.append("expectancy is negative")
        blockers.append("negative expectancy")
        return REJECT, reasons, blockers

    if metrics["risk_blocked"]:
        reasons.append("candidate is explicitly risk-blocked")
        blockers.append("risk block flag is true")
        return BLOCKED_BY_RISK, reasons, blockers

    if max_drawdown is not None and max_drawdown > config.max_drawdown_allowed:
        reasons.append(
            f"max_drawdown {max_drawdown} exceeds allowed {config.max_drawdown_allowed}"
        )
        blockers.append("excessive drawdown")
        return BLOCKED_BY_RISK, reasons, blockers

    evidence_blockers = _evidence_blockers(metrics, config)
    if evidence_blockers:
        reasons.extend(evidence_blockers)
        blockers.extend(evidence_blockers)
        return BLOCKED_BY_EVIDENCE, reasons, blockers

    demo_blockers = _demo_readiness_blockers(metrics)
    if demo_blockers:
        reasons.extend(demo_blockers)
        blockers.extend(demo_blockers)
        return BLOCKED_BY_DEMO_READINESS, reasons, blockers

    more_evidence = _more_evidence_reasons(metrics, config)
    if more_evidence:
        reasons.extend(more_evidence)
        blockers.extend(more_evidence)
        return REQUIRE_MORE_EVIDENCE, reasons, blockers

    if normalized_score >= config.review_ready_threshold:
        reasons.append(
            f"normalized_score {normalized_score} meets review threshold "
            f"{config.review_ready_threshold}"
        )
        reasons.append("candidate remains review-only and authorizes no execution")
        return REVIEW_READY, reasons, blockers

    reasons.append(
        f"normalized_score {normalized_score} is below review threshold "
        f"{config.review_ready_threshold}"
    )
    if expectancy is None:
        reasons.append("expectancy is missing")
    if sample_size is None:
        reasons.append("sample_size is missing")
    if evidence_age_days is None:
        reasons.append("evidence recency is missing")
    blockers.extend(reasons)
    return REQUIRE_MORE_EVIDENCE, reasons, blockers


def _evidence_blockers(
    metrics: Mapping[str, Any],
    config: CandidateScoringConfig,
) -> list[str]:
    blockers: list[str] = []
    evidence_score = metrics["evidence_quality_score"]
    evidence_present = metrics["evidence_present"]
    evidence_complete = metrics["required_evidence_complete"]
    evidence_age_days = metrics["evidence_age_days"]
    recency_score = metrics["recency_score"]

    if evidence_present is False:
        blockers.append("required evidence is marked absent")
    if evidence_complete is False:
        blockers.append("required evidence is incomplete")
    if evidence_score is None and evidence_present is not True and evidence_complete is not True:
        blockers.append("evidence quality is missing")
    elif evidence_score is not None and evidence_score <= Decimal("0"):
        blockers.append("evidence quality score must be greater than zero")
    if evidence_age_days is not None and evidence_age_days >= config.stale_evidence_days:
        blockers.append(
            f"evidence age {evidence_age_days} days is stale at or beyond "
            f"{config.stale_evidence_days} days"
        )
    elif evidence_age_days is None and recency_score is None:
        blockers.append("evidence recency is missing")

    return blockers


def _demo_readiness_blockers(metrics: Mapping[str, Any]) -> list[str]:
    demo_score = metrics["demo_readiness_score"]
    demo_readiness = metrics["demo_readiness"]
    if demo_readiness is False:
        return ["demo readiness is marked false"]
    if demo_score is None and demo_readiness is not True:
        return ["demo readiness is missing"]
    if demo_score is not None and demo_score <= Decimal("0"):
        return ["demo readiness score must be greater than zero"]
    return []


def _more_evidence_reasons(
    metrics: Mapping[str, Any],
    config: CandidateScoringConfig,
) -> list[str]:
    reasons: list[str] = []
    expectancy = metrics["expectancy"]
    profit_factor = metrics["profit_factor"]
    max_drawdown = metrics["max_drawdown"]
    sample_size = metrics["sample_size"]

    if expectancy is None:
        reasons.append("expectancy is missing")
    if profit_factor is None:
        reasons.append("profit_factor is missing")
    if max_drawdown is None:
        reasons.append("max_drawdown is missing")
    if sample_size is None:
        reasons.append("sample_size is missing")
    elif sample_size < config.min_sample_size:
        reasons.append(
            f"sample_size {sample_size} is below required {config.min_sample_size}"
        )
    return reasons


def _ranking_key(result: CandidateScoreResult) -> tuple[Any, ...]:
    return (
        DECISION_PRIORITY[result.decision],
        Decimal(str(-result.normalized_score)),
        Decimal(str(-result.total_score)),
        result.candidate_id,
    )


def _recommended_next_action(decision: str) -> str:
    if decision == REVIEW_READY:
        return (
            "Prepare a supervised demo review packet; do not place, route, or "
            "approve a trade."
        )
    if decision == REQUIRE_MORE_EVIDENCE:
        return "Collect missing or weak candidate evidence, then rerun scoring."
    if decision == REJECT:
        return "Reject or redesign the candidate before any review lane."
    if decision == BLOCKED_BY_RISK:
        return "Resolve risk blockers before candidate review."
    if decision == BLOCKED_BY_EVIDENCE:
        return "Repair candidate evidence completeness and freshness before review."
    return "Complete demo readiness evidence before supervised demo review."


def _score_or_derived(score: Decimal | None, derived: Decimal) -> Decimal:
    return _clamp_decimal(derived if score is None else score)


def _first(source: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in source:
            return source[name]
    return None


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if value is True or value is False:
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y"}:
            return True
        if lowered in {"0", "false", "no", "n"}:
            return False
    return None


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _int_or_none(value: Any) -> int | None:
    decimal_value = _decimal_or_none(value)
    if decimal_value is None:
        return None
    try:
        return int(decimal_value)
    except (ValueError, OverflowError):
        return None


def _score_or_none(value: Any) -> Decimal | None:
    decimal_value = _decimal_or_none(value)
    if decimal_value is None:
        return None
    return _clamp_decimal(decimal_value)


def _clamp_decimal(value: Decimal) -> Decimal:
    if value < Decimal("0"):
        return Decimal("0")
    if value > Decimal("100"):
        return Decimal("100")
    return value.quantize(Decimal("0.000001"))


def _decimal_float(value: Decimal | None) -> float:
    if value is None:
        return 0.0
    return float(value.quantize(Decimal("0.000001")))


__all__ = [
    "BLOCKED_BY_DEMO_READINESS",
    "BLOCKED_BY_EVIDENCE",
    "BLOCKED_BY_RISK",
    "CANDIDATE_SCORING_VERSION",
    "CandidateScoreResult",
    "CandidateScoringConfig",
    "REJECT",
    "REQUIRE_MORE_EVIDENCE",
    "REVIEW_READY",
    "SCORE_DIMENSIONS",
    "candidate_score_to_jsonable_dict",
    "candidate_scores_to_jsonable_dict",
    "score_candidate",
    "score_candidates",
]
