"""Deterministic forex paper-session supervisor proof."""
from __future__ import annotations

import hashlib
import json
from typing import Any

SESSION_MODE = "PAPER_ONLY"
SESSION_ID = "paper-session-supervisor-v1"
STARTING_BALANCE = 10000.0
MAX_RISK_PERCENT = 2.0
MAX_SPREAD = 0.001


def _candidate_setups() -> list[dict[str, Any]]:
    return [
        {
            "candidate_id": "setup-001",
            "symbol": "EURUSD",
            "direction": "buy",
            "score": 92.0,
            "entry": 1.1000,
            "stop": 1.0950,
            "target": 1.1100,
            "risk_percent": 1.0,
            "spread": 0.0002,
            "close_price": 1.1100,
            "close_reason": "take_profit",
        },
        {
            "candidate_id": "setup-002",
            "symbol": "GBPUSD",
            "direction": "sell",
            "score": 88.0,
            "entry": 1.2500,
            "stop": 1.2550,
            "target": 1.2400,
            "risk_percent": 1.0,
            "spread": 0.0003,
            "close_price": 1.2550,
            "close_reason": "stop_loss",
        },
        {
            "candidate_id": "setup-003",
            "symbol": "USDJPY",
            "direction": "buy",
            "score": 84.0,
            "entry": 150.00,
            "stop": 149.50,
            "target": 150.40,
            "risk_percent": 1.0,
            "spread": 0.03,
            "close_price": 150.40,
            "close_reason": "take_profit",
            "max_spread": 0.05,
        },
        {
            "candidate_id": "setup-004",
            "symbol": "AUDUSD",
            "direction": "buy",
            "score": 79.0,
            "entry": 0.6700,
            "stop": 0.6650,
            "target": 0.6800,
            "risk_percent": 1.0,
            "spread": 0.0040,
            "close_price": 0.6800,
            "close_reason": "blocked",
        },
        {
            "candidate_id": "setup-005",
            "symbol": "EURUSD",
            "direction": "sell",
            "score": 73.0,
            "entry": 1.1010,
            "stop": 1.1060,
            "target": 1.0910,
            "risk_percent": 4.0,
            "spread": 0.0002,
            "close_price": 1.0910,
            "close_reason": "blocked",
        },
    ]


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _risk_rejection(candidate: dict[str, Any]) -> str | None:
    if candidate.get("stop") in {None, candidate.get("entry")}:
        return "stop_required"
    max_spread = float(candidate.get("max_spread", MAX_SPREAD))
    if float(candidate["spread"]) > max_spread:
        return "spread_too_high"
    if float(candidate["risk_percent"]) > MAX_RISK_PERCENT:
        return "risk_percent_too_high"
    return None


def _risk_reward(candidate: dict[str, Any]) -> float:
    reward = abs(float(candidate["target"]) - float(candidate["entry"]))
    risk = abs(float(candidate["entry"]) - float(candidate["stop"]))
    if risk <= 0:
        return 0.0
    return round(reward / risk, 6)


def _size_position(candidate: dict[str, Any], balance: float) -> dict[str, float]:
    risk_dollars = round(balance * float(candidate["risk_percent"]) / 100.0, 8)
    stop_distance = round(abs(float(candidate["entry"]) - float(candidate["stop"])), 8)
    units = round(risk_dollars / stop_distance, 8) if stop_distance > 0 else 0.0
    return {
        "risk_dollars": risk_dollars,
        "risk_percent": float(candidate["risk_percent"]),
        "stop_distance": stop_distance,
        "units": units,
    }


def _realized_pl(trade: dict[str, Any]) -> float:
    entry = float(trade["entry"])
    exit_price = float(trade["exit"])
    units = float(trade["units"])
    if trade["direction"] == "buy":
        return round((exit_price - entry) * units, 8)
    return round((entry - exit_price) * units, 8)


def _new_event(events: list[dict[str, Any]], event_type: str, payload: dict[str, Any]) -> None:
    event = {
        "event_id": f"evt-{len(events) + 1:04d}",
        "event_type": event_type,
        "payload": dict(payload),
        "paper_only": True,
    }
    events.append(event)


def _replay(events: list[dict[str, Any]], starting_balance: float, ending_balance: float, realized_pl: float) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for event in events:
        event_type = str(event.get("event_type"))
        counts[event_type] = counts.get(event_type, 0) + 1

    wins = [
        event for event in events
        if event["event_type"] == "trade_closed" and float(event["payload"].get("realized_pl", 0.0)) > 0
    ]
    losses = [
        event for event in events
        if event["event_type"] == "trade_closed" and float(event["payload"].get("realized_pl", 0.0)) < 0
    ]
    return {
        "event_count": len(events),
        "counts_by_event_type": counts,
        "candidate_events": counts.get("candidate_created", 0),
        "rejection_events": counts.get("risk_rejected", 0),
        "approval_events": counts.get("risk_approved", 0),
        "execution_events": counts.get("paper_trade_opened", 0),
        "lifecycle_events": counts.get("trade_closed", 0),
        "balance_events": counts.get("balance_updated", 0),
        "accepted_trades": counts.get("risk_approved", 0),
        "rejected_trades": counts.get("risk_rejected", 0),
        "win_count": len(wins),
        "loss_count": len(losses),
        "starting_balance": starting_balance,
        "ending_balance": ending_balance,
        "balance_delta": round(ending_balance - starting_balance, 8),
        "realized_pl": realized_pl,
        "drawdown": round(max(0.0, starting_balance - ending_balance), 8),
    }


