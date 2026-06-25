"""Local-only AIOS Forex Strategy Proof Engine V1.

This module ranks deterministic Forex strategy seed evidence and reports the
strongest candidate for operator proof review. It does not call brokers, read
credentials, read .env files, use network access, place orders, approve real
money, approve compounding, or move money.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from decimal import Decimal, InvalidOperation, getcontext
from enum import Enum
from typing import Any, Mapping, Sequence


getcontext().prec = 28

STRATEGY_PROOF_ENGINE_VERSION = "strategy_proof_engine_v1"

STRATEGY_PROOF_ENGINE_REVIEW_READY = "STRATEGY_PROOF_ENGINE_REVIEW_READY"
STRATEGY_PROOF_ENGINE_MORE_PROOF_REQUIRED = (
    "STRATEGY_PROOF_ENGINE_MORE_PROOF_REQUIRED"
)
STRATEGY_PROOF_ENGINE_BLOCKED_NO_STRATEGY = (
    "STRATEGY_PROOF_ENGINE_BLOCKED_NO_STRATEGY"
)

STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY = (
    "PROMOTE_TO_STRATEGY_PROOF_REVIEW_ONLY"
)
STRATEGY_RECOMMENDATION_IMPROVE = "IMPROVE_PROOF_BEFORE_REVIEW"
STRATEGY_RECOMMENDATION_REJECT = "REJECT_FOR_NOW"

STRATEGY_SEEDS = (
    ("supertrend", "Supertrend"),
    ("ema_crossover", "EMA Crossover"),
    ("vwap_bias", "VWAP Bias"),
    ("donchian_breakout", "Donchian Breakout"),
    ("atr_trend_filter", "ATR Trend Filter"),
    ("adx_trend_filter", "ADX Trend Filter"),
    ("rsi_mean_reversion", "RSI Mean Reversion"),
    ("macd_confirmation", "MACD Confirmation"),
    ("market_structure_break", "Market Structure Break"),
    ("multi_timeframe_alignment", "Multi-Timeframe Alignment"),
)

REQUIRED_STRATEGY_OUTPUT_FIELDS = (
    "strategy_id",
    "strategy_name",
    "total_trades",
    "wins",
    "losses",
    "win_rate",
    "realized_pl",
    "expectancy",
    "profit_factor",
    "max_drawdown",
    "consecutive_losses",
    "confidence_score",
    "proof_score",
    "recommendation",
    "blockers",
    "next_safe_action",
)


@dataclass(frozen=True)
class StrategyProofConfig:
    """Thresholds for local-only strategy proof ranking."""

    minimum_total_trades: int = 30
    minimum_profit_factor: Decimal | str | int | float = Decimal("1.25")
    maximum_drawdown: Decimal | str | int | float = Decimal("0.050")
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
    def from_mapping(cls, raw: Mapping[str, Any]) -> "StrategyProofConfig":
        return cls(
            minimum_total_trades=raw.get(
                "minimum_total_trades", cls.minimum_total_trades
            ),
            minimum_profit_factor=raw.get(
                "minimum_profit_factor", cls.minimum_profit_factor
            ),
            maximum_drawdown=raw.get("maximum_drawdown", cls.maximum_drawdown),
            maximum_consecutive_losses=raw.get(
                "maximum_consecutive_losses", cls.maximum_consecutive_losses
            ),
            minimum_market_regimes=raw.get(
                "minimum_market_regimes", cls.minimum_market_regimes
            ),
        )


@dataclass(frozen=True)
class StrategySeedEvidence:
    """Raw or normalized evidence for one strategy seed."""

    strategy_id: Any = None
    strategy_name: Any = None
    total_trades: Any = None
    wins: Any = None
    losses: Any = None
    realized_pl: Any = None
    expectancy: Any = None
    profit_factor: Any = None
    max_drawdown: Any = None
    consecutive_losses: Any = None
    walk_forward_passed: Any = None
    out_of_sample_passed: Any = None
    market_regime_coverage: Any = None
    spread_sensitivity_passed: Any = None
    slippage_sensitivity_passed: Any = None
    latency_sensitivity_passed: Any = None
    risk_controls_present: Any = None
    notes: Any = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "StrategySeedEvidence":
        return cls(
            strategy_id=raw.get("strategy_id", raw.get("candidate_id")),
            strategy_name=raw.get("strategy_name"),
            total_trades=raw.get("total_trades"),
            wins=raw.get("wins"),
            losses=raw.get("losses"),
            realized_pl=raw.get("realized_pl", raw.get("realized_pl_total")),
            expectancy=raw.get("expectancy"),
            profit_factor=raw.get("profit_factor"),
            max_drawdown=raw.get("max_drawdown"),
            consecutive_losses=raw.get("consecutive_losses"),
            walk_forward_passed=raw.get("walk_forward_passed"),
            out_of_sample_passed=raw.get("out_of_sample_passed"),
            market_regime_coverage=raw.get("market_regime_coverage"),
            spread_sensitivity_passed=raw.get("spread_sensitivity_passed"),
            slippage_sensitivity_passed=raw.get("slippage_sensitivity_passed"),
            latency_sensitivity_passed=raw.get("latency_sensitivity_passed"),
            risk_controls_present=raw.get("risk_controls_present"),
            notes=raw.get("notes"),
        )


@dataclass(frozen=True)
class StrategyProofCandidate:
    """Per-strategy deterministic proof output."""

    rank: int | None
    strategy_id: str
    strategy_name: str
    total_trades: int
    wins: int
    losses: int
    win_rate: Decimal
    realized_pl: Decimal
    expectancy: Decimal
    profit_factor: Decimal
    max_drawdown: Decimal
    consecutive_losses: int
    confidence_score: Decimal
    proof_score: Decimal
    recommendation: str
    blockers: tuple[str, ...]
    next_safe_action: str

    @property
    def review_ready(self) -> bool:
        return self.recommendation == STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY


@dataclass(frozen=True)
class StrategyProofEngineResult:
    """Full strategy proof engine result."""

    engine_version: str
    result_status: str
    top_strategy: StrategyProofCandidate | None
    supertrend_status: Mapping[str, Any]
    top_expectancy: Decimal
    top_profit_factor: Decimal
    safest_candidate: StrategyProofCandidate | None
    fastest_candidate_to_prove: StrategyProofCandidate | None
    strategies_to_improve: tuple[StrategyProofCandidate, ...]
    strategies_to_reject: tuple[StrategyProofCandidate, ...]
    strategy_results: tuple[StrategyProofCandidate, ...]
    demo_trade_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    permissions: Mapping[str, bool]
    blockers: tuple[str, ...]
    next_safe_action: str
    operator_answer: str


def build_strategy_seed_catalog() -> tuple[dict[str, str], ...]:
    """Return the ten required strategy seed identifiers and display names."""

    return tuple(
        {"strategy_id": strategy_id, "strategy_name": strategy_name}
        for strategy_id, strategy_name in STRATEGY_SEEDS
    )


def build_sample_mixed_strategy_evidence() -> tuple[StrategySeedEvidence, ...]:
    """Return deterministic mixed evidence with Supertrend as the top seed."""

    return tuple(
        StrategySeedEvidence.from_mapping(raw)
        for raw in (
            {
                "strategy_id": "supertrend",
                "strategy_name": "Supertrend",
                "total_trades": 72,
                "wins": 47,
                "losses": 25,
                "realized_pl": "34.80",
                "expectancy": "0.4833",
                "profit_factor": "1.82",
                "max_drawdown": "0.024",
                "consecutive_losses": 2,
                "walk_forward_passed": True,
                "out_of_sample_passed": True,
                "market_regime_coverage": 4,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "donchian_breakout",
                "strategy_name": "Donchian Breakout",
                "total_trades": 68,
                "wins": 43,
                "losses": 25,
                "realized_pl": "31.96",
                "expectancy": "0.4700",
                "profit_factor": "1.76",
                "max_drawdown": "0.019",
                "consecutive_losses": 2,
                "walk_forward_passed": True,
                "out_of_sample_passed": True,
                "market_regime_coverage": 4,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "multi_timeframe_alignment",
                "strategy_name": "Multi-Timeframe Alignment",
                "total_trades": 60,
                "wins": 39,
                "losses": 21,
                "realized_pl": "26.40",
                "expectancy": "0.4400",
                "profit_factor": "1.71",
                "max_drawdown": "0.018",
                "consecutive_losses": 2,
                "walk_forward_passed": True,
                "out_of_sample_passed": True,
                "market_regime_coverage": 4,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "market_structure_break",
                "strategy_name": "Market Structure Break",
                "total_trades": 54,
                "wins": 33,
                "losses": 21,
                "realized_pl": "17.28",
                "expectancy": "0.3200",
                "profit_factor": "1.52",
                "max_drawdown": "0.027",
                "consecutive_losses": 2,
                "walk_forward_passed": True,
                "out_of_sample_passed": True,
                "market_regime_coverage": 3,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "atr_trend_filter",
                "strategy_name": "ATR Trend Filter",
                "total_trades": 44,
                "wins": 25,
                "losses": 19,
                "realized_pl": "9.68",
                "expectancy": "0.2200",
                "profit_factor": "1.38",
                "max_drawdown": "0.031",
                "consecutive_losses": 3,
                "walk_forward_passed": True,
                "out_of_sample_passed": False,
                "market_regime_coverage": 3,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "adx_trend_filter",
                "strategy_name": "ADX Trend Filter",
                "total_trades": 36,
                "wins": 21,
                "losses": 15,
                "realized_pl": "7.20",
                "expectancy": "0.2000",
                "profit_factor": "1.45",
                "max_drawdown": "0.041",
                "consecutive_losses": 3,
                "walk_forward_passed": True,
                "out_of_sample_passed": False,
                "market_regime_coverage": 2,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "ema_crossover",
                "strategy_name": "EMA Crossover",
                "total_trades": 42,
                "wins": 23,
                "losses": 19,
                "realized_pl": "5.04",
                "expectancy": "0.1200",
                "profit_factor": "1.18",
                "max_drawdown": "0.029",
                "consecutive_losses": 3,
                "walk_forward_passed": True,
                "out_of_sample_passed": False,
                "market_regime_coverage": 3,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": False,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "vwap_bias",
                "strategy_name": "VWAP Bias",
                "total_trades": 30,
                "wins": 16,
                "losses": 14,
                "realized_pl": "3.30",
                "expectancy": "0.1100",
                "profit_factor": "1.16",
                "max_drawdown": "0.026",
                "consecutive_losses": 3,
                "walk_forward_passed": False,
                "out_of_sample_passed": False,
                "market_regime_coverage": 2,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "macd_confirmation",
                "strategy_name": "MACD Confirmation",
                "total_trades": 28,
                "wins": 14,
                "losses": 14,
                "realized_pl": "1.40",
                "expectancy": "0.0500",
                "profit_factor": "1.08",
                "max_drawdown": "0.034",
                "consecutive_losses": 4,
                "walk_forward_passed": False,
                "out_of_sample_passed": False,
                "market_regime_coverage": 2,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": False,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
            {
                "strategy_id": "rsi_mean_reversion",
                "strategy_name": "RSI Mean Reversion",
                "total_trades": 40,
                "wins": 18,
                "losses": 22,
                "realized_pl": "-5.20",
                "expectancy": "-0.1300",
                "profit_factor": "0.82",
                "max_drawdown": "0.045",
                "consecutive_losses": 5,
                "walk_forward_passed": False,
                "out_of_sample_passed": False,
                "market_regime_coverage": 2,
                "spread_sensitivity_passed": False,
                "slippage_sensitivity_passed": False,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            },
        )
    )


def build_sample_all_blocked_strategy_evidence() -> tuple[StrategySeedEvidence, ...]:
    """Return deterministic evidence where every strategy remains blocked."""

    blocked = []
    for index, (strategy_id, strategy_name) in enumerate(STRATEGY_SEEDS):
        blocked.append(
            StrategySeedEvidence.from_mapping(
                {
                    "strategy_id": strategy_id,
                    "strategy_name": strategy_name,
                    "total_trades": 18 + index,
                    "wins": 7 + index // 2,
                    "losses": 11 + index // 2,
                    "realized_pl": "-2.40",
                    "expectancy": "-0.0800",
                    "profit_factor": "0.92",
                    "max_drawdown": "0.060",
                    "consecutive_losses": 5,
                    "walk_forward_passed": False,
                    "out_of_sample_passed": False,
                    "market_regime_coverage": 1,
                    "spread_sensitivity_passed": False,
                    "slippage_sensitivity_passed": False,
                    "latency_sensitivity_passed": True,
                    "risk_controls_present": True,
                }
            )
        )
    return tuple(blocked)


def evaluate_strategy_proof_candidate(
    evidence: StrategySeedEvidence | Mapping[str, Any] | None = None,
    config: StrategyProofConfig | Mapping[str, Any] | None = None,
) -> StrategyProofCandidate:
    """Evaluate one strategy evidence record without inventing missing proof."""

    active_config = _coerce_config(config)
    raw = _coerce_evidence(evidence)
    normalized = _normalize_evidence(raw)
    proof_flags = _build_proof_flags(normalized, active_config)
    blockers = _candidate_blockers(normalized, proof_flags, active_config)
    proof_score = _score_proof(proof_flags)
    confidence_score = _score_confidence(normalized, proof_score)
    recommendation = _recommendation(normalized, proof_flags, blockers, active_config)

    return StrategyProofCandidate(
        rank=None,
        strategy_id=normalized["strategy_id"],
        strategy_name=normalized["strategy_name"],
        total_trades=normalized["total_trades"],
        wins=normalized["wins"],
        losses=normalized["losses"],
        win_rate=normalized["win_rate"],
        realized_pl=normalized["realized_pl"],
        expectancy=normalized["expectancy"],
        profit_factor=normalized["profit_factor"],
        max_drawdown=normalized["max_drawdown"],
        consecutive_losses=normalized["consecutive_losses"],
        confidence_score=confidence_score,
        proof_score=proof_score,
        recommendation=recommendation,
        blockers=tuple(blockers),
        next_safe_action=_candidate_next_safe_action(recommendation),
    )


def evaluate_strategy_proof_engine(
    evidence_records: Sequence[StrategySeedEvidence | Mapping[str, Any]] | None = None,
    config: StrategyProofConfig | Mapping[str, Any] | None = None,
) -> StrategyProofEngineResult:
    """Evaluate and rank strategy seeds for operator proof review."""

    records = (
        tuple(evidence_records)
        if evidence_records is not None
        else build_sample_mixed_strategy_evidence()
    )
    candidates = tuple(
        evaluate_strategy_proof_candidate(record, config) for record in records
    )
    ranked = _rank_candidates(candidates)
    top_strategy = ranked[0] if ranked else None
    review_ready = tuple(candidate for candidate in ranked if candidate.review_ready)
    strategies_to_improve = tuple(
        candidate
        for candidate in ranked
        if candidate.recommendation == STRATEGY_RECOMMENDATION_IMPROVE
    )
    strategies_to_reject = tuple(
        candidate
        for candidate in ranked
        if candidate.recommendation == STRATEGY_RECOMMENDATION_REJECT
    )
    safest_candidate = _safest_candidate(ranked)
    fastest_candidate = _fastest_candidate_to_prove(ranked)
    permissions = _permissions()
    result_status = _result_status(ranked, review_ready)

    return StrategyProofEngineResult(
        engine_version=STRATEGY_PROOF_ENGINE_VERSION,
        result_status=result_status,
        top_strategy=top_strategy,
        supertrend_status=_supertrend_status(ranked, top_strategy),
        top_expectancy=top_strategy.expectancy if top_strategy else Decimal("0"),
        top_profit_factor=top_strategy.profit_factor if top_strategy else Decimal("0"),
        safest_candidate=safest_candidate,
        fastest_candidate_to_prove=fastest_candidate,
        strategies_to_improve=strategies_to_improve,
        strategies_to_reject=strategies_to_reject,
        strategy_results=ranked,
        demo_trade_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        live_trading_allowed=False,
        permissions=permissions,
        blockers=_engine_blockers(ranked, result_status),
        next_safe_action=_engine_next_safe_action(result_status, top_strategy),
        operator_answer=_operator_answer(result_status, top_strategy),
    )


def result_to_operator_text(result: StrategyProofEngineResult | None = None) -> str:
    """Return deterministic operator-readable proof output."""

    active = result if result is not None else evaluate_strategy_proof_engine()
    top_id = active.top_strategy.strategy_id if active.top_strategy else "NONE"
    safest_id = active.safest_candidate.strategy_id if active.safest_candidate else "NONE"
    fastest_id = (
        active.fastest_candidate_to_prove.strategy_id
        if active.fastest_candidate_to_prove
        else "NONE"
    )
    lines = [
        "AIOS Forex Strategy Proof Engine V1",
        f"result_status: {active.result_status}",
        f"top_strategy: {top_id}",
        f"supertrend_status: {active.supertrend_status['status']}",
        f"supertrend_rank: {active.supertrend_status['rank']}",
        f"top_expectancy: {_json_value(active.top_expectancy)}",
        f"top_profit_factor: {_json_value(active.top_profit_factor)}",
        f"safest_candidate: {safest_id}",
        f"fastest_candidate_to_prove: {fastest_id}",
        f"demo_trade_allowed: {_bool_text(active.demo_trade_allowed)}",
        f"broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
        f"real_money_allowed: {_bool_text(active.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(active.compounding_allowed)}",
        f"bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
        f"live_trading_allowed: {_bool_text(active.live_trading_allowed)}",
        "rankings:",
    ]
    for candidate in active.strategy_results:
        lines.append(
            "- rank "
            f"{candidate.rank}: {candidate.strategy_id} "
            f"expectancy={_json_value(candidate.expectancy)} "
            f"profit_factor={_json_value(candidate.profit_factor)} "
            f"recommendation={candidate.recommendation}"
        )
    lines.extend(
        [
            "strategies_to_improve: "
            + _strategy_id_list(active.strategies_to_improve),
            "strategies_to_reject: " + _strategy_id_list(active.strategies_to_reject),
            f"next_safe_action: {active.next_safe_action}",
            f"operator_answer: {active.operator_answer}",
        ]
    )
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(
    result: StrategyProofEngineResult | None = None,
) -> dict[str, Any]:
    """Return deterministic JSON-safe strategy proof data."""

    active = result if result is not None else evaluate_strategy_proof_engine()
    return {
        "engine_version": active.engine_version,
        "result_status": active.result_status,
        "top_strategy": _candidate_to_jsonable(active.top_strategy),
        "supertrend_status": _json_value(active.supertrend_status),
        "top_expectancy": _json_value(active.top_expectancy),
        "top_profit_factor": _json_value(active.top_profit_factor),
        "safest_candidate": _candidate_to_jsonable(active.safest_candidate),
        "fastest_candidate_to_prove": _candidate_to_jsonable(
            active.fastest_candidate_to_prove
        ),
        "strategies_to_improve": [
            _candidate_to_jsonable(candidate) for candidate in active.strategies_to_improve
        ],
        "strategies_to_reject": [
            _candidate_to_jsonable(candidate) for candidate in active.strategies_to_reject
        ],
        "strategy_results": [
            _candidate_to_jsonable(candidate) for candidate in active.strategy_results
        ],
        "permissions": dict(active.permissions),
        "demo_trade_allowed": active.demo_trade_allowed,
        "broker_action_allowed": active.broker_action_allowed,
        "real_money_allowed": active.real_money_allowed,
        "compounding_allowed": active.compounding_allowed,
        "bank_movement_allowed": active.bank_movement_allowed,
        "live_trading_allowed": active.live_trading_allowed,
        "blockers": list(active.blockers),
        "next_safe_action": active.next_safe_action,
        "operator_answer": active.operator_answer,
        "safety": {
            "local_only": True,
            "network_calls": False,
            "subprocess_calls": False,
            "broker_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "repo_mutation": False,
            "order_placement": False,
            "live_trading_enablement": False,
        },
    }


def strategy_proof_to_markdown(result: StrategyProofEngineResult | None = None) -> str:
    """Return readable strategy proof markdown."""

    active = result if result is not None else evaluate_strategy_proof_engine()
    top_id = active.top_strategy.strategy_id if active.top_strategy else "NONE"
    lines = [
        "# AIOS Forex Strategy Proof Engine V1",
        "",
        "## Summary",
        f"- result_status: {active.result_status}",
        f"- top_strategy: {top_id}",
        f"- supertrend_status: {active.supertrend_status['status']}",
        f"- top_expectancy: {_json_value(active.top_expectancy)}",
        f"- top_profit_factor: {_json_value(active.top_profit_factor)}",
        "",
        "## Rankings",
    ]
    for candidate in active.strategy_results:
        blocker_text = "; ".join(candidate.blockers) if candidate.blockers else "none"
        lines.append(
            "- rank "
            f"{candidate.rank}: {candidate.strategy_id} "
            f"expectancy={_json_value(candidate.expectancy)} "
            f"profit_factor={_json_value(candidate.profit_factor)} "
            f"proof_score={_json_value(candidate.proof_score)} "
            f"recommendation={candidate.recommendation} "
            f"blockers={blocker_text}"
        )
    lines.extend(
        [
            "",
            "## Safety Locks",
            f"- demo_trade_allowed: {_bool_text(active.demo_trade_allowed)}",
            f"- broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
            f"- real_money_allowed: {_bool_text(active.real_money_allowed)}",
            f"- compounding_allowed: {_bool_text(active.compounding_allowed)}",
            f"- bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
            f"- live_trading_allowed: {_bool_text(active.live_trading_allowed)}",
            "",
            "## Next Safe Action",
            active.next_safe_action,
            "",
        ]
    )
    return "\n".join(lines)


def _coerce_config(
    raw: StrategyProofConfig | Mapping[str, Any] | None,
) -> StrategyProofConfig:
    if isinstance(raw, StrategyProofConfig):
        return raw
    if raw is None:
        return StrategyProofConfig()
    if isinstance(raw, Mapping):
        return StrategyProofConfig.from_mapping(raw)
    raise TypeError("unsupported strategy proof config")


def _coerce_evidence(
    raw: StrategySeedEvidence | Mapping[str, Any] | None,
) -> StrategySeedEvidence:
    if isinstance(raw, StrategySeedEvidence):
        return raw
    if raw is None:
        return StrategySeedEvidence()
    if isinstance(raw, Mapping):
        return StrategySeedEvidence.from_mapping(raw)
    raise TypeError("unsupported strategy evidence")


def _normalize_evidence(evidence: StrategySeedEvidence) -> dict[str, Any]:
    strategy_id = _string_or_default(evidence.strategy_id, "unknown_strategy")
    strategy_name = _string_or_default(evidence.strategy_name, strategy_id)
    total_trades = _to_non_negative_int(evidence.total_trades or 0)
    wins = _to_non_negative_int(evidence.wins or 0)
    losses = _to_non_negative_int(evidence.losses or 0)
    return {
        "strategy_id": strategy_id,
        "strategy_name": strategy_name,
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": _ratio(wins, total_trades),
        "realized_pl": _to_decimal(evidence.realized_pl or 0),
        "expectancy": _to_decimal(evidence.expectancy or 0),
        "profit_factor": _to_decimal(evidence.profit_factor or 0),
        "max_drawdown": abs(_to_decimal(evidence.max_drawdown or 0)),
        "consecutive_losses": _to_non_negative_int(evidence.consecutive_losses or 0),
        "walk_forward_passed": _bool_or_unknown(evidence.walk_forward_passed),
        "out_of_sample_passed": _bool_or_unknown(evidence.out_of_sample_passed),
        "market_regime_coverage": _to_non_negative_int(
            evidence.market_regime_coverage or 0
        ),
        "spread_sensitivity_passed": _bool_or_unknown(
            evidence.spread_sensitivity_passed
        ),
        "slippage_sensitivity_passed": _bool_or_unknown(
            evidence.slippage_sensitivity_passed
        ),
        "latency_sensitivity_passed": _bool_or_unknown(
            evidence.latency_sensitivity_passed
        ),
        "risk_controls_present": _bool_or_unknown(evidence.risk_controls_present),
    }


def _build_proof_flags(
    normalized: Mapping[str, Any],
    config: StrategyProofConfig,
) -> dict[str, bool]:
    return {
        "sample_depth": normalized["total_trades"] >= config.minimum_total_trades,
        "positive_expectancy": normalized["expectancy"] > Decimal("0"),
        "profit_factor": normalized["profit_factor"] >= config.minimum_profit_factor,
        "drawdown_within_limit": normalized["max_drawdown"] <= config.maximum_drawdown,
        "consecutive_losses_within_limit": normalized["consecutive_losses"]
        <= config.maximum_consecutive_losses,
        "walk_forward_passed": normalized["walk_forward_passed"] is True,
        "out_of_sample_passed": normalized["out_of_sample_passed"] is True,
        "market_regime_coverage": normalized["market_regime_coverage"]
        >= config.minimum_market_regimes,
        "spread_sensitivity_passed": normalized["spread_sensitivity_passed"] is True,
        "slippage_sensitivity_passed": normalized["slippage_sensitivity_passed"] is True,
        "latency_sensitivity_passed": normalized["latency_sensitivity_passed"] is True,
        "risk_controls_present": normalized["risk_controls_present"] is True,
    }


def _candidate_blockers(
    normalized: Mapping[str, Any],
    proof_flags: Mapping[str, bool],
    config: StrategyProofConfig,
) -> list[str]:
    blockers: list[str] = []
    if not proof_flags["sample_depth"]:
        blockers.append(
            f"sample depth below {config.minimum_total_trades} trades"
        )
    if not proof_flags["positive_expectancy"]:
        blockers.append("expectancy is not positive")
    if not proof_flags["profit_factor"]:
        blockers.append(
            f"profit factor below {config.minimum_profit_factor}"
        )
    if not proof_flags["drawdown_within_limit"]:
        blockers.append(f"max drawdown above {config.maximum_drawdown}")
    if not proof_flags["consecutive_losses_within_limit"]:
        blockers.append(
            f"consecutive losses above {config.maximum_consecutive_losses}"
        )
    if not proof_flags["walk_forward_passed"]:
        blockers.append("walk-forward proof has not passed")
    if not proof_flags["out_of_sample_passed"]:
        blockers.append("out-of-sample proof has not passed")
    if not proof_flags["market_regime_coverage"]:
        blockers.append(
            f"market regime coverage below {config.minimum_market_regimes}"
        )
    if not proof_flags["spread_sensitivity_passed"]:
        blockers.append("spread sensitivity proof has not passed")
    if not proof_flags["slippage_sensitivity_passed"]:
        blockers.append("slippage sensitivity proof has not passed")
    if not proof_flags["latency_sensitivity_passed"]:
        blockers.append("latency sensitivity proof has not passed")
    if not proof_flags["risk_controls_present"]:
        blockers.append("risk controls are not proven")
    if normalized["wins"] + normalized["losses"] != normalized["total_trades"]:
        blockers.append("wins plus losses does not match total trades")
    return list(dict.fromkeys(blockers))


def _score_proof(proof_flags: Mapping[str, bool]) -> Decimal:
    total = Decimal(len(proof_flags))
    passed = Decimal(sum(1 for value in proof_flags.values() if value is True))
    if total == Decimal("0"):
        return Decimal("0.00")
    return (passed / total * Decimal("100")).quantize(Decimal("0.01"))


def _score_confidence(
    normalized: Mapping[str, Any],
    proof_score: Decimal,
) -> Decimal:
    raw = (
        proof_score * Decimal("0.45")
        + min(Decimal(normalized["total_trades"]), Decimal("120")) / Decimal("120") * Decimal("20")
        + max(Decimal("0"), normalized["expectancy"]) * Decimal("30")
        + max(Decimal("0"), normalized["profit_factor"] - Decimal("1")) * Decimal("10")
        - normalized["max_drawdown"] * Decimal("120")
        - Decimal(normalized["consecutive_losses"]) * Decimal("1.5")
    )
    return min(Decimal("100"), max(Decimal("0"), raw)).quantize(Decimal("0.01"))


def _recommendation(
    normalized: Mapping[str, Any],
    proof_flags: Mapping[str, bool],
    blockers: Sequence[str],
    config: StrategyProofConfig,
) -> str:
    if all(proof_flags.values()) and not blockers:
        return STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY
    if (
        normalized["expectancy"] <= Decimal("0")
        or normalized["profit_factor"] < Decimal("1")
        or normalized["max_drawdown"] > config.maximum_drawdown * Decimal("1.5")
        or normalized["consecutive_losses"] > config.maximum_consecutive_losses + 1
    ):
        return STRATEGY_RECOMMENDATION_REJECT
    return STRATEGY_RECOMMENDATION_IMPROVE


def _rank_candidates(
    candidates: Sequence[StrategyProofCandidate],
) -> tuple[StrategyProofCandidate, ...]:
    ranked = sorted(
        candidates,
        key=lambda candidate: (
            _recommendation_rank(candidate.recommendation),
            -candidate.confidence_score,
            -candidate.proof_score,
            -candidate.expectancy,
            -candidate.profit_factor,
            candidate.max_drawdown,
            -Decimal(candidate.total_trades),
            candidate.strategy_id,
        ),
    )
    return tuple(
        _replace_rank(candidate, rank=index)
        for index, candidate in enumerate(ranked, start=1)
    )


def _replace_rank(candidate: StrategyProofCandidate, *, rank: int) -> StrategyProofCandidate:
    return StrategyProofCandidate(
        rank=rank,
        strategy_id=candidate.strategy_id,
        strategy_name=candidate.strategy_name,
        total_trades=candidate.total_trades,
        wins=candidate.wins,
        losses=candidate.losses,
        win_rate=candidate.win_rate,
        realized_pl=candidate.realized_pl,
        expectancy=candidate.expectancy,
        profit_factor=candidate.profit_factor,
        max_drawdown=candidate.max_drawdown,
        consecutive_losses=candidate.consecutive_losses,
        confidence_score=candidate.confidence_score,
        proof_score=candidate.proof_score,
        recommendation=candidate.recommendation,
        blockers=candidate.blockers,
        next_safe_action=candidate.next_safe_action,
    )


def _recommendation_rank(recommendation: str) -> int:
    return {
        STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY: 0,
        STRATEGY_RECOMMENDATION_IMPROVE: 1,
        STRATEGY_RECOMMENDATION_REJECT: 2,
    }.get(recommendation, 3)


def _safest_candidate(
    ranked: Sequence[StrategyProofCandidate],
) -> StrategyProofCandidate | None:
    candidates = [
        candidate
        for candidate in ranked
        if candidate.recommendation != STRATEGY_RECOMMENDATION_REJECT
    ] or list(ranked)
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda candidate: (
            candidate.max_drawdown,
            -candidate.proof_score,
            -candidate.expectancy,
            candidate.strategy_id,
        ),
    )[0]


def _fastest_candidate_to_prove(
    ranked: Sequence[StrategyProofCandidate],
) -> StrategyProofCandidate | None:
    candidates = [
        candidate
        for candidate in ranked
        if candidate.recommendation != STRATEGY_RECOMMENDATION_REJECT
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda candidate: (
            len(candidate.blockers),
            _recommendation_rank(candidate.recommendation),
            -candidate.proof_score,
            -candidate.expectancy,
            candidate.strategy_id,
        ),
    )[0]


def _result_status(
    ranked: Sequence[StrategyProofCandidate],
    review_ready: Sequence[StrategyProofCandidate],
) -> str:
    if review_ready:
        return STRATEGY_PROOF_ENGINE_REVIEW_READY
    if ranked:
        return STRATEGY_PROOF_ENGINE_MORE_PROOF_REQUIRED
    return STRATEGY_PROOF_ENGINE_BLOCKED_NO_STRATEGY


def _supertrend_status(
    ranked: Sequence[StrategyProofCandidate],
    top_strategy: StrategyProofCandidate | None,
) -> dict[str, Any]:
    supertrend = next(
        (candidate for candidate in ranked if candidate.strategy_id == "supertrend"),
        None,
    )
    if supertrend is None:
        return {
            "strategy_id": "supertrend",
            "status": "SUPER_TREND_MISSING",
            "rank": None,
            "is_top_strategy": False,
            "good_enough_for_strategy_review": False,
            "good_enough_for_22_6_operation": False,
            "improvement_reason": "Supertrend evidence is missing.",
            "blockers": ["Supertrend evidence is missing"],
        }
    is_top = top_strategy is not None and top_strategy.strategy_id == "supertrend"
    if supertrend.review_ready and is_top:
        improvement_reason = (
            "Supertrend is the top proof-review seed; 22/6 operation still needs "
            "longer supervised availability evidence."
        )
    elif supertrend.review_ready:
        improvement_reason = (
            "Supertrend is proof-review ready, but another strategy currently "
            "ranks higher on the deterministic proof score."
        )
    else:
        improvement_reason = "; ".join(supertrend.blockers)
    return {
        "strategy_id": "supertrend",
        "status": "SUPER_TREND_PROOF_REVIEW_READY"
        if supertrend.review_ready
        else "SUPER_TREND_MORE_PROOF_REQUIRED",
        "rank": supertrend.rank,
        "is_top_strategy": is_top,
        "good_enough_for_strategy_review": supertrend.review_ready,
        "good_enough_for_22_6_operation": False,
        "recommendation": supertrend.recommendation,
        "expectancy": supertrend.expectancy,
        "profit_factor": supertrend.profit_factor,
        "blockers": list(supertrend.blockers),
        "improvement_reason": improvement_reason,
    }


def _engine_blockers(
    ranked: Sequence[StrategyProofCandidate],
    result_status: str,
) -> tuple[str, ...]:
    blockers: list[str] = []
    if result_status == STRATEGY_PROOF_ENGINE_BLOCKED_NO_STRATEGY:
        blockers.append("no strategy evidence records were provided")
    if not any(candidate.review_ready for candidate in ranked):
        blockers.append("no strategy has earned proof review")
    blockers.extend(
        (
            "demo trade remains locked",
            "broker action remains locked",
            "real money remains locked",
            "compounding remains locked",
            "bank movement remains locked",
            "live trading remains locked",
        )
    )
    return tuple(dict.fromkeys(blockers))


def _engine_next_safe_action(
    result_status: str,
    top_strategy: StrategyProofCandidate | None,
) -> str:
    if (
        result_status == STRATEGY_PROOF_ENGINE_REVIEW_READY
        and top_strategy is not None
    ):
        return (
            f"Prepare operator proof review for {top_strategy.strategy_id}; keep "
            "22/6 operation, broker action, real money, and compounding locked."
        )
    if result_status == STRATEGY_PROOF_ENGINE_MORE_PROOF_REQUIRED:
        return (
            "Collect missing strategy proof and rerun Strategy Proof Engine V1 "
            "before any readiness promotion."
        )
    return "Add valid strategy evidence before any proof review."


def _operator_answer(
    result_status: str,
    top_strategy: StrategyProofCandidate | None,
) -> str:
    if (
        result_status == STRATEGY_PROOF_ENGINE_REVIEW_READY
        and top_strategy is not None
    ):
        return (
            f"{top_strategy.strategy_name} is the current top proof-review "
            "candidate. This is not a profit guarantee and does not approve a "
            "trade, broker action, real money, compounding, or bank movement."
        )
    return (
        "No strategy is approved for execution. Missing proof must be repaired "
        "before any review path advances."
    )


def _candidate_next_safe_action(recommendation: str) -> str:
    if recommendation == STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY:
        return (
            "Prepare operator proof review only; do not approve 22/6 operation "
            "or broker action."
        )
    if recommendation == STRATEGY_RECOMMENDATION_IMPROVE:
        return "Collect missing proof and rerun the deterministic ranking."
    return "Reject for now and redesign or replace the strategy seed."


def _permissions() -> dict[str, bool]:
    return {
        "demo_trade_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
    }


def _candidate_to_jsonable(
    candidate: StrategyProofCandidate | None,
) -> dict[str, Any] | None:
    if candidate is None:
        return None
    return {
        "rank": candidate.rank,
        "strategy_id": candidate.strategy_id,
        "strategy_name": candidate.strategy_name,
        "total_trades": candidate.total_trades,
        "wins": candidate.wins,
        "losses": candidate.losses,
        "win_rate": _json_value(candidate.win_rate),
        "realized_pl": _json_value(candidate.realized_pl),
        "expectancy": _json_value(candidate.expectancy),
        "profit_factor": _json_value(candidate.profit_factor),
        "max_drawdown": _json_value(candidate.max_drawdown),
        "consecutive_losses": candidate.consecutive_losses,
        "confidence_score": _json_value(candidate.confidence_score),
        "proof_score": _json_value(candidate.proof_score),
        "recommendation": candidate.recommendation,
        "blockers": list(candidate.blockers),
        "next_safe_action": candidate.next_safe_action,
    }


def _strategy_id_list(candidates: Sequence[StrategyProofCandidate]) -> str:
    if not candidates:
        return "none"
    return ", ".join(candidate.strategy_id for candidate in candidates)


def _ratio(numerator: int, denominator: int) -> Decimal:
    if denominator <= 0:
        return Decimal("0.0000")
    return (Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.0001"))


def _string_or_default(value: Any, default: str) -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _bool_or_unknown(value: Any) -> bool | str:
    if value is None:
        return "UNKNOWN"
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "pass", "passed", "clear", "cleared"}:
            return True
        if lowered in {"false", "0", "no", "fail", "failed", "blocked"}:
            return False
    return "UNKNOWN"


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


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
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
