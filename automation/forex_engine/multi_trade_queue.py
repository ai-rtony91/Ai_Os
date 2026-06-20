"""Paper-only multi-trade queue for Forex strategy candidates."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from .order_preview import build_order_preview
from .risk_governor import evaluate_risk_preview

MULTI_TRADE_QUEUE_MODE = "PAPER_ONLY"
MULTI_TRADE_QUEUE_ALLOWED = "allowed"
MULTI_TRADE_QUEUE_BLOCKED = "blocked"

MULTI_TRADE_QUEUE_REJECTION_REASONS = [
    "none",
    "invalid_candidates",
    "non_paper_mode",
    "live_trading_blocked",
    "missing_candidate_id",
    "missing_pair",
    "missing_direction",
    "invalid_score",
    "score_below_threshold",
    "duplicate_setup",
    "max_selected_trades_hit",
    "max_open_trades_hit",
    "max_pair_exposure_hit",
    "session_trade_cap_hit",
    "cooldown_active",
    "risk_governor_blocked",
    "order_preview_blocked",
    "evidence_path_invalid",
]


def _coerce_int(value: Any, default: int) -> int:
    try:
        return max(int(value), 0)
    except Exception:
        return int(default)


def _coerce_float(value: Any, default: float) -> float:
    try:
        return max(float(value), 0.0)
    except Exception:
        return float(default)


def _coerce_limits(limits: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    value = limits if isinstance(limits, Mapping) else {}
    return {
        "min_score": _coerce_float(value.get("min_score", 50.0), 50.0),
        "max_selected_trades": _coerce_int(value.get("max_selected_trades", 3), 3),
        "max_open_trades": _coerce_int(value.get("max_open_trades", 3), 3),
        "max_candidates_per_pair": _coerce_int(value.get("max_candidates_per_pair", 1), 1),
        "max_pair_exposure": _coerce_float(value.get("max_pair_exposure", 0.0), 0.0),
        "session_trade_cap": _coerce_int(value.get("session_trade_cap", 0), 0),
        "cooldown_after_loss_seconds": _coerce_int(value.get("cooldown_after_loss_seconds", 0), 0),
        "duplicate_setup_block": bool(value.get("duplicate_setup_block", True)),
        "require_risk_governor": bool(value.get("require_risk_governor", True)),
        "require_order_preview": bool(value.get("require_order_preview", False)),
    }


def _safe_is_evidence_path_valid(path: Any) -> bool:
    if path is None or path == "":
        return True
    if not isinstance(path, str):
        return False
    if path.startswith("/"):
        return False
    if len(path) >= 3 and path[1:3] == ":\\":
        return False
    return True


def _normalize_pair(pair: Any) -> str:
    if pair is None:
        return ""
    return "".join(str(pair).upper().replace("-", "").replace("_", "").split())


def _normalize_direction(direction: Any) -> str:
    if direction is None:
        return ""
    return str(direction).lower()


def _normalize_mode(mode: Any) -> str:
    return str(mode or MULTI_TRADE_QUEUE_MODE).lower()


def _candidate_score(candidate: Mapping[str, Any]) -> float:
    try:
        return float(candidate.get("score", 0.0))
    except Exception:
        return -1.0


def _is_live_like_mode(mode: str) -> bool:
    return mode in {"live", "demo", "broker", "live_blocked", "trading", "broker_demo"}


def _extract_risk(candidate: Mapping[str, Any]) -> float:
    for key in ("dollar_risk", "risk_dollars", "risk_amount", "risk_amount_usd"):
        if key in candidate:
            try:
                return float(candidate.get(key))
            except Exception:
                return 0.0
    return 0.0


def _is_open_trade(trade: Mapping[str, Any]) -> bool:
    status = str(trade.get("status", "")).lower()
    return status in {"active", "opened", "queued"}


def _is_loss_trade(trade: Mapping[str, Any]) -> bool:
    pnl = trade.get("realized_pnl", trade.get("pnl"))
    reason = str(trade.get("close_reason", "")).lower()
    if isinstance(pnl, (int, float)):
        return pnl < 0
    return reason in {"stop_loss", "manual_close", "expiry", "kill_switch", "error"}


def _trade_time(trade: Mapping[str, Any]) -> Optional[float]:
    value = trade.get("closed_timestamp", trade.get("timestamp", trade.get("data_timestamp")))
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _to_candidate_rows(strategy_result_or_candidates: Any) -> Optional[List[Dict[str, Any]]]:
    rows = []
    if isinstance(strategy_result_or_candidates, Mapping):
        raw = strategy_result_or_candidates.get("candidates", [])
    elif isinstance(strategy_result_or_candidates, Iterable):
        raw = strategy_result_or_candidates
    else:
        return None

    if raw is None:
        return []
    if not isinstance(raw, Iterable):
        return None

    for row in raw:
        if isinstance(row, Mapping):
            normalized = dict(row)
            normalized["pair"] = _normalize_pair(row.get("pair"))
            normalized["direction"] = _normalize_direction(row.get("direction"))
            normalized["mode"] = _normalize_mode(row.get("mode", MULTI_TRADE_QUEUE_MODE))
            if "paper_only" in row and row.get("paper_only") is not None:
                normalized["paper_only"] = bool(row.get("paper_only"))
            else:
                normalized["paper_only"] = True
            rows.append(normalized)
        else:
            rows.append({
                "candidate_id": None,
                "pair": "",
                "direction": "",
                "mode": MULTI_TRADE_QUEUE_MODE,
                "paper_only": True,
                "score": None,
            })
    return rows


def _base_safety_dict() -> Dict[str, Any]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _candidate_rejected(candidate: Mapping[str, Any], limits: Mapping[str, Any]) -> List[str]:
    reasons: List[str] = []
    if not candidate.get("paper_only", True):
        reasons.append("non_paper_mode")
    if _is_live_like_mode(_normalize_mode(candidate.get("mode", MULTI_TRADE_QUEUE_MODE))):
        reasons.append("live_trading_blocked")
    if not candidate.get("candidate_id"):
        reasons.append("missing_candidate_id")
    if not _normalize_pair(candidate.get("pair")):
        reasons.append("missing_pair")
    if _normalize_direction(candidate.get("direction")) not in {"buy", "sell"}:
        reasons.append("missing_direction")
    score = _candidate_score(candidate)
    if score is None:
        reasons.append("invalid_score")
    elif score < 0 or score > 100:
        reasons.append("invalid_score")
    elif score < limits["min_score"]:
        reasons.append("score_below_threshold")
    return reasons


def build_multi_trade_queue(
    strategy_result_or_candidates: Any,
    account_state: Optional[Mapping[str, Any]] = None,
    open_trades: Optional[Iterable[Any]] = None,
    closed_trades: Optional[Iterable[Any]] = None,
    limits: Optional[Mapping[str, Any]] = None,
    market_state: Optional[Mapping[str, Any]] = None,
    now_timestamp: Optional[float] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    normalized_limits = _coerce_limits(limits)

    if not _safe_is_evidence_path_valid(evidence_path):
        return {
            "allowed": False,
            "decision": MULTI_TRADE_QUEUE_BLOCKED,
            "blocked_reason": "evidence_path_invalid",
            "blocked_reasons": ["evidence_path_invalid"],
            "warnings": [],
            "paper_only": True,
            "mode": MULTI_TRADE_QUEUE_MODE,
            "total_candidates": 0,
            "selected_count": 0,
            "rejected_count": 0,
            "selected_candidates": [],
            "rejected_candidates": [],
            "ranked_candidates": [],
            "limits": normalized_limits,
            "risk_evaluations": [],
            "preview_evaluations": [],
            "evidence": {"cause": "invalid_evidence_path"},
            "evidence_path": evidence_path,
            "safety": _base_safety_dict(),
            "next_safe_action": "provide_relative_evidence_path",
            "metadata": dict(metadata or {}),
        }

    candidate_rows = _to_candidate_rows(strategy_result_or_candidates)
    if candidate_rows is None:
        return {
            "allowed": False,
            "decision": MULTI_TRADE_QUEUE_BLOCKED,
            "blocked_reason": "invalid_candidates",
            "blocked_reasons": ["invalid_candidates"],
            "warnings": [],
            "paper_only": True,
            "mode": MULTI_TRADE_QUEUE_MODE,
            "total_candidates": 0,
            "selected_count": 0,
            "rejected_count": 0,
            "selected_candidates": [],
            "rejected_candidates": [],
            "ranked_candidates": [],
            "limits": normalized_limits,
            "risk_evaluations": [],
            "preview_evaluations": [],
            "evidence": {"cause": "invalid_candidates"},
            "evidence_path": evidence_path,
            "safety": _base_safety_dict(),
            "next_safe_action": "provide_candidate_list_or_dict",
            "metadata": dict(metadata or {}),
        }

    source_mode = MULTI_TRADE_QUEUE_MODE
    source_paper_only = True
    if isinstance(strategy_result_or_candidates, Mapping):
        source_mode = _normalize_mode(strategy_result_or_candidates.get("mode", MULTI_TRADE_QUEUE_MODE))
        source_paper_only = strategy_result_or_candidates.get("paper_only", True) is not False

    if not source_paper_only:
        return {
            "allowed": False,
            "decision": MULTI_TRADE_QUEUE_BLOCKED,
            "blocked_reason": "non_paper_mode",
            "blocked_reasons": ["non_paper_mode"],
            "warnings": [],
            "paper_only": False,
            "mode": source_mode,
            "total_candidates": len(candidate_rows),
            "selected_count": 0,
            "rejected_count": 0,
            "selected_candidates": [],
            "rejected_candidates": [],
            "ranked_candidates": [],
            "limits": normalized_limits,
            "risk_evaluations": [],
            "preview_evaluations": [],
            "evidence": {"cause": "strategy_source_not_paper_only"},
            "evidence_path": evidence_path,
            "safety": _base_safety_dict(),
            "next_safe_action": "set_source_to_paper_only",
            "metadata": dict(metadata or {}),
        }

    if _is_live_like_mode(source_mode):
        return {
            "allowed": False,
            "decision": MULTI_TRADE_QUEUE_BLOCKED,
            "blocked_reason": "live_trading_blocked",
            "blocked_reasons": ["live_trading_blocked"],
            "warnings": [],
            "paper_only": True,
            "mode": source_mode,
            "total_candidates": len(candidate_rows),
            "selected_count": 0,
            "rejected_count": 0,
            "selected_candidates": [],
            "rejected_candidates": [],
            "ranked_candidates": [],
            "limits": normalized_limits,
            "risk_evaluations": [],
            "preview_evaluations": [],
            "evidence": {"cause": "source_in_live_mode"},
            "evidence_path": evidence_path,
            "safety": _base_safety_dict(),
            "next_safe_action": "submit_paper_mode_candidates",
                       "metadata": dict(metadata or {}),
        }

    ranked_candidates = sorted(
        candidate_rows,
        key=lambda c: (
            -_candidate_score(c),
            _normalize_pair(c.get("pair", "")),
            _coerce_str(c.get("candidate_id", "")),
        ),
    )

    open_trades_list = list(open_trades or [])
    closed_trades_list = list(closed_trades or [])

    selected_pair_setup: set[tuple[str, str]] = {
        (_normalize_pair(trade.get("pair")), _normalize_direction(trade.get("direction")))
        for trade in open_trades_list
        if isinstance(trade, Mapping) and _is_open_trade(trade)
    }

    selected_by_pair = {
        _normalize_pair(trade.get("pair")): 0
        for trade in open_trades_list
        if isinstance(trade, Mapping) and _is_open_trade(trade)
    }
    pair_exposure = {
        _normalize_pair(trade.get("pair")): 0.0
        for trade in open_trades_list
        if isinstance(trade, Mapping) and _is_open_trade(trade)
    }
    for trade in open_trades_list:
        if not isinstance(trade, Mapping) or not _is_open_trade(trade):
            continue
        pair = _normalize_pair(trade.get("pair"))
        selected_by_pair[pair] = selected_by_pair.get(pair, 0) + 1
        pair_exposure[pair] = pair_exposure.get(pair, 0.0) + _extract_risk(trade)

    open_like_count = sum(
        1 for trade in open_trades_list if isinstance(trade, Mapping) and _is_open_trade(trade)
    )

    cooldown = False
    now_ts = None
    try:
        now_ts = float(now_timestamp) if now_timestamp is not None else None
    except Exception:
        now_ts = None
    if normalized_limits["cooldown_after_loss_seconds"] > 0 and now_ts is not None:
        for closed in closed_trades_list:
            if not isinstance(closed, Mapping) or not _is_loss_trade(closed):
                continue
            closed_ts = _trade_time(closed)
            if closed_ts is None:
                continue
            if 0 <= now_ts - closed_ts < normalized_limits["cooldown_after_loss_seconds"]:
                cooldown = True
                break

    warnings = []
    if cooldown:
        warnings.append("cooldown_active")

    session_cap = normalized_limits["session_trade_cap"]
    session_count = 0
    if session_cap > 0:
        if isinstance(account_state, Mapping):
            try:
                session_count = int(account_state.get("session_count", 0))
            except Exception:
                session_count = 0
            if session_count < 0:
                session_count = 0

    risk_evaluations: List[Dict[str, Any]] = []
    preview_evaluations: List[Dict[str, Any]] = []
    selected: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    for candidate in ranked_candidates:
        candidate_reasons = _candidate_rejected(candidate, normalized_limits)
        pair = _normalize_pair(candidate.get("pair"))
        direction = _normalize_direction(candidate.get("direction"))
        candidate_id = candidate.get("candidate_id")

        if not candidate_reasons and cooldown:
            candidate_reasons.append("cooldown_active")

        risk_eval = None
        if not candidate_reasons and normalized_limits["require_risk_governor"]:
            risk_eval = evaluate_risk_preview(
                candidate,
                account_state=account_state,
                open_trades=open_trades_list,
                closed_trades=closed_trades_list,
                limits=normalized_limits,
                market_state=market_state,
                now_timestamp=now_ts,
            )
            risk_payload = {
                "candidate_id": candidate_id,
                "result": risk_eval,
            }
            risk_evaluations.append(risk_payload)
            if not _safe_bool(risk_eval.get("allowed", False), False):
                candidate_reasons.append("risk_governor_blocked")

        preview_eval = None
        if not candidate_reasons and normalized_limits["require_order_preview"]:
            preview_eval = build_order_preview(
                candidate,
                account_state=account_state,
                limits=normalized_limits,
                market_state=market_state,
                open_trades=open_trades_list,
                closed_trades=closed_trades_list,
                now_timestamp=now_ts,
                evidence_path=None,
                metadata=metadata,
            )
            preview_evaluations.append({"candidate_id": candidate_id, "result": preview_eval})
            if not _safe_bool(preview_eval.get("allowed", False), False):
                candidate_reasons.append("order_preview_blocked")

        if not candidate_reasons:
            if normalized_limits["max_selected_trades"] > 0 and len(selected) >= normalized_limits["max_selected_trades"]:
                candidate_reasons.append("max_selected_trades_hit")
            if normalized_limits["max_open_trades"] > 0 and (open_like_count + len(selected)) >= normalized_limits["max_open_trades"]:
                candidate_reasons.append("max_open_trades_hit")
            if normalized_limits["duplicate_setup_block"] and (pair, direction) in selected_pair_setup:
                candidate_reasons.append("duplicate_setup")
            if normalized_limits["max_candidates_per_pair"] > 0 and selected_by_pair.get(pair, 0) >= normalized_limits["max_candidates_per_pair"]:
                candidate_reasons.append("max_pair_candidate_hit")
            if (
                normalized_limits["max_pair_exposure"] > 0
                and (pair_exposure.get(pair, 0.0) + _extract_risk(candidate)) >= normalized_limits["max_pair_exposure"]
            ):
                candidate_reasons.append("max_pair_exposure_hit")
            if session_cap > 0 and (session_count + len(selected)) >= session_cap:
                candidate_reasons.append("session_trade_cap_hit")

        if candidate_reasons:
            rejected.append(
                {
                    "candidate_id": candidate_id,
                    "pair": pair,
                    "direction": direction,
                    "score": candidate.get("score"),
                    "rejection_reasons": list(dict.fromkeys(candidate_reasons)),
                    "risk_evaluation": risk_eval,
                    "order_preview_result": preview_eval,
                }
            )
            continue

        selected.append(candidate)
        selected_pair_setup.add((pair, direction))
        selected_by_pair[pair] = selected_by_pair.get(pair, 0) + 1
        pair_exposure[pair] = pair_exposure.get(pair, 0.0) + _extract_risk(candidate)

    blocked_reasons = []
    if selected:
        decision = MULTI_TRADE_QUEUE_ALLOWED
        blocked_reason = "none"
        allowed = True
        next_action = "build_order_previews_for_selected"
    else:
        decision = MULTI_TRADE_QUEUE_BLOCKED
        allowed = False
        blocked_reasons = list(dict.fromkeys([reason for item in rejected for reason in item.get("rejection_reasons", [])]))
        blocked_reason = blocked_reasons[0] if blocked_reasons else "invalid_candidates"
        next_action = "resolve_rejection_reasons"

    result = {
        "allowed": allowed,
        "decision": decision,
        "blocked_reason": blocked_reason,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "paper_only": True,
        "mode": MULTI_TRADE_QUEUE_MODE,
        "total_candidates": len(ranked_candidates),
        "selected_count": len(selected),
        "rejected_count": len(rejected),
        "selected_candidates": selected,
        "rejected_candidates": rejected,
        "ranked_candidates": ranked_candidates,
        "limits": normalized_limits,
        "risk_evaluations": risk_evaluations,
        "preview_evaluations": preview_evaluations,
        "evidence": {
            "selected_candidate_ids": [item.get("candidate_id") for item in selected],
            "rejected_candidate_ids": [item.get("candidate_id") for item in rejected],
            "total_candidates": len(ranked_candidates),
            "pair_exposure": pair_exposure,
            "cooldown_active": cooldown,
        },
        "evidence_path": evidence_path,
        "safety": _base_safety_dict(),
        "next_safe_action": next_action,
        "metadata": dict(metadata or {}),
    }
    return result


def _coerce_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _safe_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return bool(default)