def run_paper_session_supervisor() -> dict[str, Any]:
    """Run one deterministic local paper session from candidates to replay."""
    starting_balance = STARTING_BALANCE
    current_balance = STARTING_BALANCE
    candidates = _candidate_setups()
    events: list[dict[str, Any]] = []
    watchlist: list[dict[str, Any]] = []
    approved_trades: list[dict[str, Any]] = []
    closed_trades: list[dict[str, Any]] = []
    risk_rejections: list[dict[str, str]] = []

    for candidate in candidates:
        _new_event(events, "candidate_created", {"candidate_id": candidate["candidate_id"], "symbol": candidate["symbol"]})
        rejection = _risk_rejection(candidate)
        row = {
            "symbol": candidate["symbol"],
            "direction": candidate["direction"],
            "score": candidate["score"],
            "entry": candidate["entry"],
            "stop": candidate["stop"],
            "target": candidate["target"],
            "spread": candidate["spread"],
            "risk_reward": _risk_reward(candidate),
            "status": "blocked" if rejection else "selected",
            "reason_selected": "risk_approved" if rejection is None else "",
            "reason_blocked": rejection or "",
        }
        watchlist.append(row)

        if rejection:
            rejected = {"candidate_id": candidate["candidate_id"], "reason": rejection}
            risk_rejections.append(rejected)
            _new_event(events, "risk_rejected", rejected)
            continue

        sizing = _size_position(candidate, starting_balance)
        trade_id = _stable_id("paper-trade", {"candidate_id": candidate["candidate_id"], "session_id": SESSION_ID})
        preview = {
            "trade_id": trade_id,
            "candidate_id": candidate["candidate_id"],
            "symbol": candidate["symbol"],
            "direction": candidate["direction"],
            "entry": candidate["entry"],
            "stop": candidate["stop"],
            "target": candidate["target"],
            **sizing,
            "status": "previewed",
        }
        _new_event(events, "risk_approved", {"candidate_id": candidate["candidate_id"], "trade_id": trade_id})
        _new_event(events, "position_sized", {"trade_id": trade_id, "units": sizing["units"], "risk_dollars": sizing["risk_dollars"]})
        opened = {**preview, "status": "active", "open_price": candidate["entry"]}
        approved_trades.append(opened)
        _new_event(events, "paper_trade_opened", {"trade_id": trade_id, "symbol": candidate["symbol"], "units": sizing["units"]})

        closed = {
            **opened,
            "status": "closed",
            "exit": candidate["close_price"],
            "close_reason": candidate["close_reason"],
        }
        closed["realized_pl"] = _realized_pl(closed)
        closed_trades.append(closed)
        current_balance = round(current_balance + closed["realized_pl"], 8)
        _new_event(events, "trade_closed", {"trade_id": trade_id, "close_reason": closed["close_reason"], "realized_pl": closed["realized_pl"]})
        _new_event(events, "balance_updated", {"trade_id": trade_id, "current_balance": current_balance, "realized_pl": closed["realized_pl"]})

    realized_pl = round(sum(float(trade["realized_pl"]) for trade in closed_trades), 8)
    ending_balance = round(starting_balance + realized_pl, 8)
    win_count = sum(1 for trade in closed_trades if float(trade["realized_pl"]) > 0)
    loss_count = sum(1 for trade in closed_trades if float(trade["realized_pl"]) < 0)
    total_risk = round(sum(float(trade["risk_dollars"]) for trade in approved_trades), 8)
    replay = _replay(events, starting_balance, ending_balance, realized_pl)

    return {
        "session_id": SESSION_ID,
        "mode": SESSION_MODE,
        "starting_balance": starting_balance,
        "ending_balance": ending_balance,
        "realized_pl": realized_pl,
        "win_count": win_count,
        "loss_count": loss_count,
        "candidate_count": len(candidates),
        "approved_trade_count": len(approved_trades),
        "rejected_trade_count": len(risk_rejections),
        "open_trade_count": 0,
        "closed_trade_count": len(closed_trades),
        "drawdown": replay["drawdown"],
        "risk_utilization": round(total_risk / starting_balance, 8),
        "risk_rejections": risk_rejections,
        "events": events,
        "watchlist": watchlist,
        "approved_trades": approved_trades,
        "closed_trades": closed_trades,
        "replay": replay,
        "safety": {
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_order_placed": False,
            "paper_only": True,
        },
    }

