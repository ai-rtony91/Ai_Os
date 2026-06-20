from __future__ import annotations

import re
from dataclasses import dataclass
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

_IMPROVEMENT_OPTIONS = {
    "tighten_spread_cap",
    "add_missing_rejection_regression_test",
    "reduce_risk_multiplier_on_drawdown",
    "improve_stale_data_rejection",
    "improve_no_trade_filter",
    "add_duplicate_setup_block_regression",
    "collect_more_paper_evidence",
}

_SAFE_IMPROVEMENTS = {
    "tighten_spread_cap": "tighten_spread_cap",
    "add_missing_rejection_regression_test": "add_missing_rejection_regression_test",
    "reduce_risk_multiplier_on_drawdown": "reduce_risk_multiplier_on_drawdown",
    "improve_stale_data_rejection": "improve_stale_data_rejection",
    "improve_no_trade_filter": "improve_no_trade_filter",
    "add_duplicate_setup_block_regression": "add_duplicate_setup_block_regression",
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


def _safe_bool(value: Any) -> bool:
    return bool(value)


def _as_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []


def _safe_mode_ok(mode: Any) -> bool:
    if mode is None:
        return True
    if not isinstance(mode, str):
        return False
    return mode == SELF_IMPROVEMENT_MODE


def _is_absolute_like(path: Any) -> bool:
    if not isinstance(path, str) or not path:
        return False
    if path.startswith(("/", "\\")) or ":" in path:
        return True
    if ".." in path:
        return True
    return False


def _metric(value: Any) -> bool:
    return value is not None


def _extract_counts(replay: Optional[Dict[str, Any]]) -> Dict[str, int]:
    if not isinstance(replay, dict):
        return {"trades_closed": 0, "wins": 0, "losses": 0, "breakeven": 0}
    return {
        "trades_closed": _to_int(replay.get("trades_closed"), replay.get("total_closed_trades")),
        "wins": _to_int(replay.get("wins")),
        "losses": _to_int(replay.get("losses")),
        "breakeven": _to_int(replay.get("breakeven")),
    }


def _pick_metric(replay: Dict[str, Any], evidence: Dict[str, Any], key: str, default: float = 0.0) -> float:
    if _metric(replay.get(key)):
        return _to_float(replay.get(key), default)
    if _metric(evidence.get(key)):
        return _to_float(evidence.get(key), default)
    if _metric(evidence.get("metrics", {}).get(key)):
        return _to_float(evidence.get("metrics", {}).get(key), default)
    return default


def _is_duplicate_setup_reason(reason: str) -> bool:
    normalized = reason.strip().lower()
    return normalized in {"duplicate_setup", "duplicate_setups"}


def _aggregate_rejections(evidence: Dict[str, Any], replay: Dict[str, Any], supervisor: Dict[str, Any]) -> tuple:
    rejected_setups = 0
    risk_failures = 0
    rejection_summary: Dict[str, int] = {}
    replay_reason_set: set[str] = set()

    replay_rejections = replay.get("blocked_reasons") or replay.get("rejections") or []
    for item in _as_list(replay_rejections):
        reason = str(item).strip().lower()
        if not reason:
            continue
        rejection_summary[reason] = rejection_summary.get(reason, 0) + 1
        replay_reason_set.add(reason)
        if "risk" in reason.lower():
            risk_failures += 1
        if _is_duplicate_setup_reason(reason):
            rejected_setups += 1

    evidence_rejections = evidence.get("rejected_reasons") or evidence.get("rejection_reasons") or []
    for item in _as_list(evidence_rejections):
        reason = str(item).strip().lower()
        if not reason or reason == "candidate_rejected":
            continue
        if reason in replay_reason_set:
            continue
        rejection_summary[reason] = 1
        if "risk" in reason.lower():
            risk_failures += 1
        if _is_duplicate_setup_reason(reason):
            rejected_setups += 1
        replay_reason_set.add(reason)

    queue_rejections = supervisor.get("rejected_candidates") or supervisor.get("risk_rejections") or []
    for item in _as_list(queue_rejections):
        if isinstance(item, dict):
            reason = str(item.get("reason", item.get("rejected_reason", "")))
        else:
            reason = str(item)
        reason = reason.strip().lower()
        if not reason or reason == "candidate_rejected":
            continue
        if reason in replay_reason_set:
            continue
        rejection_summary[reason] = rejection_summary.get(reason, 0) + 1
        if "risk" in reason.lower():
            risk_failures += 1
        if _is_duplicate_setup_reason(reason):
            rejected_setups += 1
        replay_reason_set.add(reason)

    return rejected_setups, risk_failures, rejection_summary


def _metrics_from_inputs(session_replay: Optional[Dict[str, Any]], evidence: Dict[str, Any], supervisor: Dict[str, Any]) -> Dict[str, float]:
    return {
        "net_pnl": _pick_metric(session_replay, evidence, "net_pnl", 0.0),
        "max_drawdown": abs(_pick_metric(session_replay, evidence, "max_drawdown", 0.0)),
        "max_drawdown_pct": _pick_metric(session_replay, evidence, "max_drawdown_pct", _pick_metric(session_replay, evidence, "max_drawdown_percent", 0.0)),
        "gross_profit": _pick_metric(session_replay, evidence, "gross_profit", 0.0),
        "gross_loss": abs(_pick_metric(session_replay, evidence, "gross_loss", _pick_metric(session_replay, evidence, "gross_loss_abs", 0.0))),
        "win_rate_pct": _pick_metric(session_replay, evidence, "win_rate_pct", 0.0),
        "trades_closed": _pick_metric(session_replay, evidence, "trades_closed", _to_float(supervisor.get("trades_closed"), 0.0)),
        "trade_count_metric": _pick_metric(session_replay, evidence, "trade_count", _to_float(supervisor.get("cycle_summary", {}).get("trades_opened"), 0.0)),
        "session_count": _pick_metric(session_replay, evidence, "session_count", 0.0),
    }


def _evidence_quality(replay: Dict[str, Any], evidence: Dict[str, Any], supervisor: Dict[str, Any], limits: Dict[str, Any]) -> Dict[str, Any]:
    counts = _extract_counts(replay)
    expected = _to_int(limits.get("min_trades"), 10)
    total_trades = counts["trades_closed"]
    if total_trades == 0 and _to_int(replay.get("trades_opened"), 0) > 0:
        total_trades = _to_int(replay.get("trades_opened"), 0)
    total_metrics = (
        total_trades,
        _metric(replay.get("net_pnl")),
        _metric(replay.get("wins")),
        _metric(replay.get("losses")),
    )
    return {
        "sample_ready": total_trades >= expected and all(v is not None for v in total_metrics),
        "total_trades": total_trades,
        "min_trades_required": expected,
        "missing_fields": [
            field
            for field in ("net_pnl", "wins", "losses", "breakeven", "trades_closed")
            if not _metric(replay.get(field))
        ]
        if isinstance(replay, dict)
        else ["session_replay"],
    }


def _propose_safe_improvement(
    metrics: Dict[str, int],
    risk_failures: int,
    rejection_summary: Dict[str, int],
    counts: Dict[str, int],
) -> tuple[str, str, List[str]]:
    if risk_failures >= 3 or metrics["max_drawdown"] > 0:
        return (
            _SAFE_IMPROVEMENTS["reduce_risk_multiplier_on_drawdown"],
            "trade_risk_governance",
            [
                "test_risk_governor_drawdown_reduction",
                "test_max_open_risk_and_session_cap_bounds",
            ],
        )
    if _to_int(rejection_summary.get("stale_data_rejected", 0), 0) > 0:
        return (
            _SAFE_IMPROVEMENTS["improve_stale_data_rejection"],
            "data_guardrails",
            ["test_stale_market_data_rejected_deterministically", "test_invalid_timestamp_blocks"],
        )
    if _to_int(rejection_summary.get("spread_too_high", 0), 0) > 0:
        return (
            _SAFE_IMPROVEMENTS["tighten_spread_cap"],
            "market_data_filters",
            ["test_high_spread_is_rejected", "test_spread_cap_applies_consistently"],
        )
    if counts["losses"] > counts["wins"]:
        return (
            _SAFE_IMPROVEMENTS["improve_no_trade_filter"],
            "strategy_candidate_logic",
            ["test_no_trade_signal_reason_codes", "test_candidate_filter_reduces_false_positives"],
        )
    if _to_int(rejection_summary.get("duplicate_setup", 0), 0) > 0 or _to_int(rejection_summary.get("duplicate_setups", 0), 0) > 0:
        return (
            _SAFE_IMPROVEMENTS["add_duplicate_setup_block_regression"],
            "queue_rules",
            ["test_duplicate_setup_blocked", "test_duplicate_direction_per_pair_block"],
        )
    return (
        _SAFE_IMPROVEMENTS["add_missing_rejection_regression_test"],
        "candidate_quality",
        ["test_rejection_reason_coverage", "test_rejection_reason_determinism"],
    )


def _safe_decision_text(protected: bool, allow: bool, reasons: List[str]) -> str:
    if protected:
        return SELF_IMPROVEMENT_REQUIRES_APPROVAL
    if allow:
        return SELF_IMPROVEMENT_ALLOWED
    return SELF_IMPROVEMENT_BLOCKED


@dataclass
class _ReviewResult:
    allowed: bool
    decision: str
    blocked_reason: str
    blocked_reasons: List[str]
    warnings: List[str]
    paper_only: bool
    mode: str
    evidence_quality: Dict[str, Any]
    total_trades: int
    wins: int
    losses: int
    breakeven: int
    win_rate_pct: float
    net_pnl: float
    max_drawdown: float
    risk_failures: int
    rejection_summary: Dict[str, int]
    winning_trade_summary: Dict[str, Any]
    losing_trade_summary: Dict[str, Any]
    rejected_setup_summary: Dict[str, int]
    strategy_performance_metrics: Dict[str, Any]
    risk_failure_metrics: Dict[str, Any]
    recommended_improvement: str
    recommended_improvement_scope: str
    proposed_regression_tests: List[str]
    protected_action_detected: bool
    approval_required: bool
    approval_reason: str
    no_live_setting_change: bool
    evidence_used: Dict[str, Any]
    evidence_path: str
    safety: Dict[str, Any]
    next_safe_action: str
    metadata: Dict[str, Any]


def _as_dict(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    return {}

def _contains_protected_action(text: Any) -> bool:
    if not isinstance(text, str):
        return False
    normalized = text.lower()
    return any(token in normalized for token in _PROTECTED_PATTERNS)


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
            recommend_collect_more=False,
        )

    if _is_absolute_like(evidence_path):
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
        )

    requested = str(requested_change or "")
    if _contains_protected_action(requested):
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
    rejected_setups, risk_failures, rejection_summary = _aggregate_rejections(evidence, replay, supervisor)
    quality = _evidence_quality(replay, evidence, supervisor, limits)
    evidence_used = {"replay": replay, "evidence_summary": evidence, "supervisor_summary": supervisor}

    total = counts["trades_closed"]
    missing = 0
    required_ok = quality["sample_ready"]
    if not _metric(replay.get("wins")) or not _metric(replay.get("losses")) or not _metric(replay.get("breakeven")):
        missing += 1
    if not _metric(replay.get("net_pnl")):
        missing += 1

    if total <= 0 or not required_ok or missing > 0:
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
            warnings=["insufficient_or_incomplete_session_metrics"],
            recommend_collect_more=True,
            counts=counts,
            quality=quality,
            rejection_summary=rejection_summary,
            risk_failures=risk_failures,
            evidence_used=evidence_used,
        )

    metrics = _metrics_from_inputs(replay, evidence, supervisor)
    win_rate = _to_float(metrics.get("win_rate_pct"), 0.0)
    net_pnl = _to_float(metrics.get("net_pnl"), 0.0)
    max_drawdown = _to_float(metrics.get("max_drawdown"), 0.0)
    gains = _to_float(metrics.get("gross_profit"), 0.0)
    losses = _to_float(metrics.get("gross_loss"), 0.0)

    recommended_improvement, scope, tests = _propose_safe_improvement(
        metrics={"max_drawdown": max_drawdown},
        risk_failures=risk_failures,
        rejection_summary=rejection_summary,
        counts=counts,
    )

    strategy_performance = {
        "candidate_total": _to_int(supervisor.get("candidate_count"), 0),
        "selected_total": _to_int(supervisor.get("selected_count"), 0),
        "gross_profit": gains,
        "gross_loss": losses,
        "net_pnl": net_pnl,
    }
    risk_failure_metrics = {
        "risk_failures": risk_failures,
        "risk_failure_ratio": 0.0 if total == 0 else risk_failures / max(1, total),
        "max_drawdown": max_drawdown,
    }
    winning_summary = {
        "wins": counts["wins"],
        "gross_profit": gains,
        "win_ratio": 0.0 if total == 0 else counts["wins"] / max(1, total),
    }
    losing_summary = {
        "losses": counts["losses"],
        "gross_loss": losses,
        "loss_ratio": 0.0 if total == 0 else counts["losses"] / max(1, total),
    }

    return _build_success(
        replay,
        evidence,
        supervisor,
        evidence_path or "",
        metadata,
        counts=counts,
        quality=quality,
        risk_failures=risk_failures,
        rejection_summary=rejection_summary,
        rejection_setup_summary={"duplicate_setups": rejected_setups},
        strategy_performance=strategy_performance,
        risk_failure_metrics=risk_failure_metrics,
        winning_summary=winning_summary,
        losing_summary=losing_summary,
        recommended_improvement=recommended_improvement,
        recommended_scope=scope,
        tests=tests,
        evidence_used=evidence_used,
        win_rate=win_rate,
        net_pnl=net_pnl,
        max_drawdown=max_drawdown,
    )


