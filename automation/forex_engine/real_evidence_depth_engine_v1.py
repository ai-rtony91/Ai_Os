"""Local-only AIOS Forex Real Evidence Depth Engine V1.

This module deepens the evidence review for the current top Strategy Proof
Engine candidate. It does not call brokers, read credentials, read .env files,
use network access, place orders, approve real money, approve compounding, or
move money.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping

from automation.forex_engine.expectancy_strength_router_v1 import (
    EXPECTANCY_STRONG,
    ExpectancyStrengthResult,
    route_expectancy_strength,
    result_to_jsonable_dict as expectancy_result_to_jsonable_dict,
)
from automation.forex_engine.strategy_proof_engine_v1 import (
    StrategyProofCandidate,
    StrategyProofEngineResult,
    build_sample_all_blocked_strategy_evidence,
    build_sample_mixed_strategy_evidence,
    evaluate_strategy_proof_engine,
    result_to_jsonable_dict as strategy_result_to_jsonable_dict,
)
from automation.forex_engine.trusted_profit_22_6_readiness_v1 import (
    TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY,
    TrustedProfit226ReadinessResult,
    evaluate_trusted_profit_22_6_readiness,
    result_to_jsonable_dict as readiness_result_to_jsonable_dict,
)


REAL_EVIDENCE_DEPTH_ENGINE_VERSION = "real_evidence_depth_engine_v1"

REAL_EVIDENCE_DEPTH_IMPROVING = "REAL_EVIDENCE_DEPTH_IMPROVING"
REAL_EVIDENCE_DEPTH_MORE_PROOF_REQUIRED = "REAL_EVIDENCE_DEPTH_MORE_PROOF_REQUIRED"
REAL_EVIDENCE_DEPTH_BLOCKED = "REAL_EVIDENCE_DEPTH_BLOCKED"
REAL_EVIDENCE_DEPTH_UNKNOWN = "REAL_EVIDENCE_DEPTH_UNKNOWN"

VALID_REAL_EVIDENCE_DEPTH_STATUSES = {
    REAL_EVIDENCE_DEPTH_IMPROVING,
    REAL_EVIDENCE_DEPTH_MORE_PROOF_REQUIRED,
    REAL_EVIDENCE_DEPTH_BLOCKED,
    REAL_EVIDENCE_DEPTH_UNKNOWN,
}


@dataclass(frozen=True)
class EvidenceDepthCheck:
    check_id: str
    status: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RealEvidenceDepthResult:
    engine_version: str
    depth_status: str
    top_strategy: StrategyProofCandidate | None
    top_strategy_id: str
    supertrend_status: Mapping[str, Any]
    expectancy_result: ExpectancyStrengthResult
    expectancy_status: str
    profit_factor_strength: str
    drawdown_strength: str
    sample_depth_strength: str
    win_loss_balance: str
    consecutive_loss_risk: str
    proof_confidence: str
    trusted_22_6_readiness_status: str
    trusted_22_6_improvement: str
    checks: tuple[EvidenceDepthCheck, ...]
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    blockers: tuple[str, ...]
    proof_missing: tuple[str, ...]
    next_safe_action: str
    money_focused_next_step: str
    demo_trade_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    permissions: Mapping[str, bool]
    strategy_proof_summary: Mapping[str, Any]
    readiness_summary: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.depth_status not in VALID_REAL_EVIDENCE_DEPTH_STATUSES:
            raise ValueError(f"invalid depth status: {self.depth_status}")


def build_sample_mixed_real_evidence_inputs() -> tuple[
    StrategyProofEngineResult, TrustedProfit226ReadinessResult
]:
    strategy = evaluate_strategy_proof_engine(build_sample_mixed_strategy_evidence())
    readiness = evaluate_trusted_profit_22_6_readiness(strategy)
    return strategy, readiness


def build_sample_all_blocked_real_evidence_inputs() -> tuple[
    StrategyProofEngineResult, TrustedProfit226ReadinessResult
]:
    strategy = evaluate_strategy_proof_engine(build_sample_all_blocked_strategy_evidence())
    readiness = evaluate_trusted_profit_22_6_readiness(strategy)
    return strategy, readiness


def evaluate_real_evidence_depth(
    strategy_result: StrategyProofEngineResult | None = None,
    readiness_result: TrustedProfit226ReadinessResult | None = None,
) -> RealEvidenceDepthResult:
    active_strategy = strategy_result
    active_readiness = readiness_result
    if active_strategy is None:
        active_strategy, active_readiness = build_sample_mixed_real_evidence_inputs()
    if active_readiness is None:
        active_readiness = evaluate_trusted_profit_22_6_readiness(active_strategy)

    top = active_strategy.top_strategy
    expectancy = route_expectancy_strength(top)
    checks = _build_checks(top, active_strategy, active_readiness, expectancy)
    failed = tuple(check.check_id for check in checks if not check.passed)
    passed = tuple(check.check_id for check in checks if check.passed)
    depth_status = _depth_status(top, failed, active_readiness, expectancy)
    proof_missing = tuple(active_readiness.missing_proof)

    return RealEvidenceDepthResult(
        engine_version=REAL_EVIDENCE_DEPTH_ENGINE_VERSION,
        depth_status=depth_status,
        top_strategy=top,
        top_strategy_id=top.strategy_id if top else "NONE",
        supertrend_status=active_strategy.supertrend_status,
        expectancy_result=expectancy,
        expectancy_status=expectancy.expectancy_status,
        profit_factor_strength=_profit_factor_strength(top),
        drawdown_strength=_drawdown_strength(top),
        sample_depth_strength=_sample_depth_strength(top),
        win_loss_balance=_win_loss_balance(top),
        consecutive_loss_risk=_consecutive_loss_risk(top),
        proof_confidence=_proof_confidence(top),
        trusted_22_6_readiness_status=active_readiness.readiness_status,
        trusted_22_6_improvement=_readiness_improvement(active_readiness),
        checks=checks,
        passed_checks=passed,
        failed_checks=failed,
        blockers=_blockers(failed, proof_missing),
        proof_missing=proof_missing,
        next_safe_action=_next_safe_action(depth_status, top),
        money_focused_next_step=_money_focused_next_step(depth_status, top),
        demo_trade_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        permissions=_permissions(),
        strategy_proof_summary=_strategy_summary(active_strategy),
        readiness_summary=_readiness_summary(active_readiness),
    )


def result_to_operator_text(result: RealEvidenceDepthResult | None = None) -> str:
    active = result if result is not None else evaluate_real_evidence_depth()
    lines = [
        "AIOS Forex Real Evidence Depth Engine V1",
        f"depth_status: {active.depth_status}",
        f"top_strategy: {active.top_strategy_id}",
        f"supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"expectancy_status: {active.expectancy_status}",
        f"profit_factor_strength: {active.profit_factor_strength}",
        f"drawdown_strength: {active.drawdown_strength}",
        f"sample_depth_strength: {active.sample_depth_strength}",
        f"win_loss_balance: {active.win_loss_balance}",
        f"consecutive_loss_risk: {active.consecutive_loss_risk}",
        f"proof_confidence: {active.proof_confidence}",
        f"trusted_22_6_improvement: {active.trusted_22_6_improvement}",
        f"demo_trade_allowed: {_bool_text(active.demo_trade_allowed)}",
        f"broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
        f"real_money_allowed: {_bool_text(active.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(active.compounding_allowed)}",
        f"bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
        "failed_checks:",
    ]
    lines.extend(f"- {item}" for item in active.failed_checks or ("none",))
    lines.append(f"money_focused_next_step: {active.money_focused_next_step}")
    lines.append(f"next_safe_action: {active.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(result: RealEvidenceDepthResult | None = None) -> dict[str, Any]:
    active = result if result is not None else evaluate_real_evidence_depth()
    return {
        "engine_version": active.engine_version,
        "depth_status": active.depth_status,
        "top_strategy": _candidate_to_jsonable(active.top_strategy),
        "top_strategy_id": active.top_strategy_id,
        "supertrend_status": _json_value(active.supertrend_status),
        "expectancy_result": expectancy_result_to_jsonable_dict(active.expectancy_result),
        "expectancy_status": active.expectancy_status,
        "profit_factor_strength": active.profit_factor_strength,
        "drawdown_strength": active.drawdown_strength,
        "sample_depth_strength": active.sample_depth_strength,
        "win_loss_balance": active.win_loss_balance,
        "consecutive_loss_risk": active.consecutive_loss_risk,
        "proof_confidence": active.proof_confidence,
        "trusted_22_6_readiness_status": active.trusted_22_6_readiness_status,
        "trusted_22_6_improvement": active.trusted_22_6_improvement,
        "checks": [_json_value(check) for check in active.checks],
        "passed_checks": list(active.passed_checks),
        "failed_checks": list(active.failed_checks),
        "blockers": list(active.blockers),
        "proof_missing": list(active.proof_missing),
        "next_safe_action": active.next_safe_action,
        "money_focused_next_step": active.money_focused_next_step,
        "demo_trade_allowed": active.demo_trade_allowed,
        "broker_action_allowed": active.broker_action_allowed,
        "real_money_allowed": active.real_money_allowed,
        "compounding_allowed": active.compounding_allowed,
        "bank_movement_allowed": active.bank_movement_allowed,
        "permissions": dict(active.permissions),
        "strategy_proof_summary": _json_value(active.strategy_proof_summary),
        "readiness_summary": _json_value(active.readiness_summary),
        "safety": {
            "local_only": True,
            "broker_calls": False,
            "network_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "order_placement": False,
            "real_money_approval": False,
            "compounding_approval": False,
            "bank_movement_approval": False,
        },
    }


def real_evidence_depth_to_markdown(result: RealEvidenceDepthResult | None = None) -> str:
    active = result if result is not None else evaluate_real_evidence_depth()
    lines = [
        "# AIOS Forex Real Evidence Depth Engine V1",
        "",
        "## Status",
        f"- depth_status: {active.depth_status}",
        f"- top_strategy: {active.top_strategy_id}",
        f"- supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"- expectancy_status: {active.expectancy_status}",
        f"- trusted_22_6_improvement: {active.trusted_22_6_improvement}",
        "",
        "## Passed",
    ]
    lines.extend(f"- {item}" for item in active.passed_checks or ("none",))
    lines.extend(["", "## Failed"])
    lines.extend(f"- {item}" for item in active.failed_checks or ("none",))
    lines.extend(
        [
            "",
            "## Still Missing",
            *[f"- {item}" for item in active.proof_missing],
            "",
            "## Safety Locks",
            f"- demo_trade_allowed: {_bool_text(active.demo_trade_allowed)}",
            f"- broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
            f"- real_money_allowed: {_bool_text(active.real_money_allowed)}",
            f"- compounding_allowed: {_bool_text(active.compounding_allowed)}",
            f"- bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
            "",
            "## Next Copy/Paste Action",
            active.next_safe_action,
            "",
        ]
    )
    return "\n".join(lines)


def _build_checks(
    top: StrategyProofCandidate | None,
    strategy: StrategyProofEngineResult,
    readiness: TrustedProfit226ReadinessResult,
    expectancy: ExpectancyStrengthResult,
) -> tuple[EvidenceDepthCheck, ...]:
    if top is None:
        return (
            EvidenceDepthCheck("top_strategy_present", "FAIL", False, "No top strategy found."),
        )
    checks = (
        EvidenceDepthCheck(
            "top_strategy_present",
            "PASS",
            True,
            f"Top strategy is {top.strategy_id}.",
        ),
        EvidenceDepthCheck(
            "supertrend_strong_enough",
            "PASS" if _supertrend_strong(strategy) else "FAIL",
            _supertrend_strong(strategy),
            str(strategy.supertrend_status.get("status", "UNKNOWN")),
        ),
        EvidenceDepthCheck(
            "expectancy_strong_enough",
            "PASS" if expectancy.expectancy_status == EXPECTANCY_STRONG else "FAIL",
            expectancy.expectancy_status == EXPECTANCY_STRONG,
            expectancy.expectancy_status,
        ),
        EvidenceDepthCheck(
            "profit_factor_strong_enough",
            "PASS" if _profit_factor_strength(top) in {"PROFIT_FACTOR_STRONG", "PROFIT_FACTOR_PROMISING"} else "FAIL",
            _profit_factor_strength(top) in {"PROFIT_FACTOR_STRONG", "PROFIT_FACTOR_PROMISING"},
            _profit_factor_strength(top),
        ),
        EvidenceDepthCheck(
            "drawdown_acceptable",
            "PASS" if _drawdown_strength(top) in {"DRAWDOWN_STRONG", "DRAWDOWN_ACCEPTABLE"} else "FAIL",
            _drawdown_strength(top) in {"DRAWDOWN_STRONG", "DRAWDOWN_ACCEPTABLE"},
            _drawdown_strength(top),
        ),
        EvidenceDepthCheck(
            "sample_depth_enough",
            "PASS" if _sample_depth_strength(top) in {"SAMPLE_DEPTH_STRONG", "SAMPLE_DEPTH_ENOUGH"} else "FAIL",
            _sample_depth_strength(top) in {"SAMPLE_DEPTH_STRONG", "SAMPLE_DEPTH_ENOUGH"},
            _sample_depth_strength(top),
        ),
        EvidenceDepthCheck(
            "win_loss_balance_positive",
            "PASS" if _win_loss_balance(top) == "WIN_LOSS_BALANCE_POSITIVE" else "FAIL",
            _win_loss_balance(top) == "WIN_LOSS_BALANCE_POSITIVE",
            _win_loss_balance(top),
        ),
        EvidenceDepthCheck(
            "consecutive_loss_risk_acceptable",
            "PASS" if _consecutive_loss_risk(top) in {"CONSECUTIVE_LOSS_RISK_LOW", "CONSECUTIVE_LOSS_RISK_ACCEPTABLE"} else "FAIL",
            _consecutive_loss_risk(top) in {"CONSECUTIVE_LOSS_RISK_LOW", "CONSECUTIVE_LOSS_RISK_ACCEPTABLE"},
            _consecutive_loss_risk(top),
        ),
        EvidenceDepthCheck(
            "proof_confidence_enough",
            "PASS" if _proof_confidence(top) in {"PROOF_CONFIDENCE_STRONG", "PROOF_CONFIDENCE_ENOUGH"} else "FAIL",
            _proof_confidence(top) in {"PROOF_CONFIDENCE_STRONG", "PROOF_CONFIDENCE_ENOUGH"},
            _proof_confidence(top),
        ),
        EvidenceDepthCheck(
            "trusted_22_6_readiness_improving",
            "PASS" if _readiness_improvement(readiness) == "TRUSTED_22_6_IMPROVING_PROOF_REVIEW_READY" else "FAIL",
            _readiness_improvement(readiness) == "TRUSTED_22_6_IMPROVING_PROOF_REVIEW_READY",
            _readiness_improvement(readiness),
        ),
    )
    return checks


def _depth_status(
    top: StrategyProofCandidate | None,
    failed: tuple[str, ...],
    readiness: TrustedProfit226ReadinessResult,
    expectancy: ExpectancyStrengthResult,
) -> str:
    if top is None:
        return REAL_EVIDENCE_DEPTH_UNKNOWN
    hard_failures = {"expectancy_strong_enough"}
    if expectancy.expectancy_status == EXPECTANCY_STRONG and not hard_failures.intersection(failed):
        if readiness.readiness_status == TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY:
            return REAL_EVIDENCE_DEPTH_IMPROVING
    if failed:
        return REAL_EVIDENCE_DEPTH_MORE_PROOF_REQUIRED
    return REAL_EVIDENCE_DEPTH_BLOCKED


def _supertrend_strong(strategy: StrategyProofEngineResult) -> bool:
    return (
        strategy.supertrend_status.get("strategy_id") == "supertrend"
        and strategy.supertrend_status.get("good_enough_for_strategy_review") is True
        and strategy.supertrend_status.get("rank") == 1
    )


def _profit_factor_strength(top: StrategyProofCandidate | None) -> str:
    if top is None:
        return "PROFIT_FACTOR_UNKNOWN"
    if top.profit_factor >= Decimal("1.70"):
        return "PROFIT_FACTOR_STRONG"
    if top.profit_factor >= Decimal("1.25"):
        return "PROFIT_FACTOR_PROMISING"
    if top.profit_factor >= Decimal("1.00"):
        return "PROFIT_FACTOR_WEAK"
    return "PROFIT_FACTOR_BLOCKED"


def _drawdown_strength(top: StrategyProofCandidate | None) -> str:
    if top is None:
        return "DRAWDOWN_UNKNOWN"
    if top.max_drawdown <= Decimal("0.025"):
        return "DRAWDOWN_STRONG"
    if top.max_drawdown <= Decimal("0.050"):
        return "DRAWDOWN_ACCEPTABLE"
    return "DRAWDOWN_BLOCKED"


def _sample_depth_strength(top: StrategyProofCandidate | None) -> str:
    if top is None:
        return "SAMPLE_DEPTH_UNKNOWN"
    if top.total_trades >= 60:
        return "SAMPLE_DEPTH_STRONG"
    if top.total_trades >= 30:
        return "SAMPLE_DEPTH_ENOUGH"
    return "SAMPLE_DEPTH_INSUFFICIENT"


def _win_loss_balance(top: StrategyProofCandidate | None) -> str:
    if top is None:
        return "WIN_LOSS_BALANCE_UNKNOWN"
    if top.wins > top.losses:
        return "WIN_LOSS_BALANCE_POSITIVE"
    return "WIN_LOSS_BALANCE_BLOCKED"


def _consecutive_loss_risk(top: StrategyProofCandidate | None) -> str:
    if top is None:
        return "CONSECUTIVE_LOSS_RISK_UNKNOWN"
    if top.consecutive_losses <= 2:
        return "CONSECUTIVE_LOSS_RISK_LOW"
    if top.consecutive_losses <= 3:
        return "CONSECUTIVE_LOSS_RISK_ACCEPTABLE"
    return "CONSECUTIVE_LOSS_RISK_HIGH"


def _proof_confidence(top: StrategyProofCandidate | None) -> str:
    if top is None:
        return "PROOF_CONFIDENCE_UNKNOWN"
    if top.proof_score >= Decimal("95") and top.confidence_score >= Decimal("70"):
        return "PROOF_CONFIDENCE_STRONG"
    if top.proof_score >= Decimal("80"):
        return "PROOF_CONFIDENCE_ENOUGH"
    return "PROOF_CONFIDENCE_WEAK"


def _readiness_improvement(readiness: TrustedProfit226ReadinessResult) -> str:
    if (
        readiness.readiness_status == TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY
        and readiness.strategy_worth_proof_review
        and not readiness.enough_proof_for_22_6
    ):
        return "TRUSTED_22_6_IMPROVING_PROOF_REVIEW_READY"
    return "TRUSTED_22_6_NOT_IMPROVING"


def _blockers(failed: tuple[str, ...], proof_missing: tuple[str, ...]) -> tuple[str, ...]:
    blockers = list(failed)
    blockers.extend(proof_missing)
    blockers.extend(
        (
            "demo trade remains locked",
            "broker action remains locked",
            "real money remains locked",
            "compounding remains locked",
            "bank movement remains locked",
        )
    )
    return tuple(dict.fromkeys(blockers))


def _next_safe_action(status: str, top: StrategyProofCandidate | None) -> str:
    if status == REAL_EVIDENCE_DEPTH_IMPROVING and top is not None:
        return (
            f"Create the next proof-review packet for {top.strategy_id}; collect "
            "real observation evidence and keep all money permissions locked."
        )
    if top is not None:
        return f"Repair failed evidence checks for {top.strategy_id} before money-path review."
    return "Provide valid strategy proof output before evidence-depth review."


def _money_focused_next_step(status: str, top: StrategyProofCandidate | None) -> str:
    if status == REAL_EVIDENCE_DEPTH_IMPROVING and top is not None:
        return (
            f"Use {top.strategy_id} as the proof-review candidate and gather "
            "non-broker, non-money observation depth."
        )
    return "Do not advance money path until failed evidence checks are repaired."


def _permissions() -> dict[str, bool]:
    return {
        "demo_trade_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def _strategy_summary(strategy: StrategyProofEngineResult) -> dict[str, Any]:
    raw = strategy_result_to_jsonable_dict(strategy)
    return {
        "result_status": raw["result_status"],
        "top_strategy": raw["top_strategy"],
        "supertrend_status": raw["supertrend_status"],
        "top_expectancy": raw["top_expectancy"],
        "top_profit_factor": raw["top_profit_factor"],
    }


def _readiness_summary(readiness: TrustedProfit226ReadinessResult) -> dict[str, Any]:
    raw = readiness_result_to_jsonable_dict(readiness)
    return {
        "readiness_status": raw["readiness_status"],
        "strategy_worth_proof_review": raw["strategy_worth_proof_review"],
        "enough_proof_for_22_6": raw["enough_proof_for_22_6"],
        "missing_proof": raw["missing_proof"],
    }


def _candidate_to_jsonable(candidate: StrategyProofCandidate | None) -> dict[str, Any] | None:
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
