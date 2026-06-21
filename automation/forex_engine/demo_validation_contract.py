from __future__ import annotations

from typing import Any, Iterable, Mapping


DEMO_CONTRACT_BLOCKED = "DEMO_CONTRACT_BLOCKED"
DEMO_CONTRACT_MORE_EVIDENCE_REQUIRED = "DEMO_CONTRACT_MORE_EVIDENCE_REQUIRED"
DEMO_CONTRACT_CONTINUE = "DEMO_CONTRACT_CONTINUE"
DEMO_CONTRACT_REJECTED = "DEMO_CONTRACT_REJECTED"
DEMO_CONTRACT_COMPLETE = "DEMO_CONTRACT_COMPLETE"

DEMO_CANDIDATE_CREATED = "DEMO_CANDIDATE_CREATED"
DEMO_CANDIDATE_ACTIVE = "DEMO_CANDIDATE_ACTIVE"
DEMO_CANDIDATE_PAUSED = "DEMO_CANDIDATE_PAUSED"
DEMO_CANDIDATE_REVOKED = "DEMO_CANDIDATE_REVOKED"
DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION = "DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION"


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "on", "pass", "passed", "ok"}


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


def _to_list(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, bytearray, dict)):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _read_first(mapping: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _first_candidate(state: Mapping[str, Any]) -> Mapping[str, Any]:
    candidate = _read_first(
        state,
        ("demo_candidate_record", "candidate_record", "candidate", "campaign_candidate"),
        default={},
    )
    if isinstance(candidate, Mapping):
        return candidate
    return {}


def _read_validation_results(state: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    results = _read_first(
        state,
        (
            "demo_validation_results",
            "validation_results",
            "validation_evidence",
            "results",
        ),
        default=None,
    )
    return _to_list(results)


def _add_blocker(blockers: list[str], blocker: str) -> None:
    if blocker not in blockers:
        blockers.append(blocker)


def _read_metric(result: Mapping[str, Any], aliases: tuple[str, ...], default: Any = 0.0) -> Any:
    return _read_first(result, aliases, default=default)


def _unsafe_blockers(state: Mapping[str, Any]) -> list[str]:
    flags = {
        "unsafe_broker_connection_detected": _to_bool(
            _read_first(state, ("broker_connection_detected", "broker_connection_active"), default=False),
            default=False,
        ),
        "unsafe_credential_access_detected": _to_bool(
            _read_first(state, ("credential_access_detected", "credentials_accessed"), default=False),
            default=False,
        ),
        "unsafe_account_identifier_detected": _to_bool(
            _read_first(state, ("account_identifier_detected", "account_identifiers_accessed"), default=False),
            default=False,
        ),
        "unsafe_order_execution_detected": _to_bool(
            _read_first(state, ("order_execution_detected", "order_execution_enabled"), default=False),
            default=False,
        ),
        "unsafe_live_trading_detected": _to_bool(
            _read_first(state, ("live_trading_authorized", "live_trading_detected"), default=False),
            default=False,
        ),
    }
    return [name for name, triggered in flags.items() if triggered]


def evaluate_demo_validation_contract(
    state: Mapping[str, Any],
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}

    limits = optional_limits or {}
    minimum_validation_sessions = _to_int(limits.get("minimum_validation_sessions", 3), default=3)
    minimum_validation_trades = _to_int(limits.get("minimum_validation_trades", 20), default=20)
    minimum_positive_expectancy = _to_float(limits.get("minimum_positive_expectancy", 0.01), default=0.01)
    minimum_profit_factor = _to_float(limits.get("minimum_profit_factor", 1.10), default=1.10)
    maximum_drawdown = _to_float(limits.get("maximum_drawdown", 10.0), default=10.0)
    minimum_evidence_score = _to_float(limits.get("minimum_evidence_score", 0.75), default=0.75)

    blockers: list[str] = []
    warnings: list[str] = []

    candidate = _first_candidate(state)
    candidate_id = _to_first = _read_first(candidate, ("candidate_id",), default="")
    candidate_state = _read_first(
        candidate,
        ("candidate_state",),
        default=DEMO_CANDIDATE_ACTIVE,
    )
    candidate_approved = _to_bool(
        _read_first(
            candidate,
            ("candidate_approved", "approved_for_demo_validation", "candidate_approved_for_demo_validation"),
            default=False,
        ),
        default=False,
    )

    validations = _read_validation_results(state)
    if not candidate:
        _add_blocker(blockers, "missing_candidate_record")
    if not validations:
        _add_blocker(blockers, "missing_validation_results")

    unsafe = _unsafe_blockers(state)
    for item in unsafe:
        _add_blocker(blockers, item)

    blocked = bool(unsafe) or (not candidate) or candidate_state in {
        DEMO_CANDIDATE_PAUSED,
        DEMO_CANDIDATE_REVOKED,
    }

    if candidate_state in {DEMO_CANDIDATE_PAUSED, DEMO_CANDIDATE_REVOKED}:
        _add_blocker(blockers, "candidate_state_blocked")
    if candidate_state == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION and not candidate_approved:
        _add_blocker(blockers, "candidate_not_approved_for_demo_validation")
    if candidate_state != DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION:
        _add_blocker(blockers, "candidate_not_approved_for_demo_validation")

    # Aggregate aliases and metrics
    session_count = 0
    trade_count = 0
    win_count = 0
    loss_count = 0
    realized_pl = 0.0
    expectancy_values: list[float] = []
    profit_factor_values: list[float] = []
    drawdown_values: list[float] = []
    evidence_score_values: list[float] = []
    risk_failures = False

    for record in validations:
        session_count += _to_int(_read_metric(record, ("validation_session_count", "session_count"), default=0), default=0)
        trade_count += _to_int(
            _read_metric(record, ("validation_trade_count", "trade_count", "closed_trade_count"), default=0),
            default=0,
        )
        win_count += _to_int(_read_metric(record, ("validation_win_count", "win_count"), default=0), default=0)
        loss_count += _to_int(_read_metric(record, ("validation_loss_count", "loss_count"), default=0), default=0)
        realized_pl += _to_float(_read_metric(record, ("validation_realized_pl", "realized_pl"), default=0.0), default=0.0)
        expectancy_values.append(
            _to_float(_read_metric(record, ("validation_expectancy", "expectancy"), default=0.0), default=0.0)
        )
        profit_factor_values.append(
            _to_float(_read_metric(record, ("validation_profit_factor", "profit_factor"), default=0.0), default=0.0)
        )
        drawdown_values.append(
            _to_float(
                _read_metric(record, ("validation_max_drawdown", "max_drawdown", "drawdown"), default=0.0),
                default=0.0,
            )
        )
        evidence_score_values.append(
            _to_float(_read_metric(record, ("validation_evidence_score", "evidence_score"), default=0.0), default=0.0)
        )
        if _to_bool(_read_metric(record, ("risk_failed", "risk_failure", "risk_failures_present"), default=False), default=False):
            risk_failures = True

    expectation = sum(expectancy_values) / len(expectancy_values) if expectancy_values else 0.0
    profit_factor = sum(profit_factor_values) / len(profit_factor_values) if profit_factor_values else 0.0
    drawdown = sum(drawdown_values) / len(drawdown_values) if drawdown_values else 0.0
    evidence_score = sum(evidence_score_values) / len(evidence_score_values) if evidence_score_values else 0.0

    if validations:
        if risk_failures:
            _add_blocker(blockers, "risk_failures_present")
        if session_count < minimum_validation_sessions:
            _add_blocker(blockers, "minimum_validation_sessions_not_met")
        if trade_count < minimum_validation_trades:
            _add_blocker(blockers, "minimum_validation_trades_not_met")
        if expectation < 0:
            _add_blocker(blockers, "negative_expectancy")
        elif expectation < minimum_positive_expectancy:
            _add_blocker(blockers, "expectancy_below_threshold")
        if profit_factor < minimum_profit_factor:
            _add_blocker(blockers, "profit_factor_below_threshold")
        if drawdown > maximum_drawdown:
            _add_blocker(blockers, "drawdown_above_threshold")
        if evidence_score < minimum_evidence_score:
            _add_blocker(blockers, "evidence_score_below_threshold")

    if blocked:
        status = DEMO_CONTRACT_BLOCKED
        live_readiness_candidate = False
        completed = True
    elif any(
        b in blockers
        for b in (
            "negative_expectancy",
            "profit_factor_below_threshold",
            "drawdown_above_threshold",
            "evidence_score_below_threshold",
            "risk_failures_present",
        )
    ):
        status = DEMO_CONTRACT_REJECTED
        live_readiness_candidate = False
        completed = True
    elif "missing_validation_results" in blockers:
        status = DEMO_CONTRACT_MORE_EVIDENCE_REQUIRED
        live_readiness_candidate = False
        completed = False
    elif any(
        b in blockers
        for b in (
            "minimum_validation_sessions_not_met",
            "minimum_validation_trades_not_met",
            "expectancy_below_threshold",
        )
    ):
        status = DEMO_CONTRACT_CONTINUE
        live_readiness_candidate = False
        completed = False
    elif blockers:
        status = DEMO_CONTRACT_BLOCKED
        live_readiness_candidate = False
        completed = True
    else:
        status = DEMO_CONTRACT_COMPLETE
        live_readiness_candidate = True
        completed = True

    status_to_safe_action = {
        DEMO_CONTRACT_MORE_EVIDENCE_REQUIRED: "collect_more_validation_results",
        DEMO_CONTRACT_CONTINUE: "improve_validation_evidence",
        DEMO_CONTRACT_REJECTED: "reject_candidate_and_restart_campaign",
        DEMO_CONTRACT_COMPLETE: "advance_to_live_readiness_review",
        DEMO_CONTRACT_BLOCKED: "resolve_blockers_before_review",
    }
    next_safe_action = status_to_safe_action.get(status, "collect_additional_validation_results")

    required_next_packets = _ranked_packets(blockers, status)

    return {
        "demo_validation_contract_completed": completed,
        "demo_validation_contract_status": status,
        "live_readiness_candidate": live_readiness_candidate,
        "blockers": blockers,
        "warnings": warnings,
        "next_safe_action": next_safe_action,
        "required_next_packets": required_next_packets,
        "contract_summary": {
            "candidate_id": candidate_id,
            "candidate_state": candidate_state,
            "candidate_approved": candidate_approved,
            "minimum_validation_sessions": minimum_validation_sessions,
            "minimum_validation_trades": minimum_validation_trades,
            "minimum_positive_expectancy": minimum_positive_expectancy,
            "minimum_profit_factor": minimum_profit_factor,
            "maximum_drawdown": maximum_drawdown,
            "minimum_evidence_score": minimum_evidence_score,
            "risk_failures_present": risk_failures,
        },
        "metric_summary": {
            "validation_session_count": session_count,
            "validation_trade_count": trade_count,
            "validation_win_count": win_count,
            "validation_loss_count": loss_count,
            "validation_realized_pl": round(realized_pl, 6),
            "validation_expectancy": round(expectation, 6),
            "validation_profit_factor": round(profit_factor, 6),
            "validation_max_drawdown": round(drawdown, 6),
            "validation_evidence_score": round(evidence_score, 6),
        },
        "safety": {
            "broker_connection_active": _to_bool(_read_first(state, ("broker_connection_active",), default=False), default=False),
            "network_access": False,
            "credentials_accessed": _to_bool(_read_first(state, ("credentials_accessed",), default=False), default=False),
            "account_identifiers_accessed": _to_bool(
                _read_first(state, ("account_identifiers_accessed",), default=False), default=False
            ),
            "order_execution_enabled": _to_bool(_read_first(state, ("order_execution_enabled",), default=False), default=False),
            "live_trading_authorized": _to_bool(_read_first(state, ("live_trading_authorized",), default=False), default=False),
            "capital_allocated": _to_bool(_read_first(state, ("capital_allocated",), default=False), default=False),
            "operator_review_required": True,
        },
    }


def _ranked_packets(blockers: list[str], status: str) -> list[str]:
    if status == DEMO_CONTRACT_MORE_EVIDENCE_REQUIRED:
        priority = [
            "collect_more_validation_results",
            "run_validation_session_batch",
            "refresh_live_readiness_packet",
        ]
    elif status in {DEMO_CONTRACT_BLOCKED, DEMO_CONTRACT_REJECTED}:
        priority = [
            "resolve_candidate_record_issues",
            "resolve_candidate_state",
            "run_safety_and_risk_repair",
            "collect_more_validation_results",
            "prepare_live_readiness_packet",
        ]
    elif status == DEMO_CONTRACT_CONTINUE:
        priority = [
            "collect_more_validation_results",
            "improve_risk_profile",
            "validate_expectancy_thresholds",
        ]
    else:
        priority = [
            "advance_to_live_readiness_review",
            "submit_for_one_shot_approval_review",
            "perform_hardening_checks",
        ]
    return [item for item in priority if True]
