"""Local-only AIOS Forex Trusted Profit 22/6 Readiness V1.

This module consumes Strategy Proof Engine V1 output and answers whether the
current strategy evidence is ready for proof review and whether AIOS has enough
proof for 22 hours/day, 6 days/week supervised operation. It never approves
broker action, real money, compounding, bank movement, or live trading.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping, Sequence

from automation.forex_engine.strategy_proof_engine_v1 import (
    STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY,
    StrategyProofCandidate,
    StrategyProofEngineResult,
    build_sample_all_blocked_strategy_evidence,
    build_sample_mixed_strategy_evidence,
    evaluate_strategy_proof_engine,
    result_to_jsonable_dict as strategy_result_to_jsonable_dict,
)


TRUSTED_PROFIT_22_6_VERSION = "trusted_profit_22_6_readiness_v1"

TRUSTED_PROFIT_22_6_NOT_READY = "TRUSTED_PROFIT_22_6_NOT_READY"
TRUSTED_PROFIT_22_6_MORE_PROOF_REQUIRED = (
    "TRUSTED_PROFIT_22_6_MORE_PROOF_REQUIRED"
)
TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY = (
    "TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY"
)
TRUSTED_PROFIT_22_6_BLOCKED_NO_STRATEGY = (
    "TRUSTED_PROFIT_22_6_BLOCKED_NO_STRATEGY"
)
TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY = (
    "TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY"
)
TRUSTED_PROFIT_22_6_BLOCKED_TOO_MUCH_DRAWDOWN = (
    "TRUSTED_PROFIT_22_6_BLOCKED_TOO_MUCH_DRAWDOWN"
)
TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE = (
    "TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE"
)
TRUSTED_PROFIT_22_6_BLOCKED_REAL_MONEY = (
    "TRUSTED_PROFIT_22_6_BLOCKED_REAL_MONEY"
)
TRUSTED_PROFIT_22_6_BLOCKED_COMPOUNDING = (
    "TRUSTED_PROFIT_22_6_BLOCKED_COMPOUNDING"
)

VALID_READINESS_CLASSIFICATIONS = {
    TRUSTED_PROFIT_22_6_NOT_READY,
    TRUSTED_PROFIT_22_6_MORE_PROOF_REQUIRED,
    TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY,
    TRUSTED_PROFIT_22_6_BLOCKED_NO_STRATEGY,
    TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY,
    TRUSTED_PROFIT_22_6_BLOCKED_TOO_MUCH_DRAWDOWN,
    TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE,
    TRUSTED_PROFIT_22_6_BLOCKED_REAL_MONEY,
    TRUSTED_PROFIT_22_6_BLOCKED_COMPOUNDING,
}

REQUIRED_22_6_PROOF_ITEMS = (
    "strategy_proof_review_completed",
    "minimum_22_6_observation_window",
    "multi_session_coverage",
    "week_open_close_handling",
    "news_filter_validated",
    "spread_expansion_guard_validated",
    "slippage_stress_validated",
    "latency_monitor_validated",
    "drawdown_recovery_review",
    "strategy_decay_monitor_present",
    "paper_demo_reconciliation",
    "risk_envelope_present",
    "kill_switch_present",
    "operator_supervision_plan",
)


@dataclass(frozen=True)
class TrustedProfit226ReadinessConfig:
    """Readiness thresholds for strategy review and 22/6 planning."""

    minimum_strategy_sample: int = 30
    maximum_strategy_drawdown: Decimal | str | int | float = Decimal("0.050")
    minimum_strategy_expectancy: Decimal | str | int | float = Decimal("0")

    def __post_init__(self) -> None:
        object.__setattr__(self, "minimum_strategy_sample", int(self.minimum_strategy_sample))
        object.__setattr__(
            self,
            "maximum_strategy_drawdown",
            Decimal(str(self.maximum_strategy_drawdown)),
        )
        object.__setattr__(
            self,
            "minimum_strategy_expectancy",
            Decimal(str(self.minimum_strategy_expectancy)),
        )


@dataclass(frozen=True)
class TrustedProfit226ReadinessResult:
    """Full readiness output for the 22/6 supervised-operation target."""

    readiness_version: str
    readiness_status: str
    strategy_worth_proof_review: bool
    enough_proof_for_22_6: bool
    missing_proof: tuple[str, ...]
    fastest_safe_next_action: str
    strongest_candidate: StrategyProofCandidate | None
    strongest_candidate_id: str
    supertrend_status: Mapping[str, Any]
    supertrend_good_enough_for_strategy_review: bool
    supertrend_good_enough_for_22_6_operation: bool
    supertrend_answer: str
    real_money_allowed: bool
    compounding_allowed: bool
    broker_action_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    permissions: Mapping[str, bool]
    blockers: tuple[str, ...]
    strategy_proof_summary: Mapping[str, Any]
    next_safe_action: str
    operator_answer: str

    def __post_init__(self) -> None:
        if self.readiness_status not in VALID_READINESS_CLASSIFICATIONS:
            raise ValueError(f"invalid readiness status: {self.readiness_status}")


def build_sample_mixed_strategy_proof_result() -> StrategyProofEngineResult:
    """Return the mixed Strategy Proof Engine sample result."""

    return evaluate_strategy_proof_engine(build_sample_mixed_strategy_evidence())


def build_sample_all_blocked_strategy_proof_result() -> StrategyProofEngineResult:
    """Return the all-blocked Strategy Proof Engine sample result."""

    return evaluate_strategy_proof_engine(build_sample_all_blocked_strategy_evidence())


def evaluate_trusted_profit_22_6_readiness(
    strategy_result: StrategyProofEngineResult | None = None,
    config: TrustedProfit226ReadinessConfig | Mapping[str, Any] | None = None,
) -> TrustedProfit226ReadinessResult:
    """Evaluate whether strategy proof can advance toward 22/6 readiness."""

    active_config = _coerce_config(config)
    active_strategy_result = (
        strategy_result if strategy_result is not None else build_sample_mixed_strategy_proof_result()
    )
    strongest = active_strategy_result.top_strategy
    permissions = _permissions()
    missing_proof = _missing_22_6_proof()
    readiness_status = _readiness_status(
        strongest,
        active_strategy_result.strategy_results,
        active_config,
    )
    worth_review = (
        strongest is not None
        and strongest.recommendation == STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY
    )
    enough_22_6 = False
    supertrend_status = active_strategy_result.supertrend_status
    supertrend_review = bool(
        supertrend_status.get("good_enough_for_strategy_review", False)
    )

    return TrustedProfit226ReadinessResult(
        readiness_version=TRUSTED_PROFIT_22_6_VERSION,
        readiness_status=readiness_status,
        strategy_worth_proof_review=worth_review,
        enough_proof_for_22_6=enough_22_6,
        missing_proof=missing_proof,
        fastest_safe_next_action=_fastest_safe_next_action(
            readiness_status, strongest
        ),
        strongest_candidate=strongest,
        strongest_candidate_id=strongest.strategy_id if strongest else "NONE",
        supertrend_status=supertrend_status,
        supertrend_good_enough_for_strategy_review=supertrend_review,
        supertrend_good_enough_for_22_6_operation=False,
        supertrend_answer=_supertrend_answer(supertrend_status),
        real_money_allowed=False,
        compounding_allowed=False,
        broker_action_allowed=False,
        bank_movement_allowed=False,
        live_trading_allowed=False,
        permissions=permissions,
        blockers=_blockers(readiness_status, missing_proof),
        strategy_proof_summary=_strategy_proof_summary(active_strategy_result),
        next_safe_action=_fastest_safe_next_action(readiness_status, strongest),
        operator_answer=_operator_answer(readiness_status, strongest),
    )


def result_to_operator_text(
    result: TrustedProfit226ReadinessResult | None = None,
) -> str:
    """Return deterministic operator-readable 22/6 readiness output."""

    active = result if result is not None else evaluate_trusted_profit_22_6_readiness()
    lines = [
        "AIOS Forex Trusted Profit 22/6 Readiness V1",
        f"readiness_status: {active.readiness_status}",
        f"strategy_worth_proof_review: {_bool_text(active.strategy_worth_proof_review)}",
        f"enough_proof_for_22_6: {_bool_text(active.enough_proof_for_22_6)}",
        f"strongest_candidate: {active.strongest_candidate_id}",
        f"supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"supertrend_answer: {active.supertrend_answer}",
        f"real_money_allowed: {_bool_text(active.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(active.compounding_allowed)}",
        f"broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
        f"bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
        f"live_trading_allowed: {_bool_text(active.live_trading_allowed)}",
        "missing_proof:",
    ]
    lines.extend(f"- {item}" for item in active.missing_proof)
    lines.extend(
        [
            f"next_safe_action: {active.next_safe_action}",
            f"operator_answer: {active.operator_answer}",
        ]
    )
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(
    result: TrustedProfit226ReadinessResult | None = None,
) -> dict[str, Any]:
    """Return deterministic JSON-safe readiness data."""

    active = result if result is not None else evaluate_trusted_profit_22_6_readiness()
    return {
        "readiness_version": active.readiness_version,
        "readiness_status": active.readiness_status,
        "strategy_worth_proof_review": active.strategy_worth_proof_review,
        "enough_proof_for_22_6": active.enough_proof_for_22_6,
        "missing_proof": list(active.missing_proof),
        "fastest_safe_next_action": active.fastest_safe_next_action,
        "strongest_candidate": _strategy_candidate_to_jsonable(
            active.strongest_candidate
        ),
        "strongest_candidate_id": active.strongest_candidate_id,
        "supertrend_status": _json_value(active.supertrend_status),
        "supertrend_good_enough_for_strategy_review": (
            active.supertrend_good_enough_for_strategy_review
        ),
        "supertrend_good_enough_for_22_6_operation": (
            active.supertrend_good_enough_for_22_6_operation
        ),
        "supertrend_answer": active.supertrend_answer,
        "real_money_allowed": active.real_money_allowed,
        "compounding_allowed": active.compounding_allowed,
        "broker_action_allowed": active.broker_action_allowed,
        "bank_movement_allowed": active.bank_movement_allowed,
        "live_trading_allowed": active.live_trading_allowed,
        "permissions": dict(active.permissions),
        "blockers": list(active.blockers),
        "strategy_proof_summary": _json_value(active.strategy_proof_summary),
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
            "real_money_approval": False,
            "compounding_approval": False,
            "bank_movement_approval": False,
        },
    }


def readiness_to_markdown(
    result: TrustedProfit226ReadinessResult | None = None,
) -> str:
    """Return readable markdown for the 22/6 readiness decision."""

    active = result if result is not None else evaluate_trusted_profit_22_6_readiness()
    lines = [
        "# AIOS Forex Trusted Profit 22/6 Readiness V1",
        "",
        "## Status",
        f"- readiness_status: {active.readiness_status}",
        f"- 22/6 target: supervised availability, not trade approval",
        f"- strongest_candidate: {active.strongest_candidate_id}",
        f"- strategy_worth_proof_review: {_bool_text(active.strategy_worth_proof_review)}",
        f"- enough_proof_for_22_6: {_bool_text(active.enough_proof_for_22_6)}",
        f"- supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"- supertrend_answer: {active.supertrend_answer}",
        "",
        "## Missing Proof",
    ]
    lines.extend(f"- {item}" for item in active.missing_proof)
    lines.extend(
        [
            "",
            "## Safety Locks",
            f"- real_money_allowed: {_bool_text(active.real_money_allowed)}",
            f"- compounding_allowed: {_bool_text(active.compounding_allowed)}",
            f"- broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
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
    raw: TrustedProfit226ReadinessConfig | Mapping[str, Any] | None,
) -> TrustedProfit226ReadinessConfig:
    if isinstance(raw, TrustedProfit226ReadinessConfig):
        return raw
    if raw is None:
        return TrustedProfit226ReadinessConfig()
    if isinstance(raw, Mapping):
        return TrustedProfit226ReadinessConfig(
            minimum_strategy_sample=raw.get("minimum_strategy_sample", 30),
            maximum_strategy_drawdown=raw.get("maximum_strategy_drawdown", "0.050"),
            minimum_strategy_expectancy=raw.get("minimum_strategy_expectancy", "0"),
        )
    raise TypeError("unsupported 22/6 readiness config")


def _readiness_status(
    strongest: StrategyProofCandidate | None,
    strategy_results: Sequence[StrategyProofCandidate],
    config: TrustedProfit226ReadinessConfig,
) -> str:
    if strongest is None or not strategy_results:
        return TRUSTED_PROFIT_22_6_BLOCKED_NO_STRATEGY
    if not any(candidate.expectancy > config.minimum_strategy_expectancy for candidate in strategy_results):
        return TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY
    if strongest.total_trades < config.minimum_strategy_sample:
        return TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE
    if strongest.max_drawdown > config.maximum_strategy_drawdown:
        return TRUSTED_PROFIT_22_6_BLOCKED_TOO_MUCH_DRAWDOWN
    if strongest.recommendation == STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY:
        return TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY
    if strongest.expectancy > config.minimum_strategy_expectancy:
        return TRUSTED_PROFIT_22_6_MORE_PROOF_REQUIRED
    return TRUSTED_PROFIT_22_6_NOT_READY


def _missing_22_6_proof() -> tuple[str, ...]:
    return REQUIRED_22_6_PROOF_ITEMS


def _fastest_safe_next_action(
    readiness_status: str,
    strongest: StrategyProofCandidate | None,
) -> str:
    if readiness_status == TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY and strongest:
        return (
            f"Prepare a proof-review packet for {strongest.strategy_id}; collect "
            "22/6 observation evidence before any operation approval."
        )
    if readiness_status == TRUSTED_PROFIT_22_6_MORE_PROOF_REQUIRED:
        return "Close the missing strategy proof blockers and rerun readiness."
    if readiness_status == TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE:
        return "Collect more governed sample trades before any proof review."
    if readiness_status == TRUSTED_PROFIT_22_6_BLOCKED_TOO_MUCH_DRAWDOWN:
        return "Reduce drawdown or reject the strategy before 22/6 planning."
    if readiness_status == TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY:
        return "Reject negative-expectancy strategy evidence and find a better seed."
    return "Add a valid strategy proof candidate before 22/6 readiness planning."


def _supertrend_answer(supertrend_status: Mapping[str, Any]) -> str:
    if supertrend_status.get("good_enough_for_strategy_review") is True:
        return (
            "Supertrend is good enough for strategy proof review, but not for "
            "22/6 operation approval."
        )
    return (
        "Supertrend is not good enough yet; missing proof must be closed before "
        "strategy review or 22/6 planning advances."
    )


def _blockers(readiness_status: str, missing_proof: Sequence[str]) -> tuple[str, ...]:
    blockers = list(missing_proof)
    blockers.extend(
        (
            "22/6 operation is not approved",
            "real money remains locked",
            "compounding remains locked",
            "broker action remains locked",
            "bank movement remains locked",
        )
    )
    if readiness_status != TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY:
        blockers.append(readiness_status)
    return tuple(dict.fromkeys(blockers))


def _strategy_proof_summary(
    strategy_result: StrategyProofEngineResult,
) -> dict[str, Any]:
    strategy_json = strategy_result_to_jsonable_dict(strategy_result)
    return {
        "result_status": strategy_result.result_status,
        "top_strategy": strategy_json["top_strategy"],
        "supertrend_status": strategy_json["supertrend_status"],
        "top_expectancy": strategy_json["top_expectancy"],
        "top_profit_factor": strategy_json["top_profit_factor"],
    }


def _operator_answer(
    readiness_status: str,
    strongest: StrategyProofCandidate | None,
) -> str:
    if readiness_status == TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY and strongest:
        return (
            f"{strongest.strategy_name} is ready for operator strategy proof "
            "review only. AIOS is not approved for 22/6 trading operation, real "
            "money, compounding, broker action, or bank movement."
        )
    return (
        "Trusted profit 22/6 readiness is blocked by missing or weak proof. "
        "No execution permission is created."
    )


def _permissions() -> dict[str, bool]:
    return {
        "real_money_allowed": False,
        "compounding_allowed": False,
        "broker_action_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
    }


def _strategy_candidate_to_jsonable(
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
