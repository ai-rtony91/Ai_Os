from __future__ import annotations

from typing import Any, Dict, Mapping

CAMPAIGN_CONTINUE = "CAMPAIGN_CONTINUE"
CAMPAIGN_MORE_EVIDENCE_REQUIRED = "CAMPAIGN_MORE_EVIDENCE_REQUIRED"
CAMPAIGN_BLOCKED = "CAMPAIGN_BLOCKED"
CAMPAIGN_REJECTED = "CAMPAIGN_REJECTED"
CAMPAIGN_DEMO_CANDIDATE = "CAMPAIGN_DEMO_CANDIDATE"
CAMPAIGN_EVIDENCE_READY = "CAMPAIGN_EVIDENCE_READY"
CAMPAIGN_EVIDENCE_REJECTED = "CAMPAIGN_EVIDENCE_REJECTED"

MINIMUM_EXPECTANCY = 0.01
MINIMUM_PROFIT_FACTOR = 1.10
MAXIMUM_DRAWDOWN = 10.0


def _status_from_payload(value: Mapping[str, Any] | None, default: str = "") -> str:
    if not isinstance(value, Mapping):
        return default
    for key in (
        "status",
        "campaign_evidence_status",
        "campaign_status",
        "promotion_status",
        "capital_allocation_status",
        "decision",
        "result",
    ):
        if key in value:
            return str(value[key]).upper()
    return default


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


def _as_mapping(value: Mapping[str, Any] | None) -> Dict[str, Any]:
    return dict(value or {})


def _is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on", "passed", "pass", "ready", "approved"}


def _append_if_missing(container: list[str], reason: str) -> None:
    if reason not in container:
        container.append(reason)


