from __future__ import annotations

from typing import Any, Dict, List, Optional


SELF_IMPROVEMENT_MODE = "PAPER_ONLY"
SELF_IMPROVEMENT_ALLOWED = "allowed"
SELF_IMPROVEMENT_BLOCKED = "blocked"
SELF_IMPROVEMENT_REQUIRES_APPROVAL = "requires_approval"


class RejectionReason:
    NONE = "none"
    INVALID_REPLAY = "invalid_replay"
    INVALID_EVIDENCE = "invalid_evidence"
    NON_PAPER_MODE = "non_paper_mode"
    LIVE_TRADING_BLOCKED = "live_trading_blocked"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    PROTECTED_ACTION_REQUESTED = "protected_action_requested"
    MISSING_SESSION_METRICS = "missing_session_metrics"
    EVIDENCE_PATH_INVALID = "evidence_path_invalid"


_PROTECTED_PATTERNS = (
    "live",
    "broker",
    "auth token",
    "account id",
    "account number",
    "apikey",
    "api key",
    "order submit",
    "oanda submit",
    "real trade",
    "leverage",
    "martingale",
    "recovery",
    "risk increase",
)

_IMPROVEMENT_SCOPE = {
    "tighten_spread_cap": "market_data_filters",
    "add_missing_rejection_regression_test": "candidate_quality",
    "reduce_risk_multiplier_on_drawdown": "trade_risk_governance",
    "improve_stale_data_rejection": "data_guardrails",
    "improve_no_trade_filter": "strategy_candidate_logic",
    "add_duplicate_setup_block_regression": "queue_rules",
}


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _safe_mode_ok(mode: Any) -> bool:
    if mode is None:
        return True
    return mode == SELF_IMPROVEMENT_MODE


def _invalid_path(path: Optional[str]) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if path.startswith(("/", "\\")) or ":" in path:
        return True
    if ".." in path:
        return True
    return False


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}


def _pick_metric(replay: Dict[str, Any], evidence: Dict[str, Any], key: str, default: float = 0.0) -> float:
    if key in replay and replay.get(key) is not None:
        return _to_float(replay.get(key), default)
    if key in evidence and evidence.get(key) is not None:
        return _to_float(evidence.get(key), default)
    nested = evidence.get("metrics", {})
    if isinstance(nested, dict) and key in nested and nested.get(key) is not None:
        return _to_float(nested.get(key), default)
    return default


def _extract_counts(replay: Dict[str, Any]) -> Dict[str, int]:
    return {
        "trades_closed": _to_int(replay.get("trades_closed")),
        "wins": _to_int(replay.get("wins")),
        "losses": _to_int(replay.get("losses")),
        "breakeven": _to_int(replay.get("breakeven")),
    }


def _aggregate_rejections(
    evidence: Dict[str, Any],
    replay: Dict[str, Any],
    supervisor: Dict[str, Any],
) -> tuple:
    rejected_setups = 0
    duplicate_setups = 0
    risk_failures = 0
    rejection_summary: Dict[str, int] = {}
    replay_reasons: set[str] = set()

    def _count(reason_raw: Any, *, allow_if_in_replay: bool = False) -> None:
        nonlocal rejected_setups, duplicate_setups, risk_failures
        reason = str(reason_raw)
        normalized = _norm(reason)
        if normalized == "":
            return
        if not allow_if_in_replay and normalized in replay_reasons:
            return
        rejection_summary[reason] = rejection_summary.get(reason, 0) + 1
        if normalized in {"duplicate_setup", "duplicate_setups"}:
            rejected_setups += 1
            duplicate_setups += 1
        elif normalized in {"duplicate setup", "duplicate-setups", "duplicate setup blocked"}:
            rejected_setups += 1
        if "risk" in normalized:
            risk_failures += 1
        replay_reasons.add(normalized)

    for item in _to_list(replay.get("blocked_reasons") or replay.get("rejections") or []):
        r = _norm(item)
        if r == "":
            continue
        _count(item, allow_if_in_replay=True)
        replay_reasons.add(r)

    for item in _to_list(evidence.get("rejected_reasons") or evidence.get("rejection_reasons") or []):
        r = _norm(item)
        if r == "":
            continue
        if "duplicate_setup" in r or "duplicate_setups" in r or r not in replay_reasons:
            _count(item)

    for item in _to_list(supervisor.get("rejected_candidates") or supervisor.get("risk_rejections") or []):
        if isinstance(item, dict):
            reasons = [item.get("reason"), item.get("rejected_reason")]
            reason = str(next((r for r in reasons if r), ""))
            reason = reason if reason else "candidate_rejected"
            if reason == "candidate_rejected":
                continue
            normalized = _norm(reason)
            if normalized == "":
                continue
            if normalized in replay_reasons:
                continue
            if normalized not in {"duplicate_setup", "duplicate_setups"} and "duplicate_setup" not in normalized:
                continue
            _count(reason)
        else:
            normalized = _norm(item)
            if not normalized:
                continue
            if "duplicate_setup" in normalized or "duplicate_setups" in normalized:
                _count(item)

    return rejected_setups, risk_failures, rejection_summary, duplicate_setups


