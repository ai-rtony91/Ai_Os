"""Deterministic paper-session sample generator for promotion workflow tests."""
from __future__ import annotations

from typing import Any, Mapping

from automation.forex_engine.paper_account_state import apply_closed_trade_to_account, create_paper_account_state
from automation.forex_engine.paper_evidence_ledger import append_event, create_ledger, reconstruct_session_from_events
from automation.forex_engine.paper_position_sizing import calculate_paper_position_size
from automation.forex_engine.paper_risk_governor import evaluate_paper_trade_risk
from automation.forex_engine.paper_session_replay import build_paper_session_replay
from automation.forex_engine.paper_to_demo_promotion_workflow import run_paper_to_demo_promotion_workflow
from automation.forex_engine.paper_trade_lifecycle import close_paper_trade, create_paper_trade, open_paper_trade

MODE = "PAPER_SESSION_SAMPLE_GENERATION_ONLY"
DEFAULT_TIMESTAMP = "2026-01-01T00:00:00Z"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "sample_generation_only": True,
        "broker_access": False,
        "network_api_access": False,
        "credentials_access": False,
        "demo_execution_active": False,
        "live_execution_active": False,
        "capital_allocation_modified": False,
        "orders_submitted": False,
        "real_orders": False,
    }


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return round(float(value), 8)
    except (TypeError, ValueError):
        return default


def _normalize_sample(item: Any, index: int) -> dict[str, Any]:
    if isinstance(item, Mapping):
        source = dict(item)
        pnl = _as_float(source.get("realized_pl", source.get("pnl", source.get("pnl_usd", 0.0))))
    else:
        source = {}
        pnl = _as_float(item)
    return {
        "trade_id": str(source.get("trade_id", f"sample-trade-{index:04d}")),
        "symbol": str(source.get("symbol", "EURUSD")),
        "direction": str(source.get("direction", "buy")).lower(),
        "entry": _as_float(source.get("entry", 1.1)),
        "stop": _as_float(source.get("stop", 1.09)),
        "target": _as_float(source.get("target", 1.12)),
        "risk_percent": _as_float(source.get("risk_percent", 1.0)),
        "spread": _as_float(source.get("spread", 0.0001)),
        "realized_pl": pnl,
        "timestamp": str(source.get("timestamp", DEFAULT_TIMESTAMP)),
    }


def _exit_price_for_pnl(trade: Mapping[str, Any], pnl: float) -> float:
    units = float(trade.get("units", 0.0))
    entry = float(trade.get("entry", 0.0))
    if units <= 0:
        return entry
    price_delta = round(float(pnl) / units, 8)
    if trade.get("direction") == "sell":
        return round(entry - price_delta, 8)
    return round(entry + price_delta, 8)


def _close_reason(realized_pl: float) -> str:
    if realized_pl > 0:
        return "take_profit"
    if realized_pl < 0:
        return "stop_loss"
    return "manual_close"


def _closed_trade_payload(closed_trade: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "trade_id": closed_trade.get("trade_id", ""),
        "symbol": closed_trade.get("symbol", ""),
        "direction": closed_trade.get("direction", ""),
        "entry": closed_trade.get("entry", 0.0),
        "exit": closed_trade.get("exit", closed_trade.get("entry", 0.0)),
        "realized_pl": closed_trade.get("realized_pl", 0.0),
        "risk_dollars": closed_trade.get("risk_dollars", 0.0),
        "risk_percent": closed_trade.get("risk_percent", 0.0),
        "units": closed_trade.get("units", 0.0),
        "close_reason": closed_trade.get("close_reason", "manual_close"),
        "paper_only": True,
    }