def evaluate_campaign_supervisor(
    campaign_evidence_result: Mapping[str, Any] | None,
    promotion_workflow_result: Mapping[str, Any] | None,
    capital_allocation_result: Mapping[str, Any] | None,
    optional_strategy_metadata: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    evidence = _as_mapping(campaign_evidence_result)
    promotion = _as_mapping(promotion_workflow_result)
    capital = _as_mapping(capital_allocation_result)
    strategy_metadata = _as_mapping(optional_strategy_metadata)

    campaign_status = evidence.get("campaign_evidence_status", CAMPAIGN_MORE_EVIDENCE_REQUIRED)
    promotion_status = _status_from_payload(promotion)
    capital_status = _status_from_payload(capital)

    trade_count = _to_int(evidence.get("campaign_trade_count", evidence.get("trade_count")))
    session_count = _to_int(evidence.get("campaign_session_count", evidence.get("session_count")))
    expectancy = _to_float(evidence.get("campaign_expectancy", evidence.get("expectancy")))
    profit_factor = _to_float(evidence.get("campaign_profit_factor", evidence.get("profit_factor")))
    drawdown = _to_float(evidence.get("campaign_max_drawdown", evidence.get("drawdown", evidence.get("max_drawdown"))))
    evidence_score = _to_float(
        evidence.get("campaign_evidence_score", evidence.get("evidence_score", evidence.get("score")))
    )

    blockers: list[str] = []
    decision: str
    campaign_completed = False

    # Capital allocation control is the hard stop state for BLOCKED.
    if capital_status in {"CAMPAIGN_BLOCKED", "BLOCKED", "FAILED", "REJECTED", "FAIL"} or _is_true(capital.get("blocked", False)):
        decision = CAMPAIGN_BLOCKED
        _append_if_missing(blockers, "capital_allocation_gate_blocked")
    elif not _is_true(promotion.get("passed", True)) or promotion_status in {"BLOCKED", "FAILED", "REJECTED", "FAIL", "REJECT"}:
        decision = CAMPAIGN_REJECTED
        _append_if_missing(blockers, "promotion_workflow_rejected")
    elif campaign_status == CAMPAIGN_EVIDENCE_REJECTED:
        decision = CAMPAIGN_REJECTED
        _append_if_missing(blockers, "campaign_evidence_rejected")
    elif campaign_status == CAMPAIGN_EVIDENCE_READY:
        if expectancy < MINIMUM_EXPECTANCY:
            decision = CAMPAIGN_REJECTED
            _append_if_missing(blockers, "negative_expectancy")
        elif profit_factor < MINIMUM_PROFIT_FACTOR:
            decision = CAMPAIGN_REJECTED
            _append_if_missing(blockers, "profit_factor_below_threshold")
        elif drawdown > MAXIMUM_DRAWDOWN:
            decision = CAMPAIGN_REJECTED
            _append_if_missing(blockers, "excessive_drawdown")
        elif (
            _is_true(promotion.get("passed", promotion_status == "PASS"))
            and _is_true(capital.get("passed", capital_status == "PASS"))
            and not blockers
            and campaign_status == CAMPAIGN_EVIDENCE_READY
        ):
            decision = CAMPAIGN_DEMO_CANDIDATE
            campaign_completed = True
        else:
            decision = CAMPAIGN_CONTINUE
            _append_if_missing(blockers, "campaign_or_gate_controls_pending")
    else:
        if not evidence:
            decision = CAMPAIGN_MORE_EVIDENCE_REQUIRED
            _append_if_missing(blockers, "missing_campaign_evidence")
        else:
            decision = CAMPAIGN_MORE_EVIDENCE_REQUIRED
            _append_if_missing(blockers, "campaign_evidence_not_ready")

    if decision == CAMPAIGN_DEMO_CANDIDATE:
        campaign_completed = True

    if evidence.get("campaign_blockers"):
        blockers.extend(item for item in evidence.get("campaign_blockers", []) if isinstance(item, str))
    if promotion.get("blocked_reasons"):
        blockers.extend(item for item in promotion.get("blocked_reasons", []) if isinstance(item, str))
    if capital.get("blocked_reasons"):
        blockers.extend(item for item in capital.get("blocked_reasons", []) if isinstance(item, str))

    blockers = sorted(set(blockers))

    if decision in {CAMPAIGN_DEMO_CANDIDATE, CAMPAIGN_REJECTED, CAMPAIGN_BLOCKED, CAMPAIGN_MORE_EVIDENCE_REQUIRED}:
        campaign_completed = True

    if decision == CAMPAIGN_DEMO_CANDIDATE and blockers:
        decision = CAMPAIGN_CONTINUE
        campaign_completed = False
        _append_if_missing(blockers, "blockers_present")

    if decision == CAMPAIGN_DEMO_CANDIDATE:
        next_action = "build_demo_candidate_packet"
    elif decision == CAMPAIGN_BLOCKED:
        next_action = "resolve_capital_allocation_blockers"
    elif decision == CAMPAIGN_REJECTED:
        next_action = "stop_and_reassess_strategy"
    elif decision == CAMPAIGN_MORE_EVIDENCE_REQUIRED:
        next_action = "collect_more_campaign_evidence"
    else:
        next_action = "continue_orchestrated_campaign"

    return {
        "campaign_completed": campaign_completed,
        "campaign_status": decision,
        "campaign_demo_candidate": decision == CAMPAIGN_DEMO_CANDIDATE,
        "campaign_blockers": blockers,
        "campaign_summary": {
            "strategy": strategy_metadata.get("strategy_name", "unknown"),
            "strategy_id": strategy_metadata.get("strategy_id"),
            "trade_count": trade_count,
            "session_count": session_count,
            "evidence_ready": evidence.get("campaign_evidence_status") == CAMPAIGN_EVIDENCE_READY,
            "promotion_status": promotion_status,
            "capital_allocation_status": capital_status,
        },
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
        "campaign_metrics": {
            "trade_count": trade_count,
            "session_count": session_count,
            "expectancy": round(expectancy, 4),
            "profit_factor": round(profit_factor, 4),
            "drawdown": round(drawdown, 4),
            "evidence_score": round(evidence_score, 4),
            "promotion_status": promotion_status,
            "capital_allocation_status": capital_status,
        },
    }


__all__ = [
    "CAMPAIGN_CONTINUE",
    "CAMPAIGN_MORE_EVIDENCE_REQUIRED",
    "CAMPAIGN_BLOCKED",
    "CAMPAIGN_REJECTED",
    "CAMPAIGN_DEMO_CANDIDATE",
    "evaluate_campaign_supervisor",
]