def _evidence_quality(replay: Dict[str, Any], evidence: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, Any]:
    counts = _extract_counts(replay)
    min_trades = _to_int(limits.get("min_trades"), 10)
    total_trades = counts["trades_closed"]
    missing_fields = []
    for field in ("net_pnl", "wins", "losses", "breakeven", "trades_closed"):
        if replay.get(field) is None:
            missing_fields.append(field)
    return {
        "sample_ready": total_trades >= min_trades and not missing_fields,
        "total_trades": total_trades,
        "min_trades_required": min_trades,
        "missing_fields": missing_fields,
    }


def _propose_improvement(metrics: Dict[str, float], risk_failures: int, rejection_summary: Dict[str, int], counts: Dict[str, int]) -> tuple[str, str, List[str]]:
    if risk_failures >= 3 or _to_float(metrics.get("max_drawdown"), 0.0) > 0:
        return (
            "reduce_risk_multiplier_on_drawdown",
            _IMPROVEMENT_SCOPE["reduce_risk_multiplier_on_drawdown"],
            ["test_risk_governor_drawdown_reduction", "test_max_open_risk_and_session_cap_bounds"],
        )
    if _to_int(rejection_summary.get("stale_data_rejected"), 0) > 0:
        return (
            "improve_stale_data_rejection",
            _IMPROVEMENT_SCOPE["improve_stale_data_rejection"],
            ["test_stale_market_data_rejected_deterministically", "test_invalid_timestamp_blocks"],
        )
    if _to_int(rejection_summary.get("spread_too_high"), 0) > 0:
        return (
            "tighten_spread_cap",
            _IMPROVEMENT_SCOPE["tighten_spread_cap"],
            ["test_high_spread_is_rejected", "test_spread_cap_applies_consistently"],
        )
    if counts["losses"] > counts["wins"]:
        return (
            "improve_no_trade_filter",
            _IMPROVEMENT_SCOPE["improve_no_trade_filter"],
            ["test_no_trade_signal_reason_codes", "test_candidate_filter_reduces_false_positives"],
        )
    if _to_int(rejection_summary.get("duplicate_setup"), 0) > 0:
        return (
            "add_duplicate_setup_block_regression",
            _IMPROVEMENT_SCOPE["add_duplicate_setup_block_regression"],
            ["test_duplicate_setup_blocked", "test_duplicate_direction_per_pair_block"],
        )
    return (
        "add_missing_rejection_regression_test",
        _IMPROVEMENT_SCOPE["add_missing_rejection_regression_test"],
        ["test_rejection_reason_coverage", "test_rejection_reason_determinism"],
    )


def _contains_protected_action(text: Any) -> bool:
    if not isinstance(text, str):
        return False
    needle = text.lower()
    return any(term in needle for term in _PROTECTED_PATTERNS)


