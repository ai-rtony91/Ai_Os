"""Paper-only session replay summary from evidence ledger events."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from .evidence_ledger import EVIDENCE_LEDGER_MODE, validate_ledger, replay_ledger

SESSION_REPLAY_MODE = "PAPER_ONLY"
SESSION_REPLAY_ALLOWED = "allowed"
SESSION_REPLAY_BLOCKED = "blocked"

SESSION_REPLAY_REJECTION_REASONS = [
    "none",
    "invalid_ledger",
    "invalid_event",
    "non_paper_mode",
    "live_trading_blocked",
    "missing_session_id",
    "missing_required_event",
    "missing_market_data",
    "missing_candidate_evidence",
    "missing_preview_evidence",
    "missing_risk_evidence",
    "missing_trade_open_evidence",
    "missing_trade_close_evidence",
    "missing_balance_update_evidence",
    "evidence_path_invalid",
]


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


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _to_event_id(value: Any) -> str:
    return "" if value is None else str(value)


def _safe_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return bool(default)


def _zero_safety_dict() -> Dict[str, Any]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _safe_validate_event(event: Mapping[str, Any], required_ids: set[str]) -> List[str]:
    reasons: List[str] = []
    if not isinstance(event, Mapping):
        return ["invalid_event"]
    if event.get("paper_only") is False:
        reasons.append("non_paper_mode")
    mode = str(event.get("mode", "")).lower()
    if mode not in {"", SESSION_REPLAY_MODE}:
        reasons.append("live_trading_blocked")
    if not _to_event_id(event.get("session_id")):
        reasons.append("missing_session_id")
    event_id = _to_event_id(event.get("event_id"))
    if not event_id:
        reasons.append("invalid_event")
    if not isinstance(event.get("payload"), Mapping):
        reasons.append("invalid_event")
    if required_ids is not None and event_id and event_id not in required_ids:
        pass
    return reasons


def _coerce_events(ledger: Optional[Iterable[Any]]) -> Optional[List[Mapping[str, Any]]]:
    if ledger is None:
        return []
    if not isinstance(ledger, Iterable):
        return None
    return [event for event in ledger if isinstance(event, Mapping)]


def build_session_replay(
    ledger: Optional[Iterable[Any]],
    session_id: Optional[str] = None,
    limits: Optional[Mapping[str, Any]] = None,
    evidence_path: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    if not _safe_is_evidence_path_valid(evidence_path):
        return {
            "allowed": False,
            "decision": SESSION_REPLAY_BLOCKED,
            "blocked_reason": "evidence_path_invalid",
            "blocked_reasons": ["evidence_path_invalid"],
            "warnings": [],
            "paper_only": True,
            "mode": SESSION_REPLAY_MODE,
            "session_id": session_id,
            "event_count": 0,
            "counts_by_event_type": {},
            "total_candidates": 0,
            "accepted_candidates": 0,
            "rejected_candidates": 0,
            "previews_created": 0,
            "previews_rejected": 0,
            "risk_accepted": 0,
            "risk_rejected": 0,
            "trades_opened": 0,
            "trades_closed": 0,
            "open_trades": [],
            "closed_trades": [],
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "net_pnl": 0.0,
            "win_rate_pct": 0.0,
            "profit_factor": None,
            "balance_start": None,
            "balance_end": None,
            "balance_change": None,
            "max_drawdown": None,
            "max_drawdown_pct": None,
            "risk_usage": 0.0,
            "rejection_reasons": ["evidence_path_invalid"],
            "missing_evidence_warnings": ["invalid_evidence_path"],
            "source_event_ids": [],
            "replay_summary": {},
            "evidence": {"cause": "invalid_evidence_path"},
            "safety": _zero_safety_dict(),
            "next_safe_action": "use_relative_evidence_path",
            "metadata": dict(metadata or {}),
        }

    events = _coerce_events(ledger)
    if events is None:
        return {
            "allowed": False,
            "decision": SESSION_REPLAY_BLOCKED,
            "blocked_reason": "invalid_ledger",
            "blocked_reasons": ["invalid_ledger"],
            "warnings": [],
            "paper_only": True,
            "mode": SESSION_REPLAY_MODE,
            "session_id": session_id,
            "event_count": 0,
            "counts_by_event_type": {},
            "total_candidates": 0,
            "accepted_candidates": 0,
            "rejected_candidates": 0,
            "previews_created": 0,
            "previews_rejected": 0,
            "risk_accepted": 0,
            "risk_rejected": 0,
            "trades_opened": 0,
            "trades_closed": 0,
            "open_trades": [],
            "closed_trades": [],
            "wins": 0,
            "losses": 0,
            "breakeven": 0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "net_pnl": 0.0,
            "win_rate_pct": 0.0,
            "profit_factor": None,
            "balance_start": None,
            "balance_end": None,
            "balance_change": None,
            "max_drawdown": None,
            "max_drawdown_pct": None,
            "risk_usage": 0.0,
            "rejection_reasons": ["invalid_ledger"],
            "missing_evidence_warnings": ["invalid_ledger"],
            "source_event_ids": [],
            "replay_summary": {},
            "evidence": {"cause": "invalid_ledger"},
            "safety": _zero_safety_dict(),
            "next_safe_action": "provide_valid_ledger",
            "metadata": dict(metadata or {}),
        }

    summary = replay_ledger(events, session_id=session_id)
    # Filter once more for strict deterministic order in output.
    filtered = [event for event in events if session_id is None or event.get("session_id") == session_id]

    warnings: List[str] = []
    reasons: List[str] = []
    missing_evidence: List[str] = []

    if session_id is None and filtered:
        pass

    # Validate session_id
    if session_id is not None and not session_id:
        reasons.append("missing_session_id")
        warnings.append("missing_session_id")

    counts_by_event_type: Dict[str, int] = summary.get("counts_by_event_type", {})

    total_candidates = counts_by_event_type.get("strategy_candidate_created", 0) + counts_by_event_type.get("candidate_rejected", 0)
    accepted_candidates = counts_by_event_type.get("strategy_candidate_created", 0)
    rejected_candidates = counts_by_event_type.get("candidate_rejected", 0)
    previews_created = counts_by_event_type.get("preview_created", 0)
    previews_rejected = counts_by_event_type.get("preview_rejected", 0)
    risk_accepted = counts_by_event_type.get("risk_accepted", 0)
    risk_rejected = counts_by_event_type.get("risk_rejected", 0)

    # Collect ids and relationship maps.
    source_event_ids: List[str] = [e.get("event_id") for e in filtered if isinstance(e, Mapping)]
    event_by_id = {
        _to_event_id(e.get("event_id")): dict(e) for e in filtered if isinstance(e, Mapping) and _to_event_id(e.get("event_id"))
    }
    open_trades: List[Dict[str, Any]] = []
    closed_trades: List[Dict[str, Any]] = []

    for e in filtered:
        if not isinstance(e, Mapping):
            continue
        if e.get("event_type") == "paper_trade_opened":
            open_trades.append(dict(e))
        if e.get("event_type") == "paper_trade_closed":
            closed_trades.append(dict(e))

    open_trade_ids = set()
    for trade in open_trades:
        trade_id = _to_event_id(trade.get("payload", {}).get("trade_id") or trade.get("trade_id"))
        if trade_id:
            open_trade_ids.add(trade_id)

    closed_trade_ids = []
    for trade in closed_trades:
        payload = trade.get("payload", {})
        trade_id = _to_event_id(payload.get("trade_id") or trade.get("trade_id"))
        if trade_id:
            closed_trade_ids.append(trade_id)
            if trade_id not in open_trade_ids:
                missing_evidence.append("missing_trade_open_evidence")

    # missing preview with no candidate
    candidate_ids = set()
    for event in filtered:
        if event.get("event_type") not in {"strategy_candidate_created", "candidate_rejected"}:
            continue
        payload = event.get("payload", {})
        candidate_id = _to_event_id(payload.get("candidate_id"))
        if candidate_id:
            candidate_ids.add(candidate_id)

    for event in filtered:
        if event.get("event_type") not in {"preview_created", "preview_rejected"}:
            continue
        payload = event.get("payload", {})
        candidate_id = _to_event_id(payload.get("candidate_id"))
        if candidate_id and candidate_id not in candidate_ids:
            missing_evidence.append("missing_candidate_evidence")
            break

    # risk without preview/candidate linkage
    preview_ids = set()
    candidate_to_preview = set()
    for event in filtered:
        if event.get("event_type") not in {"preview_created", "preview_rejected"}:
            continue
        payload = event.get("payload", {})
        preview_id = _to_event_id(event.get("event_id"))
        if preview_id:
            preview_ids.add(preview_id)
        if _to_event_id(payload.get("candidate_id")):
            candidate_to_preview.add(_to_event_id(payload.get("candidate_id")))

    for event in filtered:
        if event.get("event_type") not in {"risk_accepted", "risk_rejected"}:
            continue
        payload = event.get("payload", {})
        ref = _to_event_id(payload.get("candidate_id"))
        if ref:
            if ref not in candidate_to_preview:
                missing_evidence.append("missing_risk_evidence")
                break
            if _to_event_id(payload.get("preview_event_id")) and _to_event_id(payload.get("preview_event_id")) not in preview_ids:
                missing_evidence.append("missing_preview_evidence")
                break

    if not filtered:
        reasons.append("missing_required_event")
        warnings.append("missing_required_event")

    market_data_present = counts_by_event_type.get("market_data_accepted", 0) + counts_by_event_type.get("market_data_rejected", 0)
    if market_data_present == 0:
        warnings.append("missing_market_data")
        reasons.append("missing_market_data")

    # P&L
    gross_profit = 0.0
    gross_loss = 0.0
    wins = 0
    losses = 0
    breakeven = 0
    closes = []

    for trade in closed_trades:
        payload = trade.get("payload", {})
        realized = _safe_float(payload.get("realized_pnl", payload.get("pnl", 0.0)))
        closes.append(realized)
        if realized > 0:
            wins += 1
            gross_profit += realized
        elif realized < 0:
            losses += 1
            gross_loss += abs(realized)
        else:
            breakeven += 1

    net_pnl = gross_profit - gross_loss
    settled = wins + losses + breakeven
    win_rate_pct = (wins / settled * 100.0) if settled > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    # balance metrics
    balances = []
    for event in filtered:
        if event.get("event_type") != "balance_updated":
            continue
        payload = event.get("payload", {})
        val = payload.get("current_balance")
        if val is None:
            val = payload.get("balance_after")
        if val is not None:
            balances.append(_safe_float(val))

    balance_start = balances[0] if balances else None
    balance_end = balances[-1] if balances else None
    balance_change = None
    if balance_start is not None and balance_end is not None:
        balance_change = balance_end - balance_start

    max_drawdown = None
    max_drawdown_pct = None
    if balances and len(balances) > 1:
        peak = balances[0]
        max_dd = 0.0
        for value in balances:
            if value > peak:
                peak = value
            dd = peak - value
            if dd > max_dd:
                max_dd = dd
        max_drawdown = max_dd
        if peak > 0:
            max_drawdown_pct = (max_dd / peak) * 100.0

    risk_usage = 0.0
    for event in filtered:
        if event.get("event_type") not in {"risk_accepted", "risk_rejected"}:
            continue
        payload = event.get("payload", {})
        risk = payload.get("dollar_risk", payload.get("risk_dollars", None))
        if risk is not None:
            risk_usage += _safe_float(risk)

    # validate events and detect any direct blocking reasons
    for event in filtered:
        for reason in _safe_validate_event(event, set(event_by_id.keys())):
            if reason not in reasons:
                reasons.append(reason)

    reasons = list(dict.fromkeys(reasons))
    missing_evidence = list(dict.fromkeys(missing_evidence))

    # remove empty reasons duplication
    if reasons:
        blocked_reason = reasons[0]
    else:
        blocked_reason = "none"

    allowed = summary.get("valid", False) and len(missing_evidence) == 0 and not reasons
    decision = SESSION_REPLAY_ALLOWED if allowed else SESSION_REPLAY_BLOCKED

    return {
        "allowed": allowed,
        "decision": decision,
        "blocked_reason": blocked_reason,
        "blocked_reasons": reasons if reasons else [],
        "warnings": warnings,
        "paper_only": True,
        "mode": SESSION_REPLAY_MODE,
        "session_id": session_id,
        "event_count": len(filtered),
        "counts_by_event_type": counts_by_event_type,
        "total_candidates": total_candidates,
        "accepted_candidates": accepted_candidates,
        "rejected_candidates": rejected_candidates,
        "previews_created": previews_created,
        "previews_rejected": previews_rejected,
        "risk_accepted": risk_accepted,
        "risk_rejected": risk_rejected,
        "trades_opened": len(open_trades),
        "trades_closed": len(closed_trades),
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "net_pnl": net_pnl,
        "win_rate_pct": win_rate_pct,
        "profit_factor": profit_factor,
        "balance_start": balance_start,
        "balance_end": balance_end,
        "balance_change": balance_change,
        "max_drawdown": max_drawdown,
        "max_drawdown_pct": max_drawdown_pct,
        "risk_usage": risk_usage,
        "rejection_reasons": reasons if reasons else [],
        "missing_evidence_warnings": missing_evidence,
        "source_event_ids": source_event_ids,
        "replay_summary": summary,
        "evidence": {"session_id": session_id, "source_event_count": len(filtered)},
        "evidence_path": evidence_path,
        "safety": _zero_safety_dict(),
        "next_safe_action": "run_validated_replay" if allowed else "fix_ledger_events",
        "metadata": dict(metadata or {}),
    }
