from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

DEMO_VALIDATION_CONTINUE = "DEMO_VALIDATION_CONTINUE"
DEMO_VALIDATION_MORE_EVIDENCE_REQUIRED = "DEMO_VALIDATION_MORE_EVIDENCE_REQUIRED"
DEMO_VALIDATION_BLOCKED = "DEMO_VALIDATION_BLOCKED"
DEMO_VALIDATION_REJECTED = "DEMO_VALIDATION_REJECTED"
DEMO_VALIDATION_LIVE_READINESS_CANDIDATE = "DEMO_VALIDATION_LIVE_READINESS_CANDIDATE"

DEMO_CANDIDATE_CREATED = "DEMO_CANDIDATE_CREATED"
DEMO_CANDIDATE_ACTIVE = "DEMO_CANDIDATE_ACTIVE"
DEMO_CANDIDATE_PAUSED = "DEMO_CANDIDATE_PAUSED"
DEMO_CANDIDATE_REVOKED = "DEMO_CANDIDATE_REVOKED"
DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION = "DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION"


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on", "pass", "passed", "ok"}


def _to_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _read_sequence(value: Sequence[Mapping[str, Any]] | None) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _read_first(mapping: Mapping[str, Any], keys: Sequence[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _safe_get(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if isinstance(mapping, Mapping) and key in mapping:
            return mapping[key]
    return default


def _add_blocker(blockers: List[str], blocker: str) -> None:
    if blocker not in blockers:
        blockers.append(blocker)


def _blocked_state(candidate_id: str, candidate_state: str, campaign_status: str, reason: str) -> Dict[str, Any]:
    return {
        "demo_validation_completed": True,
        "demo_validation_status": DEMO_VALIDATION_BLOCKED,
        "live_readiness_candidate": False,
        "demo_candidate_id": candidate_id,
        "demo_validation_blockers": [reason],
        "demo_validation_summary": {
            "campaign_status": campaign_status,
            "candidate_state": candidate_state,
            "minimum_validation_sessions": 3,
            "minimum_validation_trades": 20,
            "minimum_positive_expectancy": 0.01,
            "minimum_profit_factor": 1.10,
            "maximum_drawdown": 10.0,
            "minimum_evidence_score": 0.75,
        },
        "demo_validation_next_safe_action": "provide_demo_candidate_record",
        "operator_review_required": True,
        "safety": {
            "paper_only": False,
            "demo_validation_only": True,
            "broker_connection_active": False,
            "network_access": False,
            "credentials_accessed": False,
            "order_execution_enabled": False,
            "demo_order_submission_enabled": False,
            "demo_execution_active": False,
            "live_trading_authorized": False,
            "capital_allocated": False,
            "capital_allocation_modified": False,
            "operator_review_required": True,
        },
        "demo_validation_metrics": {
            "validation_session_count": 0,
            "validation_trade_count": 0,
            "validation_win_count": 0,
            "validation_loss_count": 0,
            "validation_realized_pl": 0.0,
            "validation_expectancy": 0.0,
            "validation_profit_factor": 0.0,
            "validation_max_drawdown": 0.0,
            "validation_evidence_score": 0.0,
            "candidate_state": candidate_state,
        },
    }


def _next_action(status: str, candidate_state: str, blockers: list[str]) -> str:
    if status == DEMO_VALIDATION_BLOCKED:
        return f"resolve_candidate_state:{candidate_state}"
    if status == DEMO_VALIDATION_REJECTED:
        return "review_and_reject_candidate"
    if status == DEMO_VALIDATION_MORE_EVIDENCE_REQUIRED:
        if not blockers:
            return "collect_more_validation_results"
        if "missing_validation_results" in blockers:
            return "collect_first_validation_batch"
        return "improve_validation_evidence"
    if status == DEMO_VALIDATION_LIVE_READINESS_CANDIDATE:
        return "advance_to_live_readiness_review"
    return "continue_validation"


def _average(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def evaluate_demo_validation_supervisor(
    demo_candidate_record: Mapping[str, Any] | None,
    demo_validation_results: Sequence[Mapping[str, Any]] | None = None,
    optional_limits: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    candidate = demo_candidate_record or {}
    validations = _read_sequence(demo_validation_results)
    limits = optional_limits or {}

    minimum_validation_sessions = _to_int(limits.get("minimum_validation_sessions", 3), default=3)
    minimum_validation_trades = _to_int(limits.get("minimum_validation_trades", 20), default=20)
    minimum_positive_expectancy = _to_float(limits.get("minimum_positive_expectancy", 0.01), default=0.01)
    minimum_profit_factor = _to_float(limits.get("minimum_profit_factor", 1.10), default=1.10)
    maximum_drawdown = _to_float(limits.get("maximum_drawdown", 10.0), default=10.0)
    minimum_evidence_score = _to_float(limits.get("minimum_evidence_score", 0.75), default=0.75)

    candidate_id = _to_str(candidate.get("candidate_id", ""))
    candidate_state = _to_str(candidate.get("candidate_state", DEMO_CANDIDATE_CREATED))
    campaign_status = _to_str(candidate.get("campaign_status", ""))

    if not candidate:
        return _blocked_state(
            candidate_id="",
            candidate_state=candidate_state,
            campaign_status=campaign_status,
            reason="missing_candidate_record",
        )

    if validations:
        validation_session_count = 0
        trade_count_sum = 0
        win_count_sum = 0
        loss_count_sum = 0
        realized_pl_sum = 0.0
        expectancy_values: list[float] = []
        profit_factor_values: list[float] = []
        drawdown_values: list[float] = []
        evidence_score_values: list[float] = []
        for result in validations:
            validation_session_count += _to_int(_read_first(result, ("validation_session_count", "session_count"), default=0), default=0)
            trade_count_sum += _to_int(
                _read_first(result, ("validation_trade_count", "trade_count", "closed_trade_count"), default=0),
                default=0,
            )
            win_count_sum += _to_int(_read_first(result, ("validation_win_count", "win_count"), default=0), default=0)
            loss_count_sum += _to_int(_read_first(result, ("validation_loss_count", "loss_count"), default=0), default=0)
            realized_pl_sum += _to_float(_read_first(result, ("validation_realized_pl", "realized_pl"), default=0.0), default=0.0)
            expectancy_values.append(
                _to_float(_read_first(result, ("validation_expectancy", "expectancy"), default=0.0), default=0.0)
            )
            profit_factor_values.append(
                _to_float(_read_first(result, ("validation_profit_factor", "profit_factor"), default=0.0), default=0.0)
            )
            drawdown_values.append(
                _to_float(_read_first(result, ("validation_max_drawdown", "max_drawdown", "drawdown"), default=0.0), default=0.0)
            )
            evidence_score_values.append(
                _to_float(
                    _read_first(result, ("validation_evidence_score", "evidence_score"), default=0.0),
                    default=0.0,
                )
            )
    else:
        validation_session_count = 0
        trade_count_sum = 0
        win_count_sum = 0
        loss_count_sum = 0
        realized_pl_sum = 0.0
        expectancy_values = [0.0]
        profit_factor_values = [0.0]
        drawdown_values = [0.0]
        evidence_score_values = [0.0]

    expectancy_avg = _average(expectancy_values)
    profit_factor_avg = _average(profit_factor_values)
    drawdown_avg = _average(drawdown_values)
    evidence_score_avg = _average(evidence_score_values)

    blockers: list[str] = []
    if candidate_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION and not _to_bool(
        candidate.get("candidate_approved", False), default=False
    ):
        _add_blocker(blockers, "candidate_not_approved_for_demo_validation")

    if candidate_state in {DEMO_CANDIDATE_PAUSED, DEMO_CANDIDATE_REVOKED}:
        _add_blocker(blockers, f"candidate_state_blocked:{candidate_state}")

    if not validations:
        _add_blocker(blockers, "missing_validation_results")

    for item in validations:
        if _to_bool(_safe_get(item, "risk_failed", "risk_failure", default=False), default=False):
            _add_blocker(blockers, "risk_failures_present")
            break

    if trade_count_sum < minimum_validation_trades:
        _add_blocker(blockers, "minimum_validation_trades_not_met")
    if validation_session_count < minimum_validation_sessions:
        _add_blocker(blockers, "minimum_validation_sessions_not_met")

    if expectancy_avg < 0:
        _add_blocker(blockers, "negative_expectancy")
    elif expectancy_avg < minimum_positive_expectancy:
        _add_blocker(blockers, "expectancy_below_threshold")
    if profit_factor_avg < minimum_profit_factor:
        _add_blocker(blockers, "profit_factor_below_threshold")
    if drawdown_avg > maximum_drawdown:
        _add_blocker(blockers, "drawdown_above_threshold")
    if evidence_score_avg < minimum_evidence_score:
        _add_blocker(blockers, "evidence_score_below_threshold")

    approved = bool(_to_bool(candidate.get("candidate_approved", False), default=False))
    if candidate_state in {DEMO_CANDIDATE_PAUSED, DEMO_CANDIDATE_REVOKED} or (
        candidate_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION and not approved
    ):
        status = DEMO_VALIDATION_BLOCKED
        live_readiness = False
    elif not validations:
        status = DEMO_VALIDATION_MORE_EVIDENCE_REQUIRED
        live_readiness = False
    elif any(flag in blockers for flag in {
        "risk_failures_present",
        "negative_expectancy",
        "profit_factor_below_threshold",
        "drawdown_above_threshold",
        "evidence_score_below_threshold",
    }):
        status = DEMO_VALIDATION_REJECTED
        live_readiness = False
    elif minimum_validation_sessions <= validation_session_count and minimum_validation_trades <= trade_count_sum:
        status = DEMO_VALIDATION_LIVE_READINESS_CANDIDATE
        live_readiness = (
            candidate_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION
            and expectancy_avg > 0
            and profit_factor_avg >= minimum_profit_factor
            and drawdown_avg <= maximum_drawdown
            and evidence_score_avg >= minimum_evidence_score
            and not blockers
        )
        if not live_readiness:
            status = DEMO_VALIDATION_CONTINUE
    else:
        status = DEMO_VALIDATION_CONTINUE
        live_readiness = False

    next_action = _next_action(status, candidate_state, blockers)
    completed = status in {
        DEMO_VALIDATION_LIVE_READINESS_CANDIDATE,
        DEMO_VALIDATION_BLOCKED,
        DEMO_VALIDATION_REJECTED,
    }

    return {
        "demo_validation_completed": completed,
        "demo_validation_status": status,
        "live_readiness_candidate": live_readiness,
        "demo_candidate_id": candidate_id,
        "demo_validation_blockers": blockers,
        "demo_validation_summary": {
            "campaign_status": campaign_status,
            "candidate_state": candidate_state,
            "minimum_validation_sessions": minimum_validation_sessions,
            "minimum_validation_trades": minimum_validation_trades,
            "minimum_positive_expectancy": minimum_positive_expectancy,
            "minimum_profit_factor": minimum_profit_factor,
            "maximum_drawdown": maximum_drawdown,
            "minimum_evidence_score": minimum_evidence_score,
        },
        "demo_validation_next_safe_action": next_action,
        "operator_review_required": True,
        "safety": {
            "paper_only": False,
            "demo_validation_only": True,
            "broker_connection_active": False,
            "network_access": False,
            "credentials_accessed": False,
            "order_execution_enabled": False,
            "demo_order_submission_enabled": False,
            "demo_execution_active": False,
            "live_trading_authorized": False,
            "capital_allocated": False,
            "capital_allocation_modified": False,
            "operator_review_required": True,
        },
        "demo_validation_metrics": {
            "validation_session_count": validation_session_count,
            "validation_trade_count": trade_count_sum,
            "validation_win_count": win_count_sum,
            "validation_loss_count": loss_count_sum,
            "validation_realized_pl": round(realized_pl_sum, 6),
            "validation_expectancy": round(expectancy_avg, 6),
            "validation_profit_factor": round(profit_factor_avg, 6),
            "validation_max_drawdown": round(drawdown_avg, 6),
            "validation_evidence_score": round(evidence_score_avg, 6),
            "candidate_state": candidate_state,
        },
    }