def _base_payload(
    *,
    allowed: bool,
    decision: str,
    blocked_reason: str,
    blocked_reasons: List[str],
    warnings: List[str],
    replay: Dict[str, Any],
    evidence: Dict[str, Any],
    evidence_path: str,
    metadata: Dict[str, Any],
    quality: Dict[str, Any],
    counts: Dict[str, int],
    risk_failures: int,
    rejection_summary: Dict[str, int],
    rejected_setup_summary: Dict[str, int],
    tests: List[str],
    evidence_used: Dict[str, Any],
    recommended_improvement: str,
    recommended_improvement_scope: str,
    win_rate: float,
    net_pnl: float,
    max_drawdown: float,
    strategy_performance: Dict[str, Any],
    risk_failure_metrics: Dict[str, Any],
    winning_summary: Dict[str, Any],
    losing_summary: Dict[str, Any],
    protected_action: bool,
    approval_required: bool,
    approval_reason: str,
    no_live_setting_change: bool = False,
) -> Dict[str, Any]:
    return {
        "allowed": allowed,
        "decision": decision,
        "blocked_reason": blocked_reason,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "paper_only": True,
        "mode": SELF_IMPROVEMENT_MODE,
        "evidence_quality": quality,
        "total_trades": counts["trades_closed"],
        "wins": counts["wins"],
        "losses": counts["losses"],
        "breakeven": counts["breakeven"],
        "win_rate_pct": win_rate,
        "net_pnl": net_pnl,
        "max_drawdown": max_drawdown,
        "risk_failures": risk_failures,
        "rejection_summary": rejection_summary,
        "winning_trade_summary": winning_summary,
        "losing_trade_summary": losing_summary,
        "rejected_setup_summary": rejected_setup_summary,
        "strategy_performance_metrics": strategy_performance,
        "risk_failure_metrics": risk_failure_metrics,
        "recommended_improvement": recommended_improvement,
        "recommended_improvement_scope": recommended_improvement_scope,
        "proposed_regression_tests": tests,
        "protected_action_detected": protected_action,
        "approval_required": approval_required,
        "approval_reason": approval_reason,
        "no_live_setting_change": no_live_setting_change,
        "evidence_used": evidence_used,
        "evidence_path": evidence_path,
        "safety": {
            "paper_only": True,
            "broker": False,
            "live_trading": False,
            "credentials": False,
            "real_orders": False,
            "network_access": False,
        },
        "next_safe_action": (
            "Apply one bounded paper-safe improvement."
            if allowed and not protected_action
            else ("Route protected actions to approval before execution." if protected_action else "Collect more paper evidence and rerun.")
        ),
        "metadata": metadata,
    }


