from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple


CAMPAIGN_EVIDENCE_READY = "CAMPAIGN_EVIDENCE_READY"
CAMPAIGN_MORE_EVIDENCE_REQUIRED = "CAMPAIGN_MORE_EVIDENCE_REQUIRED"
CAMPAIGN_EVIDENCE_BLOCKED = "CAMPAIGN_EVIDENCE_BLOCKED"
CAMPAIGN_EVIDENCE_REJECTED = "CAMPAIGN_EVIDENCE_REJECTED"


@dataclass(frozen=True)
class _Limits:
    minimum_trade_count: int = 20
    minimum_session_count: int = 3
    minimum_positive_expectancy: float = 0.01
    minimum_profit_factor: float = 1.10
    maximum_drawdown: float = 10.0
    minimum_evidence_score: float = 0.75


_PASS_VALUES = {
    "pass",
    "passed",
    "success",
    "succeeded",
    "accepted",
    "ready",
    "completed",
    "complete",
    "true",
    "on",
    "ok",
}

_BLOCK_VALUES = {
    "blocked",
    "hold",
    "waiting",
    "pending",
    "evidence_required",
    "more_evidence_required",
}

_REJECT_VALUES = {
    "reject",
    "rejected",
    "failed",
    "fail",
    "failure",
    "error",
}


def _as_sequence(value: Any) -> Sequence[Mapping[str, Any]]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(item for item in value if isinstance(item, Mapping))
    return ()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_status(value: Mapping[str, Any]) -> str:
    for key in (
        "status",
        "result_status",
        "state",
        "outcome",
        "decision",
        "campaign_status",
        "campaign_evidence_status",
        "paper_session_status",
        "profitability_status",
        "walk_forward_status",
        "promotion_status",
        "capital_allocation_status",
    ):
        if key in value:
            return str(value[key]).strip().lower()
    return ""


def _collect_numeric(value: Mapping[str, Any], keys: Iterable[str], default: float = 0.0) -> float:
    for key in keys:
        if key in value:
            return _to_float(value[key], default=default)
    return default


def _classify_status(value: Mapping[str, Any]) -> str:
    status = _extract_status(value)
    if status in _BLOCK_VALUES:
        return CAMPAIGN_EVIDENCE_BLOCKED
    if status in _REJECT_VALUES:
        return CAMPAIGN_EVIDENCE_REJECTED
    if status in _PASS_VALUES or status == "":
        return CAMPAIGN_EVIDENCE_READY
    return CAMPAIGN_EVIDENCE_READY


def _component_passed(value: Mapping[str, Any]) -> Tuple[bool, str]:
    status = _extract_status(value)
    if status in _REJECT_VALUES:
        return False, CAMPAIGN_EVIDENCE_REJECTED
    if status in _BLOCK_VALUES:
        return False, CAMPAIGN_EVIDENCE_BLOCKED
    return True, CAMPAIGN_EVIDENCE_READY


def _collect_component_flags(
    components: Sequence[Mapping[str, Any]],
) -> Tuple[bool, bool, list[str], bool]:
    """
    Returns:
        passed: bool, all components pass or missing component list
        any_blocked: bool
        blockers: list[str]
        component_result_present: bool
    """
    blockers: list[str] = []
    hard_reject = False
    blocked = False
    present = len(components) > 0

    for item in components:
        if not isinstance(item, Mapping):
            continue
        passed, state = _component_passed(item)
        if state == CAMPAIGN_EVIDENCE_REJECTED and not passed:
            hard_reject = True
            blockers.append("component_failure")
        elif state == CAMPAIGN_EVIDENCE_BLOCKED and not passed:
            blocked = True
            blockers.append("component_blocked")
        elif not passed:
            blocked = True
            blockers.append("component_not_passed")

    if hard_reject:
        return False, True, blockers, present
    if blocked:
        return False, True, blockers, present
    return True, False, blockers, present