def generate_paper_session_sample(
    sample_trades: list[Any] | None = None,
    *,
    session_id: str = "paper-session-sample-v1",
    starting_balance: float = 10000.0,
    evaluator_limits: Mapping[str, Any] | None = None,
    promotion_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate deterministic paper-session evidence and run promotion review."""
    samples = [_normalize_sample(item, index) for index, item in enumerate(list(sample_trades or []), start=1)]
    account = create_paper_account_state(starting_balance=starting_balance, session_count=1)
    ledger = create_ledger(session_id)
    balance_history = [round(float(starting_balance), 8)]
    closed_trades: list[dict[str, Any]] = []
    blocked_reasons: list[str] = []

    for index, sample in enumerate(samples, start=1):
        candidate = {
            "symbol": sample["symbol"],
            "entry": sample["entry"],
            "stop": sample["stop"],
            "target": sample["target"],
            "risk_percent": sample["risk_percent"],
            "spread": sample["spread"],
        }
        ledger = append_event(ledger, "candidate_created", {"trade_id": sample["trade_id"], **candidate}, sample["timestamp"])

        risk_result = evaluate_paper_trade_risk(
            candidate,
            account_state=account,
            open_trades=[],
            limits={"max_daily_loss": 1_000_000.0},
        )
        if not risk_result["risk_passed"]:
            blocked_reasons.extend(str(reason) for reason in risk_result["rejection_reasons"])
            ledger = append_event(
                ledger,
                "risk_rejected",
                {"trade_id": sample["trade_id"], "rejection_reasons": list(risk_result["rejection_reasons"])},
                sample["timestamp"],
            )
            continue

        ledger = append_event(ledger, "risk_approved", {"trade_id": sample["trade_id"], "risk_used": risk_result["risk_used"]}, sample["timestamp"])
        sizing = calculate_paper_position_size(
            balance=float(account["current_balance"]),
            risk_percent=sample["risk_percent"],
            entry=sample["entry"],
            stop=sample["stop"],
        )
        if not sizing["sizing_passed"]:
            blocked_reasons.extend(str(reason) for reason in sizing["rejection_reasons"])
            ledger = append_event(
                ledger,
                "candidate_rejected",
                {"trade_id": sample["trade_id"], "rejection_reasons": list(sizing["rejection_reasons"])},
                sample["timestamp"],
            )
            continue

        ledger = append_event(ledger, "sizing_created", {"trade_id": sample["trade_id"], **sizing}, sample["timestamp"])
        trade = create_paper_trade(
            trade_id=sample["trade_id"],
            symbol=sample["symbol"],
            direction=sample["direction"],
            entry=sample["entry"],
            stop=sample["stop"],
            target=sample["target"],
            units=sizing["units"],
            risk_dollars=sizing["risk_dollars"],
            risk_percent=sample["risk_percent"],
            timestamp=sample["timestamp"],
        )
        opened = open_paper_trade(trade, sample["timestamp"])
        ledger = append_event(ledger, "paper_trade_opened", {"trade_id": sample["trade_id"], **opened}, sample["timestamp"])
        closed = close_paper_trade(
            opened,
            _exit_price_for_pnl(opened, sample["realized_pl"]),
            _close_reason(sample["realized_pl"]),
            sample["timestamp"],
        )
        closed["realized_pl"] = sample["realized_pl"]
        payload = _closed_trade_payload(closed)
        closed_trades.append(payload)
        ledger = append_event(ledger, "paper_trade_closed", payload, sample["timestamp"])
        account = apply_closed_trade_to_account(account, payload, timestamp=sample["timestamp"])
        balance_history.append(round(float(account["current_balance"]), 8))
        ledger = append_event(
            ledger,
            "balance_updated",
            {
                "trade_id": sample["trade_id"],
                "current_balance": account["current_balance"],
                "equity": account["equity"],
                "drawdown": account["drawdown"],
            },
            sample["timestamp"],
        )

    replay_evidence = build_paper_session_replay(ledger, starting_balance, account["current_balance"])
    replay_evidence = {
        **replay_evidence,
        "session_id": session_id,
        "closed_trades": closed_trades,
        "balance_history": balance_history,
        "paper_only": True,
    }
    session_metrics = reconstruct_session_from_events(ledger)
    workflow_result = run_paper_to_demo_promotion_workflow(
        paper_trade_ledger=ledger,
        replay_evidence=replay_evidence,
        session_metrics=session_metrics,
        balance_history=balance_history,
        evaluator_limits=evaluator_limits,
        promotion_limits=promotion_limits,
    )
    return {
        "sample_generated": True,
        "session_id": session_id,
        "paper_trade_ledger": ledger,
        "replay_evidence": replay_evidence,
        "session_metrics": session_metrics,
        "balance_history": balance_history,
        "closed_trades": closed_trades,
        "profitability_result": workflow_result["profitability_result"],
        "promotion_result": workflow_result["promotion_result"],
        "workflow_result": workflow_result,
        "promotion_status": workflow_result["promotion_status"],
        "demo_candidate": workflow_result["demo_candidate"],
        "blocked_reasons": workflow_result["blocked_reasons"] + [reason for reason in blocked_reasons if reason not in workflow_result["blocked_reasons"]],
        "next_safe_action": workflow_result["next_safe_action"],
        "safety": _safety(),
        "mode": MODE,
    }