def _build_failure(
    blocked_reason: str,
    blocked_reasons: List[str],
    replay: Dict[str, Any],
    evidence: Dict[str, Any],
    supervisor: Dict[str, Any],
    evidence_path: str,
    metadata: Dict[str, Any],
    protected_action: bool,
    approval_required: bool,
    approval_reason: str,
    no_live_setting_change: bool,
    *,  # ensure deterministic extension points
    warnings: Optional[List[str]] = None,
    recommend_collect_more: bool = False,
    counts: Optional[Dict[str, int]] = None,
    quality: Optional[Dict[str, Any]] = None,
    rejection_summary: Optional[Dict[str, int]] = None,
    risk_failures: int = 0,
    duplicate_setups: int = 0,
) -> Dict[str, Any]:
    counts = counts or _extract_counts(replay)
    quality = quality or _evidence_quality(replay, evidence, {})
    if recommend_collect_more:
        improvement = "collect_more_paper_evidence"
        scope = "data_collection"
        tests = ["test_collect_more_paper_evidence", "test_complete_session_replay_payload"]
    else:
        improvement = "tighten_spread_cap"
        scope = _IMPROVEMENT_SCOPE["tighten_spread_cap"]
        tests = ["test_safe_fallback_behavior"]
    return _base_payload(
        allowed=False,
        decision=SELF_IMPROVEMENT_REQUIRES_APPROVAL if protected_action else SELF_IMPROVEMENT_BLOCKED,
        blocked_reason=blocked_reason,
        blocked_reasons=blocked_reasons,
        warnings=warnings or [],
        replay=replay,
        evidence=evidence,
        evidence_path=evidence_path,
        metadata=metadata,
        quality=quality,
        counts=counts,
        risk_failures=risk_failures,
        rejection_summary=rejection_summary or {},
        rejected_setup_summary={"duplicate_setups": duplicate_setups},
        tests=tests,
        evidence_used={"replay": replay, "evidence_summary": evidence, "supervisor_summary": supervisor},
        recommended_improvement=improvement,
        recommended_improvement_scope=scope,
        win_rate=_to_float(replay.get("win_rate_pct"), 0.0),
        net_pnl=_to_float(replay.get("net_pnl"), 0.0),
        max_drawdown=abs(_to_float(replay.get("max_drawdown"), 0.0)),
        strategy_performance={"candidate_total": 0, "selected_total": 0, "gross_profit": 0.0, "gross_loss": 0.0},
        risk_failure_metrics={"risk_failures": risk_failures, "risk_failure_ratio": 0.0, "max_drawdown": abs(_to_float(replay.get("max_drawdown"), 0.0))},
        winning_summary={"wins": counts["wins"], "gross_profit": 0.0, "win_ratio": 0.0},
        losing_summary={"losses": counts["losses"], "gross_loss": 0.0, "loss_ratio": 0.0},
        protected_action=protected_action,
        approval_required=approval_required,
        approval_reason=approval_reason,
        no_live_setting_change=no_live_setting_change,
    )


