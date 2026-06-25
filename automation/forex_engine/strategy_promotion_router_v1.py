"""Local-only AIOS Forex Strategy Promotion Router V1.

This module routes the strongest current strategy proof into an operator demo
review recommendation. It does not call brokers, read credentials, read .env
files, use network access, place orders, approve demo execution, approve real
money, approve compounding, or move money.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Mapping

from automation.forex_engine.expectancy_strength_router_v1 import EXPECTANCY_STRONG
from automation.forex_engine.real_evidence_depth_engine_v1 import (
    REAL_EVIDENCE_DEPTH_IMPROVING,
    RealEvidenceDepthResult,
    build_sample_all_blocked_real_evidence_inputs,
    build_sample_mixed_real_evidence_inputs,
    evaluate_real_evidence_depth,
    result_to_jsonable_dict as depth_result_to_jsonable_dict,
)


STRATEGY_PROMOTION_ROUTER_VERSION = "strategy_promotion_router_v1"

STRATEGY_PROMOTION_REVIEW_READY = "STRATEGY_PROMOTION_REVIEW_READY"
STRATEGY_PROMOTION_MORE_PROOF_REQUIRED = "STRATEGY_PROMOTION_MORE_PROOF_REQUIRED"
STRATEGY_PROMOTION_BLOCKED = "STRATEGY_PROMOTION_BLOCKED"
STRATEGY_PROMOTION_UNKNOWN = "STRATEGY_PROMOTION_UNKNOWN"

VALID_PROMOTION_STATUSES = {
    STRATEGY_PROMOTION_REVIEW_READY,
    STRATEGY_PROMOTION_MORE_PROOF_REQUIRED,
    STRATEGY_PROMOTION_BLOCKED,
    STRATEGY_PROMOTION_UNKNOWN,
}


@dataclass(frozen=True)
class PromotionRouteCheck:
    check_id: str
    status: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class StrategyPromotionRouteResult:
    router_version: str
    promotion_status: str
    best_strategy: str
    best_strategy_name: str
    why: str
    supertrend_status: Mapping[str, Any]
    promotion_score: Decimal
    review_recommendation: str
    expectancy_status: str
    proof_status: str
    proof_improving: bool
    expectancy_improving: bool
    checks: tuple[PromotionRouteCheck, ...]
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    what_must_improve_next: tuple[str, ...]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    permissions: Mapping[str, bool]
    evidence_depth_summary: Mapping[str, Any]

    def __post_init__(self) -> None:
        if self.promotion_status not in VALID_PROMOTION_STATUSES:
            raise ValueError(f"invalid promotion status: {self.promotion_status}")


def build_sample_mixed_promotion_input() -> RealEvidenceDepthResult:
    strategy, readiness = build_sample_mixed_real_evidence_inputs()
    return evaluate_real_evidence_depth(strategy, readiness)


def build_sample_all_blocked_promotion_input() -> RealEvidenceDepthResult:
    strategy, readiness = build_sample_all_blocked_real_evidence_inputs()
    return evaluate_real_evidence_depth(strategy, readiness)


def route_strategy_promotion(
    evidence_depth: RealEvidenceDepthResult | None = None,
) -> StrategyPromotionRouteResult:
    active = evidence_depth if evidence_depth is not None else build_sample_mixed_promotion_input()
    checks = _build_checks(active)
    failed = tuple(check.check_id for check in checks if not check.passed)
    passed = tuple(check.check_id for check in checks if check.passed)
    status = _promotion_status(active, failed)
    score = _promotion_score(checks)
    best_strategy = active.top_strategy_id
    best_name = active.top_strategy.strategy_name if active.top_strategy else "NONE"

    return StrategyPromotionRouteResult(
        router_version=STRATEGY_PROMOTION_ROUTER_VERSION,
        promotion_status=status,
        best_strategy=best_strategy,
        best_strategy_name=best_name,
        why=_why(status, active),
        supertrend_status=active.supertrend_status,
        promotion_score=score,
        review_recommendation=_review_recommendation(status, active),
        expectancy_status=active.expectancy_status,
        proof_status=_proof_status(active),
        proof_improving=active.depth_status == REAL_EVIDENCE_DEPTH_IMPROVING,
        expectancy_improving=active.expectancy_status == EXPECTANCY_STRONG,
        checks=checks,
        passed_checks=passed,
        failed_checks=failed,
        blockers=_blockers(active, failed),
        next_safe_action=_next_safe_action(status, best_strategy),
        what_must_improve_next=_what_must_improve_next(active, failed),
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
        permissions=_permissions(),
        evidence_depth_summary=_evidence_depth_summary(active),
    )


def result_to_operator_text(result: StrategyPromotionRouteResult | None = None) -> str:
    active = result if result is not None else route_strategy_promotion()
    lines = [
        "AIOS Forex Strategy Promotion Router V1",
        f"promotion_status: {active.promotion_status}",
        f"best_strategy: {active.best_strategy}",
        f"supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"promotion_score: {_json_value(active.promotion_score)}",
        f"review_recommendation: {active.review_recommendation}",
        f"expectancy_status: {active.expectancy_status}",
        f"proof_status: {active.proof_status}",
        f"demo_execution_allowed: {_bool_text(active.demo_execution_allowed)}",
        f"broker_action_allowed: {_bool_text(active.broker_action_allowed)}",
        f"real_money_allowed: {_bool_text(active.real_money_allowed)}",
        f"compounding_allowed: {_bool_text(active.compounding_allowed)}",
        f"bank_movement_allowed: {_bool_text(active.bank_movement_allowed)}",
        "blockers:",
    ]
    lines.extend(f"- {item}" for item in active.blockers or ("none",))
    lines.append(f"next_safe_action: {active.next_safe_action}")
    return "\n".join(lines) + "\n"


def result_to_jsonable_dict(
    result: StrategyPromotionRouteResult | None = None,
) -> dict[str, Any]:
    active = result if result is not None else route_strategy_promotion()
    return {
        "router_version": active.router_version,
        "promotion_status": active.promotion_status,
        "best_strategy": active.best_strategy,
        "best_strategy_name": active.best_strategy_name,
        "why": active.why,
        "supertrend_status": _json_value(active.supertrend_status),
        "promotion_score": _json_value(active.promotion_score),
        "review_recommendation": active.review_recommendation,
        "expectancy_status": active.expectancy_status,
        "proof_status": active.proof_status,
        "proof_improving": active.proof_improving,
        "expectancy_improving": active.expectancy_improving,
        "checks": [_json_value(check) for check in active.checks],
        "passed_checks": list(active.passed_checks),
        "failed_checks": list(active.failed_checks),
        "blockers": list(active.blockers),
        "next_safe_action": active.next_safe_action,
        "what_must_improve_next": list(active.what_must_improve_next),
        "demo_execution_allowed": active.demo_execution_allowed,
        "broker_action_allowed": active.broker_action_allowed,
        "real_money_allowed": active.real_money_allowed,
        "compounding_allowed": active.compounding_allowed,
        "bank_movement_allowed": active.bank_movement_allowed,
        "permissions": dict(active.permissions),
        "evidence_depth_summary": _json_value(active.evidence_depth_summary),
        "safety": {
            "local_only": True,
            "broker_calls": False,
            "network_calls": False,
            "credential_reads": False,
            "env_file_reads": False,
            "order_placement": False,
            "demo_execution_approval": False,
            "real_money_approval": False,
            "compounding_approval": False,
            "bank_movement_approval": False,
        },
    }


def promotion_route_to_markdown(result: StrategyPromotionRouteResult | None = None) -> str:
    active = result if result is not None else route_strategy_promotion()
    lines = [
        "# AIOS Forex Strategy Promotion Router V1",
        "",
        "## Status",
        f"- promotion_status: {active.promotion_status}",
        f"- best_strategy: {active.best_strategy}",
        f"- supertrend_status: {active.supertrend_status.get('status', 'UNKNOWN')}",
        f"- promotion_score: {_json_value(active.promotion_score)}",
        f"- expectancy_status: {active.expectancy_status}",
        f"- proof_status: {active.proof_status}",
        "",
        "## Passed",
    ]
    lines.extend(f"- {item}" for item in active.passed_checks or ("none",))
    lines.extend(["", "## Failed"])
    lines.extend(f"- {item}" for item in active.failed_checks or ("none",))
    lines.extend(["", "## What Must Improve Next"])
    lines.extend(f"- {item}" for item in active.what_must_improve_next or ("none",))
    lines.extend(
        [
            "",
            "## Safety Locks",
            f"- demo_execution_allowed: {_bool_text(active.demo_execution_allowed)}",
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


def _build_checks(active: RealEvidenceDepthResult) -> tuple[PromotionRouteCheck, ...]:
    return (
        PromotionRouteCheck(
            "best_strategy_present",
            "PASS" if active.top_strategy is not None else "FAIL",
            active.top_strategy is not None,
            active.top_strategy_id,
        ),
        PromotionRouteCheck(
            "supertrend_review_ready",
            "PASS"
            if active.supertrend_status.get("good_enough_for_strategy_review") is True
            else "FAIL",
            active.supertrend_status.get("good_enough_for_strategy_review") is True,
            str(active.supertrend_status.get("status", "UNKNOWN")),
        ),
        PromotionRouteCheck(
            "expectancy_strong",
            "PASS" if active.expectancy_status == EXPECTANCY_STRONG else "FAIL",
            active.expectancy_status == EXPECTANCY_STRONG,
            active.expectancy_status,
        ),
        PromotionRouteCheck(
            "proof_improving",
            "PASS" if active.depth_status == REAL_EVIDENCE_DEPTH_IMPROVING else "FAIL",
            active.depth_status == REAL_EVIDENCE_DEPTH_IMPROVING,
            active.depth_status,
        ),
        PromotionRouteCheck(
            "profit_factor_ready",
            "PASS"
            if active.profit_factor_strength
            in {"PROFIT_FACTOR_STRONG", "PROFIT_FACTOR_PROMISING"}
            else "FAIL",
            active.profit_factor_strength
            in {"PROFIT_FACTOR_STRONG", "PROFIT_FACTOR_PROMISING"},
            active.profit_factor_strength,
        ),
        PromotionRouteCheck(
            "drawdown_ready",
            "PASS"
            if active.drawdown_strength in {"DRAWDOWN_STRONG", "DRAWDOWN_ACCEPTABLE"}
            else "FAIL",
            active.drawdown_strength in {"DRAWDOWN_STRONG", "DRAWDOWN_ACCEPTABLE"},
            active.drawdown_strength,
        ),
        PromotionRouteCheck(
            "sample_depth_ready",
            "PASS"
            if active.sample_depth_strength in {"SAMPLE_DEPTH_STRONG", "SAMPLE_DEPTH_ENOUGH"}
            else "FAIL",
            active.sample_depth_strength in {"SAMPLE_DEPTH_STRONG", "SAMPLE_DEPTH_ENOUGH"},
            active.sample_depth_strength,
        ),
        PromotionRouteCheck(
            "demo_execution_locked",
            "PASS" if active.demo_trade_allowed is False else "FAIL",
            active.demo_trade_allowed is False,
            "demo execution remains locked",
        ),
        PromotionRouteCheck(
            "money_permissions_locked",
            "PASS" if _money_permissions_locked(active) else "FAIL",
            _money_permissions_locked(active),
            "broker, real money, compounding, and bank movement remain locked",
        ),
    )


def _promotion_status(active: RealEvidenceDepthResult, failed: tuple[str, ...]) -> str:
    if active.top_strategy is None:
        return STRATEGY_PROMOTION_UNKNOWN
    hard_failures = {
        "best_strategy_present",
        "expectancy_strong",
        "profit_factor_ready",
        "drawdown_ready",
        "sample_depth_ready",
        "money_permissions_locked",
    }
    if hard_failures.intersection(failed):
        return STRATEGY_PROMOTION_BLOCKED
    if failed:
        return STRATEGY_PROMOTION_MORE_PROOF_REQUIRED
    return STRATEGY_PROMOTION_REVIEW_READY


def _promotion_score(checks: tuple[PromotionRouteCheck, ...]) -> Decimal:
    if not checks:
        return Decimal("0.00")
    passed = Decimal(sum(1 for check in checks if check.passed))
    total = Decimal(len(checks))
    return (passed / total * Decimal("100")).quantize(Decimal("0.01"))


def _why(status: str, active: RealEvidenceDepthResult) -> str:
    if status == STRATEGY_PROMOTION_REVIEW_READY and active.top_strategy is not None:
        return (
            f"{active.top_strategy.strategy_id} has the strongest local evidence: "
            f"{active.expectancy_status}, {active.profit_factor_strength}, "
            f"{active.drawdown_strength}, and {active.sample_depth_strength}."
        )
    if active.top_strategy is not None:
        return (
            f"{active.top_strategy.strategy_id} is still the best observed candidate, "
            "but one or more promotion checks require more proof."
        )
    return "No strategy is available for demo review."


def _review_recommendation(status: str, active: RealEvidenceDepthResult) -> str:
    if status == STRATEGY_PROMOTION_REVIEW_READY:
        return "REVIEW_STRATEGY_FOR_DEMO_PACKAGE_ONLY"
    if active.top_strategy is None:
        return "DO_NOT_REVIEW_NO_STRATEGY"
    return "COLLECT_MORE_PROOF_BEFORE_DEMO_REVIEW"


def _proof_status(active: RealEvidenceDepthResult) -> str:
    if active.depth_status == REAL_EVIDENCE_DEPTH_IMPROVING:
        return "PROOF_IMPROVING"
    if active.failed_checks:
        return "PROOF_BLOCKED"
    return "PROOF_UNKNOWN"


def _blockers(active: RealEvidenceDepthResult, failed: tuple[str, ...]) -> tuple[str, ...]:
    blockers = list(failed)
    blockers.extend(active.proof_missing)
    blockers.extend(
        (
            "demo execution remains locked",
            "broker action remains locked",
            "real money remains locked",
            "compounding remains locked",
            "bank movement remains locked",
        )
    )
    return tuple(dict.fromkeys(blockers))


def _next_safe_action(status: str, best_strategy: str) -> str:
    if status == STRATEGY_PROMOTION_REVIEW_READY:
        return (
            f"Create a human demo-review packet for {best_strategy}; keep demo "
            "execution, broker action, real money, compounding, and bank movement locked."
        )
    if best_strategy != "NONE":
        return f"Collect missing proof for {best_strategy} before demo-review promotion."
    return "Repair strategy proof evidence before demo-review routing."


def _what_must_improve_next(
    active: RealEvidenceDepthResult,
    failed: tuple[str, ...],
) -> tuple[str, ...]:
    improvements = list(failed)
    improvements.extend(active.proof_missing)
    improvements.append("human demo-review package still required before any execution")
    return tuple(dict.fromkeys(improvements))


def _money_permissions_locked(active: RealEvidenceDepthResult) -> bool:
    return (
        active.broker_action_allowed is False
        and active.real_money_allowed is False
        and active.compounding_allowed is False
        and active.bank_movement_allowed is False
    )


def _permissions() -> dict[str, bool]:
    return {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
    }


def _evidence_depth_summary(active: RealEvidenceDepthResult) -> dict[str, Any]:
    raw = depth_result_to_jsonable_dict(active)
    return {
        "depth_status": raw["depth_status"],
        "top_strategy_id": raw["top_strategy_id"],
        "expectancy_status": raw["expectancy_status"],
        "profit_factor_strength": raw["profit_factor_strength"],
        "drawdown_strength": raw["drawdown_strength"],
        "sample_depth_strength": raw["sample_depth_strength"],
        "trusted_22_6_improvement": raw["trusted_22_6_improvement"],
        "proof_missing": raw["proof_missing"],
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
