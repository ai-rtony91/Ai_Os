"""Local-only AIOS Forex Profit Proof Ledger V1.

This module evaluates strategy evidence records, ranks competing strategies,
and reports whether any strategy has earned promotion to operator proof review.
It does not call brokers, read credentials, read .env files, place orders,
mutate repo state, start automation, approve real money, or approve
compounding.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Any, Mapping, Sequence


getcontext().prec = 28

PROFIT_PROOF_LEDGER_VERSION = "profit_proof_ledger_v1"

PROFIT_PROOF_LEDGER_PROMOTABLE = "PROFIT_PROOF_LEDGER_PROMOTABLE"
PROFIT_PROOF_LEDGER_MORE_EVIDENCE_REQUIRED = (
    "PROFIT_PROOF_LEDGER_MORE_EVIDENCE_REQUIRED"
)
PROFIT_PROOF_LEDGER_REJECTED = "PROFIT_PROOF_LEDGER_REJECTED"
PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE = (
    "PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE"
)
PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY = (
    "PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY"
)
PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR = (
    "PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR"
)
PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN = "PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN"
PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH = (
    "PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH"
)
PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY = "PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY"

VALID_CLASSIFICATIONS = {
    PROFIT_PROOF_LEDGER_PROMOTABLE,
    PROFIT_PROOF_LEDGER_MORE_EVIDENCE_REQUIRED,
    PROFIT_PROOF_LEDGER_REJECTED,
    PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE,
    PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY,
    PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR,
    PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN,
    PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH,
    PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY,
}

UNKNOWN = "UNKNOWN"

REQUIRED_JSON_KEYS = (
    "ledger_status",
    "top_candidate",
    "rankings",
    "candidate_results",
    "permissions",
    "blockers",
    "next_safe_action",
)

PROOF_CATEGORIES = (
    "candidate_identity",
    "total_trades",
    "wins",
    "losses",
    "win_rate",
    "loss_rate",
    "realized_pl_total",
    "expectancy",
    "average_win",
    "average_loss",
    "profit_factor",
    "max_drawdown",
    "consecutive_losses",
    "recovery_factor",
    "sample_depth",
    "walk_forward_status",
    "out_of_sample_status",
    "paper_vs_demo_comparison",
    "strategy_decay",
    "broker_reconciliation_status",
    "spread_sensitivity",
    "slippage_sensitivity",
    "latency_observations",
    "latency_sensitivity",
    "market_regime_coverage",
    "risk_controls",
)


@dataclass(frozen=True)
class ProfitProofLedgerConfig:
    """Thresholds for deterministic strategy proof evaluation."""

    minimum_total_trades: int = 30
    minimum_profit_factor: Decimal | str | int | float = Decimal("1.25")
    maximum_drawdown: Decimal | str | int | float = Decimal("0.05")
    maximum_consecutive_losses: int = 3
    minimum_market_regimes: int = 3

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "minimum_total_trades", _to_non_negative_int(self.minimum_total_trades)
        )
        object.__setattr__(
            self, "minimum_profit_factor", _to_decimal(self.minimum_profit_factor)
        )
        object.__setattr__(self, "maximum_drawdown", _to_decimal(self.maximum_drawdown))
        object.__setattr__(
            self,
            "maximum_consecutive_losses",
            _to_non_negative_int(self.maximum_consecutive_losses),
        )
        object.__setattr__(
            self, "minimum_market_regimes", _to_non_negative_int(self.minimum_market_regimes)
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProfitProofLedgerConfig":
        return cls(
            minimum_total_trades=raw.get(
                "minimum_total_trades",
                raw.get("minimum_sample_size", cls.minimum_total_trades),
            ),
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
            minimum_market_regimes=raw.get(
                "minimum_market_regimes", cls.minimum_market_regimes
            ),
        )


@dataclass(frozen=True)
class ProfitProofCandidateEvidence:
    """Raw or normalized strategy evidence for the proof ledger."""

    candidate_id: Any = None
    strategy_name: Any = None
    symbol: Any = None
    direction: Any = None
    evidence_source: Any = None
    total_trades: Any = None
    wins: Any = None
    losses: Any = None
    realized_pl_total: Any = None
    expectancy: Any = None
    average_win: Any = None
    average_loss: Any = None
    profit_factor: Any = None
    max_drawdown: Any = None
    consecutive_losses: Any = None
    sample_depth_sufficient: Any = None
    walk_forward_passed: Any = None
    out_of_sample_passed: Any = None
    paper_demo_comparison: Any = None
    strategy_decay_flag: Any = None
    broker_reconciliation_status: Any = None
    spread_sensitivity_passed: Any = None
    slippage_sensitivity_passed: Any = None
    latency_observations: Any = None
    latency_sensitivity_passed: Any = None
    market_regime_coverage: Any = None
    risk_controls_present: Any = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "ProfitProofCandidateEvidence":
        return cls(
            candidate_id=raw.get("candidate_id"),
            strategy_name=raw.get("strategy_name"),
            symbol=raw.get("symbol"),
            direction=raw.get("direction"),
            evidence_source=raw.get("evidence_source"),
            total_trades=raw.get("total_trades"),
            wins=raw.get("wins"),
            losses=raw.get("losses"),
            realized_pl_total=raw.get("realized_pl_total"),
            expectancy=raw.get("expectancy"),
            average_win=raw.get("average_win", raw.get("avg_win")),
            average_loss=raw.get("average_loss", raw.get("avg_loss")),
            profit_factor=raw.get("profit_factor"),
            max_drawdown=raw.get("max_drawdown"),
            consecutive_losses=raw.get("consecutive_losses"),
            sample_depth_sufficient=raw.get("sample_depth_sufficient"),
            walk_forward_passed=raw.get(
                "walk_forward_passed", raw.get("walk_forward_gate_cleared")
            ),
            out_of_sample_passed=raw.get(
                "out_of_sample_passed", raw.get("out_of_sample_status")
            ),
            paper_demo_comparison=raw.get(
                "paper_demo_comparison", raw.get("paper_vs_demo_comparison")
            ),
            strategy_decay_flag=raw.get(
                "strategy_decay_flag", raw.get("strategy_decay_detected")
            ),
            broker_reconciliation_status=raw.get("broker_reconciliation_status"),
            spread_sensitivity_passed=raw.get("spread_sensitivity_passed"),
            slippage_sensitivity_passed=raw.get("slippage_sensitivity_passed"),
            latency_observations=raw.get("latency_observations"),
            latency_sensitivity_passed=raw.get("latency_sensitivity_passed"),
            market_regime_coverage=raw.get("market_regime_coverage"),
            risk_controls_present=raw.get("risk_controls_present"),
        )


@dataclass(frozen=True)
class ProfitProofCandidateResult:
    """Per-strategy proof result and deterministic ranking fields."""

    candidate_id: str
    strategy_name: str
    classification: str
    promotable: bool
    review_ready: bool
    evidence_score: Decimal
    confidence_score: Decimal
    promotion_score: Decimal
    promotion_recommendation: str
    review_recommendation: str
    metrics: Mapping[str, Any]
    proof_status: Mapping[str, Any]
    blockers: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    next_safe_action: str
    rank: int | None = None

    def __post_init__(self) -> None:
        if self.classification not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid classification: {self.classification}")


@dataclass(frozen=True)
class ProfitProofLedgerResult:
    """Full ledger evaluation for a set of competing strategies."""

    ledger_status: str
    top_candidate_id: str
    top_candidate: ProfitProofCandidateResult | None
    selected_candidate: ProfitProofCandidateResult | None
    rankings: tuple[ProfitProofCandidateResult, ...]
    candidate_results: tuple[ProfitProofCandidateResult, ...]
    real_money_allowed: bool
    compounding_allowed: bool
    broker_action_allowed: bool
    bank_movement_allowed: bool
    next_demo_trade_allowed: bool
    owner_approval_required: bool
    permissions: Mapping[str, bool]
    blockers: tuple[str, ...]
    source_files_missing: tuple[str, ...]
    next_safe_action: str
    operator_answer: str

    def __post_init__(self) -> None:
        if self.ledger_status not in VALID_CLASSIFICATIONS:
            raise ValueError(f"invalid ledger status: {self.ledger_status}")


def build_sample_profit_proof_candidates() -> tuple[ProfitProofCandidateEvidence, ...]:
    """Return deterministic mixed evidence with one strongest proof candidate."""

    return (
        ProfitProofCandidateEvidence(
            candidate_id="weak-negative-expectancy",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_profit_proof_negative_expectancy",
            total_trades=35,
            wins=15,
            losses=20,
            realized_pl_total=Decimal("-4.00"),
            expectancy=Decimal("-0.11"),
            average_win=Decimal("0.85"),
            average_loss=Decimal("-0.84"),
            profit_factor=Decimal("0.76"),
            max_drawdown=Decimal("0.030"),
            consecutive_losses=3,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            paper_demo_comparison="paper_underperformed_demo",
            strategy_decay_flag=False,
            broker_reconciliation_status="RECONCILED",
            spread_sensitivity_passed=True,
            slippage_sensitivity_passed=True,
            latency_observations="stable_under_sample",
            latency_sensitivity_passed=True,
            market_regime_coverage=3,
            risk_controls_present=True,
        ),
        ProfitProofCandidateEvidence(
            candidate_id="c1-eur-buy-review-ready-proof",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_profit_proof_review_ready",
            total_trades=34,
            wins=22,
            losses=12,
            realized_pl_total=Decimal("18.40"),
            expectancy=Decimal("0.54"),
            average_win=Decimal("1.22"),
            average_loss=Decimal("-0.70"),
            profit_factor=Decimal("1.74"),
            max_drawdown=Decimal("0.026"),
            consecutive_losses=2,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            paper_demo_comparison="paper_demo_consistent",
            strategy_decay_flag=False,
            broker_reconciliation_status=UNKNOWN,
            spread_sensitivity_passed=True,
            slippage_sensitivity_passed=UNKNOWN,
            latency_observations="sample latency recorded",
            latency_sensitivity_passed=True,
            market_regime_coverage=3,
            risk_controls_present=True,
        ),
        ProfitProofCandidateEvidence(
            candidate_id="c2-eur-buy-stronger-review-ready",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_profit_proof_strongest",
            total_trades=40,
            wins=27,
            losses=13,
            realized_pl_total=Decimal("28.00"),
            expectancy=Decimal("0.70"),
            average_win=Decimal("1.35"),
            average_loss=Decimal("-0.65"),
            profit_factor=Decimal("1.90"),
            max_drawdown=Decimal("0.020"),
            consecutive_losses=2,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            paper_demo_comparison="paper_demo_consistent",
            strategy_decay_flag=False,
            broker_reconciliation_status="RECONCILED",
            spread_sensitivity_passed=True,
            slippage_sensitivity_passed=True,
            latency_observations="stable_under_sample",
            latency_sensitivity_passed=True,
            market_regime_coverage=4,
            risk_controls_present=True,
        ),
        ProfitProofCandidateEvidence(
            candidate_id="weak-low-profit-factor",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_profit_proof_low_pf",
            total_trades=36,
            wins=20,
            losses=16,
            realized_pl_total=Decimal("4.80"),
            expectancy=Decimal("0.13"),
            average_win=Decimal("0.82"),
            average_loss=Decimal("-0.78"),
            profit_factor=Decimal("1.18"),
            max_drawdown=Decimal("0.025"),
            consecutive_losses=2,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            paper_demo_comparison="paper_demo_consistent",
            strategy_decay_flag=False,
            broker_reconciliation_status="RECONCILED",
            spread_sensitivity_passed=True,
            slippage_sensitivity_passed=True,
            latency_observations="stable_under_sample",
            latency_sensitivity_passed=True,
            market_regime_coverage=3,
            risk_controls_present=True,
        ),
    )


def build_sample_all_blocked_candidates() -> tuple[ProfitProofCandidateEvidence, ...]:
    """Return deterministic evidence where every strategy is blocked."""

    return (
        ProfitProofCandidateEvidence(
            candidate_id="blocked-negative-expectancy",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_blocked_negative_expectancy",
            total_trades=32,
            wins=12,
            losses=20,
            realized_pl_total=Decimal("-6.20"),
            expectancy=Decimal("-0.19"),
            average_win=Decimal("0.70"),
            average_loss=Decimal("-0.73"),
            profit_factor=Decimal("0.58"),
            max_drawdown=Decimal("0.030"),
            consecutive_losses=3,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            risk_controls_present=True,
        ),
        ProfitProofCandidateEvidence(
            candidate_id="blocked-low-profit-factor",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_blocked_low_profit_factor",
            total_trades=34,
            wins=19,
            losses=15,
            realized_pl_total=Decimal("2.10"),
            expectancy=Decimal("0.06"),
            average_win=Decimal("0.90"),
            average_loss=Decimal("-0.88"),
            profit_factor=Decimal("1.18"),
            max_drawdown=Decimal("0.024"),
            consecutive_losses=2,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            risk_controls_present=True,
        ),
        ProfitProofCandidateEvidence(
            candidate_id="blocked-high-drawdown",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_blocked_high_drawdown",
            total_trades=38,
            wins=25,
            losses=13,
            realized_pl_total=Decimal("13.20"),
            expectancy=Decimal("0.35"),
            average_win=Decimal("1.05"),
            average_loss=Decimal("-0.82"),
            profit_factor=Decimal("1.55"),
            max_drawdown=Decimal("0.090"),
            consecutive_losses=2,
            sample_depth_sufficient=True,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            risk_controls_present=True,
        ),
        ProfitProofCandidateEvidence(
            candidate_id="blocked-insufficient-sample",
            strategy_name="paper_long_run_supervisor_v2",
            symbol="EUR_USD",
            direction="LONG",
            evidence_source="synthetic_blocked_insufficient_sample",
            total_trades=18,
            wins=12,
            losses=6,
            realized_pl_total=Decimal("7.20"),
            expectancy=Decimal("0.40"),
            average_win=Decimal("1.00"),
            average_loss=Decimal("-0.80"),
            profit_factor=Decimal("2.50"),
            max_drawdown=Decimal("0.018"),
            consecutive_losses=1,
            sample_depth_sufficient=False,
            walk_forward_passed=True,
            out_of_sample_passed=True,
            risk_controls_present=True,
        ),
    )


def evaluate_profit_proof_candidate(
    evidence: ProfitProofCandidateEvidence | Mapping[str, Any] | None = None,
    config: ProfitProofLedgerConfig | Mapping[str, Any] | None = None,
) -> ProfitProofCandidateResult:
    """Evaluate one strategy evidence record without inventing missing proof."""

    active_config = _coerce_config(config)
    candidate = _coerce_candidate(evidence)
    normalized = _normalize_candidate(candidate)
    metrics = _build_metrics(normalized, active_config)
    proof_status = _build_proof_status(normalized, metrics, active_config)
    blockers, missing_evidence = _candidate_blockers(metrics, proof_status, active_config)
    classification = _candidate_classification(metrics, proof_status, blockers)
    promotable = classification == PROFIT_PROOF_LEDGER_PROMOTABLE
    review_ready = classification in {
        PROFIT_PROOF_LEDGER_PROMOTABLE,
        PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY,
    }
    evidence_score = _score_evidence(proof_status)
    confidence_score = _score_confidence(proof_status)
    promotion_score = _score_promotion(metrics, proof_status, active_config)

    return ProfitProofCandidateResult(
        candidate_id=normalized["candidate_id"],
        strategy_name=normalized["strategy_name"],
        classification=classification,
        promotable=promotable,
        review_ready=review_ready,
        evidence_score=evidence_score,
        confidence_score=confidence_score,
        promotion_score=promotion_score,
        promotion_recommendation=_promotion_recommendation(classification),
        review_recommendation=_review_recommendation(classification),
        metrics=metrics,
        proof_status=proof_status,
        blockers=tuple(blockers),
        missing_evidence=tuple(missing_evidence),
        next_safe_action=_candidate_next_safe_action(classification),
    )


def evaluate_profit_proof_ledger(
    candidates: Sequence[ProfitProofCandidateEvidence | Mapping[str, Any]] | None = None,
    config: ProfitProofLedgerConfig | Mapping[str, Any] | None = None,
    *,
    source_files_missing: Sequence[str] = (),
) -> ProfitProofLedgerResult:
    """Evaluate and rank multiple strategy proof records."""

    active_config = _coerce_config(config)
    active_candidates = (
        tuple(candidates) if candidates is not None else build_sample_profit_proof_candidates()
    )
    candidate_results = tuple(
        evaluate_profit_proof_candidate(candidate, active_config)
        for candidate in active_candidates
    )
    rankings = _rank_results(candidate_results)
    top_candidate = rankings[0] if rankings else None
    selected_candidate = next((result for result in rankings if result.promotable), None)
    ledger_status = _ledger_status(candidate_results, selected_candidate)
    blockers = _ledger_blockers(candidate_results, source_files_missing)
    permissions = _permissions()

    return ProfitProofLedgerResult(
        ledger_status=ledger_status,
        top_candidate_id=top_candidate.candidate_id if top_candidate else "NONE",
        top_candidate=top_candidate,
        selected_candidate=selected_candidate,
        rankings=rankings,
        candidate_results=candidate_results,
        real_money_allowed=False,
        compounding_allowed=False,
        broker_action_allowed=False,
        bank_movement_allowed=False,
        next_demo_trade_allowed=False,
        owner_approval_required=True,
        permissions=permissions,
        blockers=tuple(blockers),
        source_files_missing=tuple(source_files_missing),
        next_safe_action=_ledger_next_safe_action(ledger_status),
        operator_answer=_operator_answer(ledger_status, top_candidate, selected_candidate),
    )


def result_to_operator_text(result: ProfitProofLedgerResult) -> str:
    """Return a deterministic operator-readable ledger summary."""

    top = result.top_candidate
    lines = [
        "AIOS Forex Profit Proof Ledger V1",
        f"ledger_status: {result.ledger_status}",
        f"top_candidate_id: {result.top_candidate_id}",
        (
            "top_evidence_score: "
            f"{_json_value(top.evidence_score) if top else 'NONE'}"
        ),
        (
            "top_confidence_score: "
            f"{_json_value(top.confidence_score) if top else 'NONE'}"
        ),
        (
            "top_promotion_score: "
            f"{_json_value(top.promotion_score) if top else 'NONE'}"
        ),
        f"next_demo_trade_allowed: {_bool_text(result.next_demo_trade_allowed)}",
        f"real_money_allowed: {_bool_text(result.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(result.compounding_allowed)}",
        f"broker_action_allowed: {_bool_text(result.broker_action_allowed)}",
        f"bank_movement_allowed: {_bool_text(result.bank_movement_allowed)}",
        f"owner_approval_required: {_bool_text(result.owner_approval_required)}",
        f"operator_answer: {result.operator_answer}",
        "rankings:",
    ]
    if result.rankings:
        for candidate in result.rankings:
            lines.append(
                (
                    f"- rank {candidate.rank}: {candidate.candidate_id} "
                    f"classification={candidate.classification} "
                    f"promotion_score={_json_value(candidate.promotion_score)} "
                    f"expectancy={_json_value(candidate.metrics['expectancy'])} "
                    f"profit_factor={_json_value(candidate.metrics['profit_factor'])}"
                )
            )
    else:
        lines.append("- none")
    lines.append("blockers:")
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")
    lines.append(f"next_safe_action: {result.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: ProfitProofLedgerResult) -> dict[str, Any]:
    """Return deterministic JSON-safe ledger data."""

    return {
        "ledger_version": PROFIT_PROOF_LEDGER_VERSION,
        "ledger_status": result.ledger_status,
        "top_candidate_id": result.top_candidate_id,
        "top_candidate": _candidate_result_to_jsonable(result.top_candidate),
        "selected_candidate": _candidate_result_to_jsonable(result.selected_candidate),
        "rankings": [_candidate_result_to_jsonable(candidate) for candidate in result.rankings],
        "candidate_results": [
            _candidate_result_to_jsonable(candidate)
            for candidate in result.candidate_results
        ],
        "permissions": dict(result.permissions),
        "real_money_allowed": result.real_money_allowed,
        "compounding_allowed": result.compounding_allowed,
        "broker_action_allowed": result.broker_action_allowed,
        "bank_movement_allowed": result.bank_movement_allowed,
        "next_demo_trade_allowed": result.next_demo_trade_allowed,
        "owner_approval_required": result.owner_approval_required,
        "blockers": list(result.blockers),
        "source_files_missing": list(result.source_files_missing),
        "next_safe_action": result.next_safe_action,
        "operator_answer": result.operator_answer,
        "safety": {
            "local_only": True,
            "network_calls": False,
            "broker_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "repo_mutation": False,
            "order_placement": False,
            "real_money_approval": False,
            "compounding_approval": False,
            "bank_movement_approval": False,
        },
    }


def ledger_to_markdown(result: ProfitProofLedgerResult | None = None) -> str:
    """Return the readable proof ledger artifact."""

    active_result = result if result is not None else evaluate_profit_proof_ledger()
    lines = [
        "# AIOS Forex Profit Proof Ledger V1",
        "",
        "## Purpose",
        (
            "Profit Proof Ledger V1 is the local-only evidence bucket that ranks "
            "Forex strategies and answers whether a strategy has earned "
            "operator proof review."
        ),
        "",
        "## Proof Categories",
        *[f"- {category}" for category in PROOF_CATEGORIES],
        "",
        "## Scoring Model",
        "- evidence_score measures proof categories that are present and passing.",
        "- confidence_score weights core proof gates needed before promotion.",
        "- promotion_score ranks strategies by proof status, expectancy, profit factor, sample depth, drawdown, recovery, and risk evidence.",
        "- Missing evidence remains UNKNOWN and does not become proof.",
        "",
        "## Promotion Gates",
        f"- minimum_total_trades: {ProfitProofLedgerConfig().minimum_total_trades}",
        f"- minimum_profit_factor: {_json_value(ProfitProofLedgerConfig().minimum_profit_factor)}",
        f"- maximum_drawdown: {_json_value(ProfitProofLedgerConfig().maximum_drawdown)}",
        "- positive expectancy required.",
        "- walk-forward proof required.",
        "- out-of-sample proof required.",
        "- broker reconciliation, spread, slippage, latency, market regime, decay, and risk-control evidence required for promotable status.",
        "",
        "## Permission Locks",
        "- next_demo_trade_allowed: false.",
        "- broker_action_allowed: false.",
        "- real_money_allowed: false.",
        "- compounding_allowed: false.",
        "- bank_movement_allowed: false.",
        "- owner_approval_required: true.",
        "",
        "## Sample Results",
        f"ledger_status: {active_result.ledger_status}",
        f"top_candidate_id: {active_result.top_candidate_id}",
        f"promotion_recommendation: {_top_promotion(active_result)}",
        "",
        "## Rankings",
    ]
    if active_result.rankings:
        for candidate in active_result.rankings:
            lines.append(
                (
                    f"- {candidate.rank}. {candidate.candidate_id}: "
                    f"{candidate.classification}, "
                    f"evidence_score={_json_value(candidate.evidence_score)}, "
                    f"confidence_score={_json_value(candidate.confidence_score)}, "
                    f"promotion_score={_json_value(candidate.promotion_score)}"
                )
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Next Safe Action",
            active_result.next_safe_action,
            "",
        ]
    )
    return "\n".join(lines)


def _coerce_config(
    raw: ProfitProofLedgerConfig | Mapping[str, Any] | None,
) -> ProfitProofLedgerConfig:
    if isinstance(raw, ProfitProofLedgerConfig):
        return raw
    if isinstance(raw, Mapping):
        return ProfitProofLedgerConfig.from_mapping(raw)
    return ProfitProofLedgerConfig()


def _coerce_candidate(
    raw: ProfitProofCandidateEvidence | Mapping[str, Any] | None,
) -> ProfitProofCandidateEvidence:
    if isinstance(raw, ProfitProofCandidateEvidence):
        return raw
    if isinstance(raw, Mapping):
        candidate_raw = raw.get("candidate", raw.get("candidate_evidence", raw))
        if not isinstance(candidate_raw, Mapping):
            candidate_raw = {}
        return ProfitProofCandidateEvidence.from_mapping(candidate_raw)
    return ProfitProofCandidateEvidence()


def _normalize_candidate(candidate: ProfitProofCandidateEvidence) -> dict[str, Any]:
    return {
        "candidate_id": _string_or_default(candidate.candidate_id, "NONE"),
        "strategy_name": _string_or_default(candidate.strategy_name, "UNKNOWN"),
        "symbol": _string_or_default(candidate.symbol, UNKNOWN),
        "direction": _string_or_default(candidate.direction, UNKNOWN),
        "evidence_source": _string_or_default(candidate.evidence_source, UNKNOWN),
        "total_trades": _int_or_unknown(candidate.total_trades),
        "wins": _int_or_unknown(candidate.wins),
        "losses": _int_or_unknown(candidate.losses),
        "realized_pl_total": _decimal_or_unknown(candidate.realized_pl_total),
        "expectancy": _decimal_or_unknown(candidate.expectancy),
        "average_win": _decimal_or_unknown(candidate.average_win, absolute=True),
        "average_loss": _decimal_or_unknown(candidate.average_loss, absolute=True),
        "profit_factor": _decimal_or_unknown(candidate.profit_factor),
        "max_drawdown": _decimal_or_unknown(candidate.max_drawdown, absolute=True),
        "consecutive_losses": _int_or_unknown(candidate.consecutive_losses),
        "sample_depth_sufficient": _bool_or_unknown(candidate.sample_depth_sufficient),
        "walk_forward_passed": _bool_or_unknown(candidate.walk_forward_passed),
        "out_of_sample_passed": _bool_or_unknown(candidate.out_of_sample_passed),
        "paper_demo_comparison": _string_or_default(candidate.paper_demo_comparison, UNKNOWN),
        "strategy_decay_flag": _bool_or_unknown(candidate.strategy_decay_flag),
        "broker_reconciliation_status": _string_or_default(
            candidate.broker_reconciliation_status, UNKNOWN
        ),
        "spread_sensitivity_passed": _bool_or_unknown(candidate.spread_sensitivity_passed),
        "slippage_sensitivity_passed": _bool_or_unknown(
            candidate.slippage_sensitivity_passed
        ),
        "latency_observations": _string_or_default(candidate.latency_observations, UNKNOWN),
        "latency_sensitivity_passed": _bool_or_unknown(candidate.latency_sensitivity_passed),
        "market_regime_coverage": _int_or_unknown(candidate.market_regime_coverage),
        "risk_controls_present": _bool_or_unknown(candidate.risk_controls_present),
    }


def _build_metrics(
    candidate: Mapping[str, Any],
    config: ProfitProofLedgerConfig,
) -> dict[str, Any]:
    total_trades = candidate["total_trades"]
    wins = candidate["wins"]
    losses = candidate["losses"]
    average_win = candidate["average_win"]
    average_loss = candidate["average_loss"]

    win_rate = UNKNOWN
    loss_rate = UNKNOWN
    if _all_known(total_trades, wins, losses) and total_trades > 0:
        win_rate = Decimal(wins) / Decimal(total_trades)
        loss_rate = Decimal(losses) / Decimal(total_trades)

    expectancy = candidate["expectancy"]
    if expectancy == UNKNOWN and _all_known(win_rate, loss_rate, average_win, average_loss):
        expectancy = (win_rate * average_win) - (loss_rate * average_loss)

    profit_factor = candidate["profit_factor"]
    if profit_factor == UNKNOWN and _all_known(wins, losses, average_win, average_loss):
        profit_factor = _calculate_profit_factor(wins, losses, average_win, average_loss)

    recovery_factor = UNKNOWN
    realized_pl_total = candidate["realized_pl_total"]
    max_drawdown = candidate["max_drawdown"]
    if _all_known(realized_pl_total, max_drawdown) and max_drawdown > Decimal("0"):
        recovery_factor = realized_pl_total / max_drawdown

    sample_depth = UNKNOWN
    if total_trades != UNKNOWN:
        sample_depth = {
            "total_trades": total_trades,
            "minimum_total_trades": config.minimum_total_trades,
            "sufficient": total_trades >= config.minimum_total_trades
            and candidate["sample_depth_sufficient"] is True,
        }

    return {
        "candidate_id": candidate["candidate_id"],
        "strategy_name": candidate["strategy_name"],
        "symbol": candidate["symbol"],
        "direction": candidate["direction"],
        "evidence_source": candidate["evidence_source"],
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "loss_rate": loss_rate,
        "realized_pl_total": realized_pl_total,
        "expectancy": expectancy,
        "average_win": average_win,
        "average_loss": average_loss,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "consecutive_losses": candidate["consecutive_losses"],
        "recovery_factor": recovery_factor,
        "sample_depth": sample_depth,
        "walk_forward_status": _pass_fail_unknown(candidate["walk_forward_passed"]),
        "out_of_sample_status": _pass_fail_unknown(candidate["out_of_sample_passed"]),
        "paper_vs_demo_comparison": candidate["paper_demo_comparison"],
        "strategy_decay": _decay_status(candidate["strategy_decay_flag"]),
        "broker_reconciliation_status": candidate["broker_reconciliation_status"],
        "spread_sensitivity": _pass_fail_unknown(candidate["spread_sensitivity_passed"]),
        "slippage_sensitivity": _pass_fail_unknown(candidate["slippage_sensitivity_passed"]),
        "latency_observations": candidate["latency_observations"],
        "latency_sensitivity": _pass_fail_unknown(candidate["latency_sensitivity_passed"]),
        "market_regime_coverage": candidate["market_regime_coverage"],
        "risk_controls": _pass_fail_unknown(candidate["risk_controls_present"]),
    }


def _build_proof_status(
    candidate: Mapping[str, Any],
    metrics: Mapping[str, Any],
    config: ProfitProofLedgerConfig,
) -> dict[str, Any]:
    sample_depth = metrics["sample_depth"]
    market_regime_coverage = metrics["market_regime_coverage"]
    return {
        "candidate_identity": candidate["candidate_id"].strip().upper()
        not in {"", "NONE", "UNKNOWN"},
        "total_trades": metrics["total_trades"] != UNKNOWN,
        "wins": metrics["wins"] != UNKNOWN,
        "losses": metrics["losses"] != UNKNOWN,
        "win_rate": metrics["win_rate"] != UNKNOWN,
        "loss_rate": metrics["loss_rate"] != UNKNOWN,
        "realized_pl_total": metrics["realized_pl_total"] != UNKNOWN,
        "expectancy": metrics["expectancy"] != UNKNOWN and metrics["expectancy"] > Decimal("0"),
        "average_win": metrics["average_win"] != UNKNOWN,
        "average_loss": metrics["average_loss"] != UNKNOWN,
        "profit_factor": (
            metrics["profit_factor"] != UNKNOWN
            and metrics["profit_factor"] >= config.minimum_profit_factor
        ),
        "max_drawdown": (
            metrics["max_drawdown"] != UNKNOWN
            and metrics["max_drawdown"] <= config.maximum_drawdown
        ),
        "consecutive_losses": (
            metrics["consecutive_losses"] != UNKNOWN
            and metrics["consecutive_losses"] <= config.maximum_consecutive_losses
        ),
        "recovery_factor": metrics["recovery_factor"] != UNKNOWN
        and metrics["recovery_factor"] > Decimal("0"),
        "sample_depth": isinstance(sample_depth, Mapping) and sample_depth["sufficient"],
        "walk_forward_status": candidate["walk_forward_passed"] is True,
        "out_of_sample_status": candidate["out_of_sample_passed"] is True,
        "paper_vs_demo_comparison": metrics["paper_vs_demo_comparison"] != UNKNOWN,
        "strategy_decay": candidate["strategy_decay_flag"] is False,
        "broker_reconciliation_status": str(
            metrics["broker_reconciliation_status"]
        ).upper()
        == "RECONCILED",
        "spread_sensitivity": candidate["spread_sensitivity_passed"] is True,
        "slippage_sensitivity": candidate["slippage_sensitivity_passed"] is True,
        "latency_observations": metrics["latency_observations"] != UNKNOWN,
        "latency_sensitivity": candidate["latency_sensitivity_passed"] is True,
        "market_regime_coverage": (
            market_regime_coverage != UNKNOWN
            and market_regime_coverage >= config.minimum_market_regimes
        ),
        "risk_controls": candidate["risk_controls_present"] is True,
    }


def _candidate_blockers(
    metrics: Mapping[str, Any],
    proof_status: Mapping[str, Any],
    config: ProfitProofLedgerConfig,
) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    missing: list[str] = []

    for category, passed in proof_status.items():
        if passed:
            continue
        if _category_unknown(category, metrics):
            missing.append(category)

    if not proof_status["candidate_identity"]:
        blockers.append("candidate identity is missing")
    if missing:
        blockers.extend(f"{category} is UNKNOWN" for category in missing)

    total_trades = metrics["total_trades"]
    if total_trades != UNKNOWN and total_trades < config.minimum_total_trades:
        blockers.append(
            f"total trades {total_trades} below minimum {config.minimum_total_trades}"
        )
    sample_depth = metrics["sample_depth"]
    if isinstance(sample_depth, Mapping) and not sample_depth["sufficient"]:
        blockers.append("sample depth is not sufficient")
    expectancy = metrics["expectancy"]
    if expectancy != UNKNOWN and expectancy <= Decimal("0"):
        blockers.append(f"expectancy {expectancy} is not positive")
    profit_factor = metrics["profit_factor"]
    if profit_factor != UNKNOWN and profit_factor < config.minimum_profit_factor:
        blockers.append(
            f"profit factor {profit_factor} below minimum {config.minimum_profit_factor}"
        )
    max_drawdown = metrics["max_drawdown"]
    if max_drawdown != UNKNOWN and max_drawdown > config.maximum_drawdown:
        blockers.append(
            f"max drawdown {max_drawdown} exceeds maximum {config.maximum_drawdown}"
        )
    consecutive_losses = metrics["consecutive_losses"]
    if (
        consecutive_losses != UNKNOWN
        and consecutive_losses > config.maximum_consecutive_losses
    ):
        blockers.append(
            "consecutive losses "
            f"{consecutive_losses} exceed maximum {config.maximum_consecutive_losses}"
        )
    if metrics["walk_forward_status"] != "PASS":
        blockers.append("walk-forward proof has not passed")
    if metrics["out_of_sample_status"] != "PASS":
        blockers.append("out-of-sample proof has not passed")
    if metrics["strategy_decay"] != "NO_DECAY_DETECTED":
        blockers.append("strategy decay proof is not clear")
    if metrics["broker_reconciliation_status"] != "RECONCILED":
        blockers.append("broker reconciliation is not proven")
    if metrics["spread_sensitivity"] != "PASS":
        blockers.append("spread sensitivity proof has not passed")
    if metrics["slippage_sensitivity"] != "PASS":
        blockers.append("slippage sensitivity proof has not passed")
    if metrics["latency_sensitivity"] != "PASS":
        blockers.append("latency sensitivity proof has not passed")
    if not proof_status["market_regime_coverage"]:
        blockers.append("market regime coverage is insufficient or UNKNOWN")
    if metrics["risk_controls"] != "PASS":
        blockers.append("risk controls are not proven")

    return list(dict.fromkeys(blockers)), list(dict.fromkeys(missing))


def _candidate_classification(
    metrics: Mapping[str, Any],
    proof_status: Mapping[str, Any],
    blockers: Sequence[str],
) -> str:
    if all(proof_status.values()) and not blockers:
        return PROFIT_PROOF_LEDGER_PROMOTABLE
    if not proof_status["candidate_identity"] or any("UNKNOWN" in blocker for blocker in blockers):
        core_missing = {
            "candidate_identity",
            "total_trades",
            "wins",
            "losses",
            "expectancy",
            "profit_factor",
            "max_drawdown",
            "sample_depth",
        }
        missing_core = any(
            category in blocker
            for blocker in blockers
            for category in core_missing
        )
        if missing_core:
            return PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE
    if metrics["total_trades"] != UNKNOWN and not proof_status["sample_depth"]:
        return PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH
    if metrics["expectancy"] != UNKNOWN and metrics["expectancy"] <= Decimal("0"):
        return PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY
    if metrics["profit_factor"] != UNKNOWN and not proof_status["profit_factor"]:
        return PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR
    if metrics["max_drawdown"] != UNKNOWN and not proof_status["max_drawdown"]:
        return PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN
    if _core_profit_gates_pass(proof_status):
        return PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY
    if blockers:
        return PROFIT_PROOF_LEDGER_MORE_EVIDENCE_REQUIRED
    return PROFIT_PROOF_LEDGER_REJECTED


def _core_profit_gates_pass(proof_status: Mapping[str, Any]) -> bool:
    return all(
        proof_status.get(category) is True
        for category in (
            "candidate_identity",
            "total_trades",
            "wins",
            "losses",
            "expectancy",
            "profit_factor",
            "max_drawdown",
            "consecutive_losses",
            "sample_depth",
            "walk_forward_status",
            "out_of_sample_status",
            "risk_controls",
        )
    )


def _rank_results(
    results: Sequence[ProfitProofCandidateResult],
) -> tuple[ProfitProofCandidateResult, ...]:
    ranked = sorted(
        results,
        key=lambda result: (
            _status_rank(result),
            -result.promotion_score,
            -_metric_decimal(result, "expectancy"),
            -_metric_decimal(result, "profit_factor"),
            _metric_decimal(result, "max_drawdown", unknown=Decimal("999999")),
            -_metric_decimal(result, "total_trades"),
            result.candidate_id,
        ),
    )
    return tuple(
        _replace_rank(result, rank=index)
        for index, result in enumerate(ranked, start=1)
    )


def _replace_rank(
    result: ProfitProofCandidateResult,
    *,
    rank: int,
) -> ProfitProofCandidateResult:
    return ProfitProofCandidateResult(
        candidate_id=result.candidate_id,
        strategy_name=result.strategy_name,
        classification=result.classification,
        promotable=result.promotable,
        review_ready=result.review_ready,
        evidence_score=result.evidence_score,
        confidence_score=result.confidence_score,
        promotion_score=result.promotion_score,
        promotion_recommendation=result.promotion_recommendation,
        review_recommendation=result.review_recommendation,
        metrics=result.metrics,
        proof_status=result.proof_status,
        blockers=result.blockers,
        missing_evidence=result.missing_evidence,
        next_safe_action=result.next_safe_action,
        rank=rank,
    )


def _ledger_status(
    candidate_results: Sequence[ProfitProofCandidateResult],
    selected_candidate: ProfitProofCandidateResult | None,
) -> str:
    if selected_candidate is not None:
        return PROFIT_PROOF_LEDGER_PROMOTABLE
    if any(result.review_ready for result in candidate_results):
        return PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY
    if not candidate_results:
        return PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE
    if all(result.classification == PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE for result in candidate_results):
        return PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE
    return PROFIT_PROOF_LEDGER_MORE_EVIDENCE_REQUIRED


def _ledger_blockers(
    candidate_results: Sequence[ProfitProofCandidateResult],
    source_files_missing: Sequence[str],
) -> list[str]:
    blockers: list[str] = []
    if not any(result.promotable for result in candidate_results):
        blockers.append("no promotable strategy is selected")
    for result in candidate_results:
        for blocker in result.blockers:
            blockers.append(f"{result.candidate_id}: {blocker}")
    for path in source_files_missing:
        blockers.append(f"source file missing: {path}")
    blockers.extend(
        (
            "next demo trade remains locked",
            "broker action remains locked",
            "real money remains locked",
            "compounding remains locked",
            "bank movement remains locked",
        )
    )
    return list(dict.fromkeys(blockers))


def _score_evidence(proof_status: Mapping[str, Any]) -> Decimal:
    total = Decimal(len(proof_status))
    passed = Decimal(sum(1 for value in proof_status.values() if value is True))
    if total == Decimal("0"):
        return Decimal("0")
    return (passed / total * Decimal("100")).quantize(Decimal("0.01"))


def _score_confidence(proof_status: Mapping[str, Any]) -> Decimal:
    weighted = {
        "expectancy": Decimal("12"),
        "profit_factor": Decimal("12"),
        "max_drawdown": Decimal("10"),
        "sample_depth": Decimal("10"),
        "walk_forward_status": Decimal("10"),
        "out_of_sample_status": Decimal("10"),
        "broker_reconciliation_status": Decimal("8"),
        "spread_sensitivity": Decimal("6"),
        "slippage_sensitivity": Decimal("6"),
        "latency_sensitivity": Decimal("4"),
        "market_regime_coverage": Decimal("6"),
        "risk_controls": Decimal("6"),
    }
    total = sum(weighted.values(), Decimal("0"))
    passed = sum(
        weight
        for category, weight in weighted.items()
        if proof_status.get(category) is True
    )
    if total == Decimal("0"):
        return Decimal("0")
    return (passed / total * Decimal("100")).quantize(Decimal("0.01"))


def _score_promotion(
    metrics: Mapping[str, Any],
    proof_status: Mapping[str, Any],
    config: ProfitProofLedgerConfig,
) -> Decimal:
    expectancy = _metric_decimal_from_mapping(metrics, "expectancy")
    profit_factor = _metric_decimal_from_mapping(metrics, "profit_factor")
    total_trades = _metric_decimal_from_mapping(metrics, "total_trades")
    win_rate = _metric_decimal_from_mapping(metrics, "win_rate")
    recovery_factor = _metric_decimal_from_mapping(metrics, "recovery_factor")
    max_drawdown = _metric_decimal_from_mapping(metrics, "max_drawdown")
    consecutive_losses = _metric_decimal_from_mapping(metrics, "consecutive_losses")

    drawdown_reward = Decimal("0")
    if metrics["max_drawdown"] != UNKNOWN:
        drawdown_reward = max(
            Decimal("0"),
            (config.maximum_drawdown - max_drawdown) * Decimal("1000"),
        )
    sample_reward = min(total_trades, Decimal("100")) / Decimal("2")
    proof_reward = Decimal(sum(1 for value in proof_status.values() if value is True)) * Decimal("4")
    missing_penalty = Decimal(sum(1 for value in proof_status.values() if value is not True)) * Decimal("6")

    score = (
        expectancy * Decimal("120")
        + profit_factor * Decimal("35")
        + sample_reward
        + win_rate * Decimal("30")
        + recovery_factor
        + drawdown_reward
        + proof_reward
        - consecutive_losses * Decimal("5")
        - max_drawdown * Decimal("100")
        - missing_penalty
    )
    return score.quantize(Decimal("0.0001"))


def _promotion_recommendation(classification: str) -> str:
    if classification == PROFIT_PROOF_LEDGER_PROMOTABLE:
        return "PROMOTE_TO_OPERATOR_PROOF_REVIEW_ONLY"
    if classification == PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY:
        return "REVIEW_READY_ONLY_MORE_PROOF_REQUIRED"
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY:
        return "REJECT_NEGATIVE_EXPECTANCY"
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR:
        return "REJECT_LOW_PROFIT_FACTOR"
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN:
        return "REJECT_DRAWDOWN"
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH:
        return "COLLECT_MORE_SAMPLE_DEPTH"
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE:
        return "COLLECT_MISSING_EVIDENCE"
    return "MORE_EVIDENCE_REQUIRED"


def _review_recommendation(classification: str) -> str:
    if classification == PROFIT_PROOF_LEDGER_PROMOTABLE:
        return "OPERATOR_CAN_REVIEW_PROOF_PACKET"
    if classification == PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY:
        return "OPERATOR_CAN_REVIEW_BUT_PROMOTION_IS_BLOCKED"
    return "DO_NOT_REVIEW_FOR_PROMOTION"


def _candidate_next_safe_action(classification: str) -> str:
    if classification == PROFIT_PROOF_LEDGER_PROMOTABLE:
        return (
            "Prepare an operator proof review packet; do not approve broker "
            "action, real money, or compounding."
        )
    if classification == PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY:
        return "Collect missing proof before any promotion beyond operator review."
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_NEGATIVE_EXPECTANCY:
        return "Reject promotion until expectancy is positive."
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_LOW_PROFIT_FACTOR:
        return "Reject promotion until profit factor clears the threshold."
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_DRAWDOWN:
        return "Reject promotion until drawdown is within limit."
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_SAMPLE_DEPTH:
        return "Collect deeper governed evidence before review."
    if classification == PROFIT_PROOF_LEDGER_BLOCKED_MISSING_EVIDENCE:
        return "Record missing proof fields before promotion review."
    return "Continue evidence collection under local-only proof controls."


def _ledger_next_safe_action(status: str) -> str:
    if status == PROFIT_PROOF_LEDGER_PROMOTABLE:
        return (
            "Create a Candidate Review to Operator Decision Packet V1 for the "
            "top strategy; do not place trades or enable real money."
        )
    if status == PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY:
        return "Close missing proof blockers before any demo permission envelope."
    return "Repair blocked strategy evidence and rerun Profit Proof Ledger V1."


def _operator_answer(
    ledger_status: str,
    top_candidate: ProfitProofCandidateResult | None,
    selected_candidate: ProfitProofCandidateResult | None,
) -> str:
    if selected_candidate is not None:
        return (
            "Profit proof ledger selected "
            f"{selected_candidate.candidate_id} for operator proof review only. "
            "This does not approve a next demo trade, broker action, real money, "
            "compounding, or bank movement."
        )
    if top_candidate is not None and ledger_status == PROFIT_PROOF_LEDGER_REVIEW_READY_ONLY:
        return (
            f"Top strategy {top_candidate.candidate_id} is review-ready only, "
            "but promotion is blocked by missing proof. No trade, broker action, "
            "real money, compounding, or bank movement is approved."
        )
    return (
        "No strategy has earned promotion. Missing or weak proof must be repaired "
        "before any operator promotion review. No trade, broker action, real "
        "money, compounding, or bank movement is approved."
    )


def _permissions() -> dict[str, bool]:
    return {
        "candidate_review_allowed": True,
        "next_demo_trade_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
        "credential_access_allowed": False,
        "owner_approval_required": True,
    }


def _candidate_result_to_jsonable(
    result: ProfitProofCandidateResult | None,
) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "rank": result.rank,
        "candidate_id": result.candidate_id,
        "strategy_name": result.strategy_name,
        "classification": result.classification,
        "promotable": result.promotable,
        "review_ready": result.review_ready,
        "evidence_score": _json_value(result.evidence_score),
        "confidence_score": _json_value(result.confidence_score),
        "promotion_score": _json_value(result.promotion_score),
        "promotion_recommendation": result.promotion_recommendation,
        "review_recommendation": result.review_recommendation,
        "metrics": _json_value(result.metrics),
        "proof_status": _json_value(result.proof_status),
        "blockers": list(result.blockers),
        "missing_evidence": list(result.missing_evidence),
        "next_safe_action": result.next_safe_action,
    }


def _category_unknown(category: str, metrics: Mapping[str, Any]) -> bool:
    metric_name = {
        "candidate_identity": "candidate_id",
        "sample_depth": "sample_depth",
        "walk_forward_status": "walk_forward_status",
        "out_of_sample_status": "out_of_sample_status",
        "paper_vs_demo_comparison": "paper_vs_demo_comparison",
        "broker_reconciliation_status": "broker_reconciliation_status",
        "spread_sensitivity": "spread_sensitivity",
        "slippage_sensitivity": "slippage_sensitivity",
        "latency_sensitivity": "latency_sensitivity",
        "market_regime_coverage": "market_regime_coverage",
        "risk_controls": "risk_controls",
        "strategy_decay": "strategy_decay",
    }.get(category, category)
    value = metrics.get(metric_name, UNKNOWN)
    if isinstance(value, Mapping):
        return False
    return value == UNKNOWN


def _status_rank(result: ProfitProofCandidateResult) -> int:
    if result.promotable:
        return 0
    if result.review_ready:
        return 1
    return 2


def _metric_decimal(
    result: ProfitProofCandidateResult,
    key: str,
    *,
    unknown: Decimal = Decimal("0"),
) -> Decimal:
    return _metric_decimal_from_mapping(result.metrics, key, unknown=unknown)


def _metric_decimal_from_mapping(
    metrics: Mapping[str, Any],
    key: str,
    *,
    unknown: Decimal = Decimal("0"),
) -> Decimal:
    value = metrics.get(key, UNKNOWN)
    if value == UNKNOWN:
        return unknown
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, Decimal):
        return value
    return _to_decimal(value)


def _all_known(*values: Any) -> bool:
    return all(value != UNKNOWN for value in values)


def _calculate_profit_factor(
    wins: int,
    losses: int,
    average_win: Decimal,
    average_loss: Decimal,
) -> Decimal:
    gross_win = Decimal(wins) * average_win
    gross_loss = Decimal(losses) * average_loss
    if gross_loss == Decimal("0"):
        if gross_win > Decimal("0"):
            return Decimal("Infinity")
        return Decimal("0")
    return gross_win / gross_loss


def _top_promotion(result: ProfitProofLedgerResult) -> str:
    if result.top_candidate is None:
        return "NONE"
    return result.top_candidate.promotion_recommendation


def _pass_fail_unknown(value: Any) -> str:
    if value is True:
        return "PASS"
    if value is False:
        return "FAIL"
    return UNKNOWN


def _decay_status(value: Any) -> str:
    if value is False:
        return "NO_DECAY_DETECTED"
    if value is True:
        return "DECAY_DETECTED"
    return UNKNOWN


def _string_or_default(value: Any, default: str) -> str:
    if _is_missing(value):
        return default
    return str(value).strip()


def _decimal_or_unknown(value: Any, *, absolute: bool = False) -> Decimal | str:
    if _is_missing(value):
        return UNKNOWN
    parsed = _to_decimal(value)
    if absolute:
        return abs(parsed)
    return parsed


def _int_or_unknown(value: Any) -> int | str:
    if _is_missing(value):
        return UNKNOWN
    return _to_non_negative_int(value)


def _bool_or_unknown(value: Any) -> bool | str:
    if _is_missing(value):
        return UNKNOWN
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "pass", "passed", "clear", "cleared", "reconciled"}:
            return True
        if lowered in {"false", "0", "no", "n", "fail", "failed", "blocked"}:
            return False
        if lowered == "unknown":
            return UNKNOWN
    if isinstance(value, int) and value in {0, 1}:
        return bool(value)
    return UNKNOWN


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


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        if value.is_infinite():
            return "Infinity"
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _bool_text(value: bool) -> str:
    return "true" if value else "false"
