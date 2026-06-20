"""Deterministic long-run paper supervisor using local fixtures only."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from automation.forex_engine.paper_account_state import apply_closed_trade_to_account, create_paper_account_state
from automation.forex_engine.paper_evidence_ledger import append_event, create_ledger
from automation.forex_engine.paper_position_sizing import calculate_paper_position_size
from automation.forex_engine.paper_risk_governor import evaluate_paper_trade_risk
from automation.forex_engine.paper_session_replay import build_paper_session_replay
from automation.forex_engine.paper_trade_lifecycle import close_paper_trade, create_paper_trade, open_paper_trade

SESSION_ID = "paper-long-run-supervisor-v2"


def _stable_id(prefix: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return f"{prefix}-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]}"


def _cycle_candidates() -> list[list[dict[str, Any]]]:
    return [
        [
            {"candidate_id": "c1-eur-buy", "symbol": "EURUSD", "direction": "buy", "entry": 1.1000, "stop": 1.0950, "target": 1.1100, "risk_percent": 1.0, "spread": 0.0002, "close_price": 1.1100},
            {"candidate_id": "c1-gbp-sell", "symbol": "GBPUSD", "direction": "sell", "entry": 1.2500, "stop": 1.2550, "target": 1.2400, "risk_percent": 1.0, "spread": 0.0003, "close_price": 1.2550},
            {"candidate_id": "c1-aud-buy", "symbol": "AUDUSD", "direction": "buy", "entry": 0.6700, "stop": 0.6650, "target": 0.6800, "risk_percent": 1.0, "spread": 0.0040, "close_price": 0.6800},
        ],
        [
            {"candidate_id": "c2-usd-buy", "symbol": "USDJPY", "direction": "buy", "entry": 150.0, "stop": 149.5, "target": 150.4, "risk_percent": 1.0, "spread": 0.03, "max_spread": 0.05, "close_price": 150.4},
            {"candidate_id": "c2-eur-sell", "symbol": "EURUSD", "direction": "sell", "entry": 1.1010, "stop": 1.1060, "target": 1.0910, "risk_percent": 4.0, "spread": 0.0002, "close_price": 1.0910},
            {"candidate_id": "c2-cad-buy", "symbol": "USDCAD", "direction": "buy", "entry": 1.3300, "stop": 1.3300, "target": 1.3400, "risk_percent": 1.0, "spread": 0.0002, "close_price": 1.3400},
        ],
        [
            {"candidate_id": "c3-nzd-buy", "symbol": "NZDUSD", "direction": "buy", "entry": 0.6100, "stop": 0.6050, "target": 0.6200, "risk_percent": 1.0, "spread": 0.0002, "close_price": 0.6200},
            {"candidate_id": "c3-chf-sell", "symbol": "USDCHF", "direction": "sell", "entry": 0.9000, "stop": 0.9050, "target": 0.8900, "risk_percent": 3.0, "spread": 0.0002, "close_price": 0.8900},
            {"candidate_id": "c3-eur-dup", "symbol": "EURUSD", "direction": "buy", "entry": 1.1050, "stop": 1.1000, "target": 1.1150, "risk_percent": 1.0, "spread": 0.0002, "close_price": 1.1150},
        ],
    ]


def run_long_run_paper_supervisor() -> dict[str, Any]:
    """Run deterministic multi-cycle paper sessions and aggregate replay evidence."""
    account = create_paper_account_state(session_count=3)
    ledger = create_ledger(SESSION_ID)
    cycle_replays: list[dict[str, Any]] = []
    approved: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    closed: list[dict[str, Any]] = []
    blocked_symbols = {"EURUSD"}

    for cycle_index, candidates in enumerate(_cycle_candidates(), start=1):
        cycle_start_event_count = len(ledger["events"])
        for candidate in candidates:
            ledger = append_event(ledger, "candidate_created", {"candidate_id": candidate["candidate_id"], "cycle": cycle_index})
            limits = {"max_spread": candidate.get("max_spread", 0.001), "max_risk_percent": 2.0, "max_open_trades": 4}
            duplicate_open = [{"symbol": "EURUSD", "status": "active"}] if candidate["candidate_id"] == "c3-eur-dup" else []
            risk = evaluate_paper_trade_risk(candidate, account, duplicate_open, limits)
            if not risk["risk_passed"]:
                reason = risk["rejection_reasons"][0]
                rejected.append({"candidate_id": candidate["candidate_id"], "reason": reason})
                ledger = append_event(ledger, "risk_rejected", {"candidate_id": candidate["candidate_id"], "reason": reason})
                continue
            sizing = calculate_paper_position_size(
                account["current_balance"],
                candidate["risk_percent"],
                candidate["entry"],
                candidate["stop"],
                max_units=100000.0,
            )
            if not sizing["sizing_passed"]:
                reason = sizing["rejection_reasons"][0]
                rejected.append({"candidate_id": candidate["candidate_id"], "reason": reason})
                ledger = append_event(ledger, "risk_rejected", {"candidate_id": candidate["candidate_id"], "reason": reason})
                continue
            trade_id = _stable_id("paper-trade", {"session_id": SESSION_ID, "candidate_id": candidate["candidate_id"]})
            trade = create_paper_trade(
                trade_id=trade_id,
                symbol=candidate["symbol"],
                direction=candidate["direction"],
                entry=candidate["entry"],
                stop=candidate["stop"],
                target=candidate["target"],
                units=sizing["units"],
                risk_dollars=sizing["risk_dollars"],
                risk_percent=candidate["risk_percent"],
            )
            ledger = append_event(ledger, "risk_approved", {"candidate_id": candidate["candidate_id"], "trade_id": trade_id})
            ledger = append_event(ledger, "sizing_created", {"trade_id": trade_id, "units": sizing["units"], "risk_dollars": sizing["risk_dollars"]})
            opened = open_paper_trade(trade)
            approved.append(opened)
            ledger = append_event(ledger, "paper_trade_opened", {"trade_id": trade_id, "symbol": candidate["symbol"], "units": sizing["units"]})
            reason = "take_profit" if candidate["close_price"] == candidate["target"] else "stop_loss"
            closed_trade = close_paper_trade(opened, candidate["close_price"], reason)
            closed.append(closed_trade)
            account = apply_closed_trade_to_account(account, closed_trade)
            ledger = append_event(ledger, "paper_trade_closed", {"trade_id": trade_id, "realized_pl": closed_trade["realized_pl"], "close_reason": closed_trade["close_reason"]})
            ledger = append_event(ledger, "balance_updated", {"trade_id": trade_id, "current_balance": account["current_balance"], "realized_pl": closed_trade["realized_pl"]})
        cycle_events = ledger["events"][cycle_start_event_count:]
        cycle_replays.append(build_paper_session_replay(cycle_events, starting_balance=0.0, ending_balance=None))

    final_replay = build_paper_session_replay(ledger, starting_balance=10000.0, ending_balance=account["current_balance"])
    return {
        "session_id": SESSION_ID,
        "mode": "PAPER_ONLY",
        "cycles": 3,
        "starting_balance": 10000.0,
        "ending_balance": account["current_balance"],
        "realized_pl": account["realized_pl"],
        "candidate_count": final_replay["candidate_count"],
        "approved_trade_count": len(approved),
        "rejected_trade_count": len(rejected),
        "closed_trade_count": len(closed),
        "win_count": final_replay["win_count"],
        "loss_count": final_replay["loss_count"],
        "approved_trades": approved,
        "rejected_candidates": rejected,
        "closed_trades": closed,
        "ledger": ledger,
        "cycle_replays": cycle_replays,
        "aggregate_replay": final_replay,
        "account_state": account,
        "safety": {
            "broker_request_sent": False,
            "network_used": False,
            "credentials_used": False,
            "live_order_placed": False,
            "paper_only": True,
        },
    }