def review_self_improvement(
    session_replay: Optional[Dict[str, Any]] = None,
    evidence_summary: Optional[Dict[str, Any]] = None,
    supervisor_summary: Optional[Dict[str, Any]] = None,
    limits: Optional[Dict[str, Any]] = None,
    requested_change: Optional[str] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = dict(metadata or {})
    limits = _as_dict(limits)
    replay = _as_dict(session_replay)
    evidence = _as_dict(evidence_summary)
    supervisor = _as_dict(supervisor_summary)

    if _invalid_path(evidence_path):
        return _build_failure(
            RejectionReason.EVIDENCE_PATH_INVALID,
            [RejectionReason.EVIDENCE_PATH_INVALID],
            replay,
            evidence,
            supervisor,
            evidence_path or "",
            metadata,
            protected_action=False,
            approval_required=False,
            approval_reason="",
            no_live_setting_change=False,
            recommend_collect_more=False,
        )

    if session_replay is not None and not isinstance(session_replay, dict):
        return _build_failure(
            RejectionReason.INVALID_REPLAY,
            [RejectionReason.INVALID_REPLAY],
            {},
            evidence,
            supervisor,
            evidence_path or "",
            metadata,
            protected_action=False,
            approval_required=False,
            approval_reason="",
            no_live_setting_change=False,
            recommend_collect_more=False,
        )
    if evidence_summary is not None and not isinstance(evidence_summary, dict):
        return _build_failure(
            RejectionReason.INVALID_EVIDENCE,
            [RejectionReason.INVALID_EVIDENCE],
            replay,
            {},
            supervisor,
            evidence_path or "",
            metadata,
            protected_action=False,
            approval_required=False,
            approval_reason="",
            no_live_setting_change=False,
            recommend_collect_more=False,
        )

    if not _safe_mode_ok(replay.get("mode")) or not _safe_mode_ok(evidence.get("mode")) or not _safe_mode_ok(supervisor.get("mode")):
        return _build_failure(
            RejectionReason.NON_PAPER_MODE,
            [RejectionReason.NON_PAPER_MODE],
            replay,
            evidence,
            supervisor,
            evidence_path or "",
            metadata,
            protected_action=False,
            approval_required=False,
            approval_reason="",
            no_live_setting_change=False,
            recommend_collect_more=False,
        )

    if _contains_protected_action(requested_change):
        return _build_failure(
            RejectionReason.PROTECTED_ACTION_REQUESTED,
            [RejectionReason.PROTECTED_ACTION_REQUESTED],
            replay,
            evidence,
            supervisor,
            evidence_path or "",
            metadata,
            protected_action=True,
            approval_required=True,
            approval_reason="Requested change is outside paper-only safe scope.",
            no_live_setting_change=True,
        )

    counts = _extract_counts(replay)
    rejected_setups, risk_failures, rejection_summary, duplicate_setups = _aggregate_rejections(evidence, replay, supervisor)
    quality = _evidence_quality(replay, evidence, limits)

    missing = []
    for key in ("wins", "losses", "breakeven", "net_pnl"):
        if replay.get(key) is None:
            missing.append(key)

    if counts["trades_closed"] < 10 or missing or not quality["sample_ready"]:
        return _build_failure(
            RejectionReason.INSUFFICIENT_EVIDENCE,
            [RejectionReason.INSUFFICIENT_EVIDENCE, RejectionReason.MISSING_SESSION_METRICS],
            replay,
            evidence,
            supervisor,
            evidence_path or "",
            metadata,
            protected_action=False,
            approval_required=False,
            approval_reason="",
            no_live_setting_change=False,
            warnings=["insufficient_or_incomplete_session_metrics"],
            recommend_collect_more=True,
            counts=counts,
            quality=quality,
            rejection_summary=rejection_summary,
            risk_failures=risk_failures,
            duplicate_setups=duplicate_setups,
        )

    net_pnl = _pick_metric(replay, evidence, "net_pnl", 0.0)
    max_drawdown = abs(_pick_metric(replay, evidence, "max_drawdown", 0.0))
    gross_profit = _pick_metric(replay, evidence, "gross_profit", 0.0)
    gross_loss = abs(_pick_metric(replay, evidence, "gross_loss", _pick_metric(replay, evidence, "gross_loss_abs", 0.0)))
    metrics = {
        "max_drawdown": max_drawdown,
    }
    improvement, scope, tests = _propose_improvement(metrics, risk_failures, rejection_summary, counts)

    total = max(1, counts["trades_closed"])
    return _base_payload(
        allowed=True,
        decision=SELF_IMPROVEMENT_ALLOWED,
        blocked_reason=RejectionReason.NONE,
        blocked_reasons=[RejectionReason.NONE],
        warnings=[],
        replay=replay,
        evidence=evidence,
        evidence_path=evidence_path or "",
        metadata=metadata,
        quality=quality,
        counts=counts,
        risk_failures=risk_failures,
        rejection_summary=rejection_summary,
        rejected_setup_summary={"duplicate_setups": duplicate_setups},
        tests=tests,
        evidence_used={"replay": replay, "evidence_summary": evidence, "supervisor_summary": supervisor},
        recommended_improvement=improvement,
        recommended_improvement_scope=scope,
        win_rate=_to_float(replay.get("win_rate_pct"), 0.0),
        net_pnl=net_pnl,
        max_drawdown=max_drawdown,
        strategy_performance={
            "candidate_total": _to_int(supervisor.get("candidate_count"), 0),
            "selected_total": _to_int(supervisor.get("selected_count"), 0),
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "net_pnl": net_pnl,
        },
        risk_failure_metrics={
            "risk_failures": risk_failures,
            "risk_failure_ratio": risk_failures / total,
            "max_drawdown": max_drawdown,
        },
        winning_summary={
            "wins": counts["wins"],
            "gross_profit": gross_profit,
            "win_ratio": counts["wins"] / total,
        },
        losing_summary={
            "losses": counts["losses"],
            "gross_loss": gross_loss,
            "loss_ratio": counts["losses"] / total,
        },
        protected_action=False,
        approval_required=False,
        approval_reason="",
        no_live_setting_change=False,
    )