def _aggregate_numeric(result_list: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    totals = {
        "trade_count": 0,
        "session_count": 0,
        "win_count": 0,
        "loss_count": 0,
        "realized_pl": 0.0,
        "expectancy_values": [],
        "profit_factor_values": [],
        "drawdown_values": [],
        "evidence_scores": [],
    }

    for item in result_list:
        totals["trade_count"] += _to_int(_collect_numeric(item, ("trade_count", "closed_trade_count", "closed_trades", "num_trades")))
        totals["session_count"] += _to_int(_collect_numeric(item, ("session_count", "sessions", "completed_sessions")))
        totals["win_count"] += _to_int(_collect_numeric(item, ("win_count", "wins", "winning_trades")))
        totals["loss_count"] += _to_int(_collect_numeric(item, ("loss_count", "losses", "losing_trades")))
        totals["realized_pl"] += _to_float(_collect_numeric(item, ("realized_pl", "realized_profit", "profit_loss", "pnl")))

        expectancy = _collect_numeric(item, ("expectancy", "expectancy_ratio"))
        if expectancy != 0.0 or "expectancy" in item or "expectancy_ratio" in item:
            totals["expectancy_values"].append(expectancy)

        pf = _collect_numeric(item, ("profit_factor", "pf"))
        if pf != 0.0 or "profit_factor" in item or "pf" in item:
            totals["profit_factor_values"].append(pf)

        dd = _collect_numeric(item, ("max_drawdown", "max_drawdown_pct", "drawdown"))
        if dd != 0.0 or "max_drawdown" in item or "max_drawdown_pct" in item or "drawdown" in item:
            totals["drawdown_values"].append(abs(dd))

        score = _collect_numeric(item, ("evidence_score", "score"))
        if score != 0.0 or "evidence_score" in item or "score" in item:
            totals["evidence_scores"].append(score)

    return totals


def _safe_ratio(numerator: float, denominator: float, fallback: float) -> float:
    if denominator <= 0:
        return fallback
    return numerator / denominator


def evaluate_campaign_evidence(
    paper_session_results: Sequence[Mapping[str, Any]] | None = None,
    profitability_results: Sequence[Mapping[str, Any]] | None = None,
    walk_forward_results: Sequence[Mapping[str, Any]] | None = None,
    promotion_results: Sequence[Mapping[str, Any]] | None = None,
    capital_allocation_results: Sequence[Mapping[str, Any]] | None = None,
    *,
    minimum_trade_count: int = _Limits.minimum_trade_count,
    minimum_session_count: int = _Limits.minimum_session_count,
    minimum_positive_expectancy: float = _Limits.minimum_positive_expectancy,
    minimum_profit_factor: float = _Limits.minimum_profit_factor,
    maximum_drawdown: float = _Limits.maximum_drawdown,
    minimum_evidence_score: float = _Limits.minimum_evidence_score,
) -> Dict[str, Any]:
    paper_session_results = _as_sequence(paper_session_results)
    profitability_results = _as_sequence(profitability_results)
    walk_forward_results = _as_sequence(walk_forward_results)
    promotion_results = _as_sequence(promotion_results)
    capital_allocation_results = _as_sequence(capital_allocation_results)

    empty_all = (
        len(paper_session_results)
        + len(profitability_results)
        + len(walk_forward_results)
        + len(promotion_results)
        + len(capital_allocation_results)
        == 0
    )

    all_results = (
        paper_session_results
        + profitability_results
        + walk_forward_results
        + promotion_results
        + capital_allocation_results
    )

    agg = _aggregate_numeric(all_results)
    trade_count = agg["trade_count"]
    session_count = agg["session_count"]
    win_count = agg["win_count"]
    loss_count = agg["loss_count"]
    realized_pl = agg["realized_pl"]

    expectancy_values = agg["expectancy_values"]
    profit_factor_values = agg["profit_factor_values"]
    drawdown_values = agg["drawdown_values"]
    evidence_scores = agg["evidence_scores"]

    expectancy = sum(expectancy_values) / len(expectancy_values) if expectancy_values else 0.0
    profit_factor = sum(profit_factor_values) / len(profit_factor_values) if profit_factor_values else 0.0
    max_drawdown = max(drawdown_values) if drawdown_values else 0.0
    evidence_score = sum(evidence_scores) / len(evidence_scores) if evidence_scores else 0.0

    profitability_pass, profitability_blocked, profitability_blockers, profitability_present = _collect_component_flags(
        profitability_results
    )
    walk_forward_pass, walk_forward_blocked, walk_forward_blockers, walk_forward_present = _collect_component_flags(
        walk_forward_results
    )
    promotion_pass, promotion_blocked, promotion_blockers, promotion_present = _collect_component_flags(
        promotion_results
    )
    capital_allocation_pass, capital_allocation_blocked, capital_allocation_blockers, capital_allocation_present = _collect_component_flags(
        capital_allocation_results
    )

    blockers: list[str] = []
    blockers.extend(profitability_blockers)
    blockers.extend(walk_forward_blockers)
    blockers.extend(promotion_blockers)
    blockers.extend(capital_allocation_blockers)

    campaign_status = CAMPAIGN_EVIDENCE_READY

    if empty_all:
        campaign_status = CAMPAIGN_MORE_EVIDENCE_REQUIRED
        blockers.extend(["no_evidence_results"])

    component_rejections = []
    if not profitability_pass:
        component_rejections.append("profitability_component_not_passed")
    if not walk_forward_pass:
        component_rejections.append("walk_forward_component_not_passed")
    if not promotion_pass:
        component_rejections.append("promotion_component_not_passed")
    if not capital_allocation_pass:
        component_rejections.append("capital_allocation_component_not_passed")

    hard_block = profitability_blocked or walk_forward_blocked or promotion_blocked or capital_allocation_blocked

    if profitability_present and not profitability_pass:
        blockers.append("profitability_failure")
    if walk_forward_present and not walk_forward_pass:
        blockers.append("walk_forward_failure")
    if promotion_present and not promotion_pass:
        blockers.append("promotion_failure")
    if capital_allocation_present and not capital_allocation_pass:
        blockers.append("capital_allocation_failure")

    if component_rejections:
        if hard_block:
            campaign_status = CAMPAIGN_EVIDENCE_BLOCKED
        else:
            campaign_status = CAMPAIGN_EVIDENCE_REJECTED

    if (
        campaign_status == CAMPAIGN_EVIDENCE_READY
        and (
            trade_count < minimum_trade_count
            or session_count < minimum_session_count
            or expectancy < minimum_positive_expectancy
            or profit_factor < minimum_profit_factor
            or max_drawdown > maximum_drawdown
            or evidence_score < minimum_evidence_score
        )
    ):
        if expectancy < minimum_positive_expectancy or profit_factor < minimum_profit_factor or max_drawdown > maximum_drawdown:
            campaign_status = CAMPAIGN_EVIDENCE_REJECTED
        else:
            campaign_status = CAMPAIGN_MORE_EVIDENCE_REQUIRED

    if campaign_status == CAMPAIGN_EVIDENCE_READY:
        if not (
            profitability_pass
            and walk_forward_pass
            and promotion_pass
            and capital_allocation_pass
            and trade_count >= minimum_trade_count
            and session_count >= minimum_session_count
            and expectancy >= minimum_positive_expectancy
            and profit_factor >= minimum_profit_factor
            and max_drawdown <= maximum_drawdown
            and evidence_score >= minimum_evidence_score
        ):
            campaign_status = CAMPAIGN_MORE_EVIDENCE_REQUIRED

    campaign_completed = campaign_status in {
        CAMPAIGN_EVIDENCE_READY,
        CAMPAIGN_EVIDENCE_REJECTED,
        CAMPAIGN_EVIDENCE_BLOCKED,
    }

    campaign_demo_candidate = (
        campaign_status == CAMPAIGN_EVIDENCE_READY
        and profitability_pass
        and walk_forward_pass
        and promotion_pass
        and capital_allocation_pass
        and not hard_block
        and len(blockers) == 0
    )

    next_action = (
        "collect_additional_evidence" if campaign_status in {CAMPAIGN_MORE_EVIDENCE_REQUIRED, CAMPAIGN_EVIDENCE_BLOCKED} else "operator_review"
    )
    if campaign_status == CAMPAIGN_EVIDENCE_READY:
        next_action = "build_demo_candidate_packet"

    if campaign_status in {CAMPAIGN_EVIDENCE_REJECTED}:
        next_action = "stop_and_reopen_strategy_design"
    elif campaign_status == CAMPAIGN_EVIDENCE_BLOCKED:
        next_action = "resolve_blockers_before_next_run"

    return {
        "campaign_evidence_completed": campaign_completed,
        "campaign_evidence_status": campaign_status,
        "campaign_demo_candidate": campaign_demo_candidate,
        "campaign_trade_count": trade_count,
        "campaign_session_count": session_count,
        "campaign_win_count": win_count,
        "campaign_loss_count": loss_count,
        "campaign_realized_pl": realized_pl,
        "campaign_expectancy": round(expectancy, 4),
        "campaign_profit_factor": round(profit_factor, 4),
        "campaign_max_drawdown": round(max_drawdown, 4),
        "campaign_evidence_score": round(evidence_score, 4),
        "campaign_blockers": blockers,
        "campaign_next_safe_action": next_action,
        "operator_review_required": True,
        "safety": {
            "paper_only": True,
            "broker_connection_active": False,
            "network_access": False,
            "credentials_accessed": False,
            "order_execution_enabled": False,
            "demo_execution_active": False,
            "live_trading_authorized": False,
            "capital_allocated": False,
            "capital_allocation_modified": False,
            "operator_review_required": True,
        },
    }


__all__ = [
    "CAMPAIGN_EVIDENCE_READY",
    "CAMPAIGN_MORE_EVIDENCE_REQUIRED",
    "CAMPAIGN_EVIDENCE_BLOCKED",
    "CAMPAIGN_EVIDENCE_REJECTED",
    "evaluate_campaign_evidence",
]