def _build_success(
    replay: Dict[str, Any],
    evidence: Dict[str, Any],
    supervisor: Dict[str, Any],
    evidence_path: str,
    metadata: Dict[str, Any],
    counts: Dict[str, int],
    quality: Dict[str, Any],
    risk_failures: int,
    rejection_summary: Dict[str, int],
    strategy_performance: Dict[str, Any],
    risk_failure_metrics: Dict[str, Any],
    winning_summary: Dict[str, Any],
    losing_summary: Dict[str, Any],
    recommended_improvement: str,
    recommended_scope: str,
    tests: List[str],
    evidence_used: Dict[str, Any],
    win_rate: float,
    net_pnl: float,
    max_drawdown: float,
    rejection_setup_summary: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    output = _build_base(
        allowed=True,
        decision=SELF_IMPROVEMENT_ALLOWED,
        blocked_reason=RejectionReason.NONE,
        blocked_reasons=[RejectionReason.NONE],
        warnings=[],
        replay=replay,
        evidence=evidence,
        evidence_path=evidence_path,
        metadata=metadata,
        quality=quality,
        counts=counts,
        risk_failures=risk_failures,
        rejection_summary=rejection_summary,
        tests=tests,
        rejection_setup_summary=rejection_setup_summary,
        evidence_used=evidence_used,
        recommended_improvement=recommended_improvement,
        recommended_scope=recommended_scope,
        win_rate=win_rate,
        net_pnl=net_pnl,
        max_drawdown=max_drawdown,
        strategy_performance=strategy_performance,
        risk_failure_metrics=risk_failure_metrics,
        winning_summary=winning_summary,
        losing_summary=losing_summary,
        supervisor=supervisor,
        protected_action=False,
        approval_required=False,
        approval_reason="",
        no_live_setting_change=False,
    )
    return output


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
    no_live_setting_change: bool = False,
    warnings: Optional[List[str]] = None,
    recommend_collect_more: bool = False,
    counts: Optional[Dict[str, int]] = None,
    quality: Optional[Dict[str, Any]] = None,
    rejection_summary: Optional[Dict[str, int]] = None,
    risk_failures: Optional[int] = None,
    evidence_used: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    counts = counts or {"trades_closed": 0, "wins": 0, "losses": 0, "breakeven": 0}
    quality = quality or _evidence_quality(replay, evidence, supervisor, {"min_trades": 10})
    if recommend_collect_more:
        improvement = "collect_more_paper_evidence"
        scope = "data_collection"
        tests = [
            "test_collect_more_paper_evidence",
            "test_complete_session_replay_payload",
        ]
    else:
        improvement = _SAFE_IMPROVEMENTS["tighten_spread_cap"]
        scope = "paper_safety"
        tests = ["test_safe_fallback_behavior"]

    return _build_base(
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
        risk_failures=risk_failures or 0,
        rejection_summary=rejection_summary or {},
        tests=tests,
        evidence_used=evidence_used or {"replay": replay, "evidence_summary": evidence, "supervisor_summary": supervisor},
        recommended_improvement=improvement,
        recommended_scope=scope,
        win_rate=_to_float(replay.get("win_rate_pct"), 0.0),
        net_pnl=_to_float(replay.get("net_pnl"), 0.0),
        max_drawdown=abs(_to_float(replay.get("max_drawdown"), 0.0)),
        strategy_performance={"candidate_total": 0, "selected_total": 0, "gross_profit": 0.0, "gross_loss": 0.0},
        risk_failure_metrics={"risk_failures": risk_failures or 0, "risk_failure_ratio": 0.0, "max_drawdown": abs(_to_float(replay.get("max_drawdown"), 0.0))},
        winning_summary={"wins": counts["wins"], "gross_profit": 0.0, "win_ratio": 0.0},
        losing_summary={"losses": counts["losses"], "gross_loss": 0.0, "loss_ratio": 0.0},
        supervisor=supervisor,
        protected_action=protected_action,
        approval_required=approval_required,
        approval_reason=approval_reason,
        no_live_setting_change=no_live_setting_change,
    )


def _build_base(
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
    tests: List[str],
    evidence_used: Dict[str, Any],
    recommended_improvement: str,
    recommended_scope: str,
    win_rate: float,
    net_pnl: float,
    max_drawdown: float,
    strategy_performance: Dict[str, Any],
    risk_failure_metrics: Dict[str, Any],
    winning_summary: Dict[str, Any],
    losing_summary: Dict[str, Any],
    supervisor: Dict[str, Any],
    protected_action: bool,
    approval_required: bool,
    approval_reason: str,
    no_live_setting_change: bool = False,
    rejection_setup_summary: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    return {
        "allowed": bool(allowed),
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
        "rejection_summary": dict(rejection_summary),
        "winning_trade_summary": dict(winning_summary),
        "losing_trade_summary": dict(losing_summary),
        "rejected_setup_summary": rejection_setup_summary if rejection_setup_summary is not None else {"duplicate_setups": 0},
        "strategy_performance_metrics": dict(strategy_performance),
        "risk_failure_metrics": dict(risk_failure_metrics),
        "recommended_improvement": recommended_improvement,
        "recommended_improvement_scope": recommended_scope,
        "proposed_regression_tests": list(tests),
        "protected_action_detected": bool(protected_action),
        "approval_required": bool(approval_required),
        "approval_reason": approval_reason,
        "no_live_setting_change": bool(no_live_setting_change),
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
            "Review evidence and apply one bounded paper-safe adjustment."
            if not protected_action and allowed
            else ("Route protected change requests to approval before any live/broker action."
                  if protected_action
                  else "Gather additional paper session evidence and rerun review.")
        ),
        "metadata": metadata,
    }
