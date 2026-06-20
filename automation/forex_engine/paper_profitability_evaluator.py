"""Paper-only profitability evaluator for measured forex edge evidence."""
from __future__ import annotations

import math
from typing import Any, Iterable, Mapping

MODE = "PAPER_PROFITABILITY_EVALUATION_ONLY"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError):
        return default
    return result


def _raw_event_items(paper_trade_ledger: Any) -> tuple[list[Any], bool]:
    if isinstance(paper_trade_ledger, Mapping):
        events = paper_trade_ledger.get("events", [])
    else:
        events = paper_trade_ledger
    if not isinstance(events, Iterable) or isinstance(events, (str, bytes)):
        return [], False
    return list(events), True


def _as_events(paper_trade_ledger: Any) -> list[Mapping[str, Any]]:
    raw_events, valid_container = _raw_event_items(paper_trade_ledger)
    if not valid_container:
        return []
    return [event for event in raw_events if isinstance(event, Mapping)]


def _first_present(payload: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def _finite_float(value: Any) -> tuple[float, bool]:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0, False
    if not math.isfinite(result):
        return 0.0, False
    return result, True


def _append_once(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _trades_match(left: list[dict[str, float]], right: list[dict[str, float]]) -> bool:
    if len(left) != len(right):
        return False
    for left_trade, right_trade in zip(left, right):
        if left_trade["pnl"] != right_trade["pnl"] or left_trade["risk"] != right_trade["risk"]:
            return False
    return True


def _replay_balance_is_consistent(replay_evidence: Any, replay_trades: list[dict[str, float]]) -> bool:
    if not isinstance(replay_evidence, Mapping):
        return True
    if "ending_balance" not in replay_evidence:
        return True
    starting_balance = _first_present(replay_evidence, ("starting_balance", "balance_start"))
    ending_balance = replay_evidence.get("ending_balance")
    starting, starting_valid = _finite_float(starting_balance)
    ending, ending_valid = _finite_float(ending_balance)
    if not starting_valid or not ending_valid:
        return False
    expected = round(starting + sum(trade["pnl"] for trade in replay_trades), 8)
    return round(ending, 8) == expected


def _event_payload(event: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = event.get("payload", {})
    return payload if isinstance(payload, Mapping) else {}


def _closed_trade_from_payload(payload: Mapping[str, Any]) -> tuple[dict[str, float] | None, bool]:
    pnl_raw = _first_present(payload, ("realized_pl", "realized_pnl", "pnl_usd", "pnl"))
    risk_raw = _first_present(payload, ("risk_dollars", "dollar_risk", "risk"))
    pnl, pnl_valid = _finite_float(pnl_raw)
    risk, risk_valid = _finite_float(risk_raw)
    if not pnl_valid or not risk_valid or risk <= 0:
        return None, False
    return {"pnl": round(pnl, 8), "risk": round(risk, 8)}, True


def _trades_from_ledger(paper_trade_ledger: Any) -> tuple[list[dict[str, float]], list[str]]:
    trades: list[dict[str, float]] = []
    reasons: list[str] = []
    raw_events, valid_container = _raw_event_items(paper_trade_ledger)
    if not valid_container:
        if paper_trade_ledger is not None:
            reasons.append("invalid_ledger_evidence")
        return trades, reasons
    for raw_event in raw_events:
        if not isinstance(raw_event, Mapping):
            _append_once(reasons, "invalid_ledger_evidence")
            continue
        event = raw_event
        event_type = str(event.get("event_type", ""))
        if event_type in {"paper_trade_closed", "trade_closed", "position_closed"}:
            trade, valid = _closed_trade_from_payload(_event_payload(event))
            if valid and trade is not None:
                trades.append(trade)
            else:
                _append_once(reasons, "invalid_ledger_evidence")
    return trades, reasons


def _trades_from_replay(replay_evidence: Any) -> tuple[list[dict[str, float]], list[str]]:
    reasons: list[str] = []
    if not isinstance(replay_evidence, Mapping):
        if replay_evidence is not None:
            reasons.append("invalid_replay_evidence")
        return [], reasons
    closed = replay_evidence.get("closed_trades", [])
    if not isinstance(closed, Iterable) or isinstance(closed, (str, bytes)):
        return [], ["invalid_replay_evidence"]
    trades: list[dict[str, float]] = []
    for item in closed:
        if isinstance(item, Mapping):
            trade, valid = _closed_trade_from_payload(item)
            if valid and trade is not None:
                trades.append(trade)
            else:
                _append_once(reasons, "invalid_replay_evidence")
        else:
            _append_once(reasons, "invalid_replay_evidence")
    if not _replay_balance_is_consistent(replay_evidence, trades):
        _append_once(reasons, "inconsistent_replay_evidence")
    return trades, reasons


def _extract_closed_trades(
    paper_trade_ledger: Any,
    replay_evidence: Any,
    session_metrics: Any,
) -> list[dict[str, float]]:
    ledger_trades, _ledger_reasons = _trades_from_ledger(paper_trade_ledger)
    if ledger_trades:
        return ledger_trades
    replay_trades, _replay_reasons = _trades_from_replay(replay_evidence)
    if replay_trades:
        return replay_trades
    if isinstance(session_metrics, Mapping):
        metric_trades = session_metrics.get("closed_trades", [])
        if isinstance(metric_trades, Iterable) and not isinstance(metric_trades, (str, bytes)):
            trades: list[dict[str, float]] = []
            for item in metric_trades:
                if isinstance(item, Mapping):
                    trade, valid = _closed_trade_from_payload(item)
                    if valid and trade is not None:
                        trades.append(trade)
            return trades
    return []


def _balance_values(
    balance_history: Any,
    starting_balance: float,
    trades: list[dict[str, float]],
) -> tuple[list[float], list[str]]:
    if isinstance(balance_history, Iterable) and not isinstance(balance_history, (str, bytes, Mapping)):
        values: list[float] = []
        for item in balance_history:
            if isinstance(item, Mapping):
                raw = item.get("equity", item.get("current_balance", item.get("balance")))
                value, valid = _finite_float(raw)
            else:
                value, valid = _finite_float(item)
            if not valid:
                return _computed_balance_values(starting_balance, trades), ["invalid_balance_history"]
            values.append(round(value, 8))
        if values:
            return values, []
    elif balance_history is not None:
        return _computed_balance_values(starting_balance, trades), ["invalid_balance_history"]
    return _computed_balance_values(starting_balance, trades), []


def _computed_balance_values(starting_balance: float, trades: list[dict[str, float]]) -> list[float]:
    equity = starting_balance
    values = [round(equity, 8)]
    for trade in trades:
        equity = round(equity + trade["pnl"], 8)
        values.append(equity)
    return values


def _max_drawdown(values: list[float]) -> float:
    peak: float | None = None
    drawdown = 0.0
    for value in values:
        peak = value if peak is None else max(peak, value)
        drawdown = max(drawdown, peak - value)
    return round(drawdown, 8)


def _max_consecutive_losses(trades: list[dict[str, float]]) -> int:
    longest = 0
    current = 0
    for trade in trades:
        if trade["pnl"] < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "live_trading_allowed": False,
        "broker_execution_allowed": False,
        "credentials_allowed": False,
        "production_deployment_allowed": False,
        "network_used": False,
        "live_order_placed": False,
    }


def evaluate_paper_profitability(
    paper_trade_ledger: Any = None,
    replay_evidence: Any = None,
    session_metrics: Any = None,
    balance_history: Any = None,
    limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate paper-only profitability evidence and gate demo-review readiness."""
    caps = {
        "minimum_trades": 5,
        "minimum_profit_factor": 1.2,
        "maximum_drawdown": 500.0,
        "minimum_expectancy_per_trade": 0.0,
        "minimum_expectancy_r": 0.0,
        **dict(limits or {}),
    }
    blocked_reasons: list[str] = []

    ledger_trades, ledger_reasons = _trades_from_ledger(paper_trade_ledger)
    replay_trades, replay_reasons = _trades_from_replay(replay_evidence)
    for reason in ledger_reasons + replay_reasons:
        _append_once(blocked_reasons, reason)
    if not ledger_trades:
        blocked_reasons.append("missing_ledger_evidence")
    if not replay_trades:
        blocked_reasons.append("missing_replay_evidence")
    if ledger_trades and replay_trades and not _trades_match(ledger_trades, replay_trades):
        blocked_reasons.append("inconsistent_ledger_replay_evidence")

    trades = ledger_trades or replay_trades
    if not trades:
        trades = _extract_closed_trades(paper_trade_ledger, replay_evidence, session_metrics)
    total_trades = len(trades)
    winners = [trade for trade in trades if trade["pnl"] > 0]
    losers = [trade for trade in trades if trade["pnl"] < 0]
    breakeven = [trade for trade in trades if trade["pnl"] == 0]
    gross_profit = round(sum(trade["pnl"] for trade in winners), 8)
    gross_loss = round(abs(sum(trade["pnl"] for trade in losers)), 8)
    win_rate_pct = round((len(winners) / total_trades) * 100.0, 8) if total_trades else 0.0
    average_win = round(gross_profit / len(winners), 8) if winners else 0.0
    average_loss = round(gross_loss / len(losers), 8) if losers else 0.0
    expectancy_per_trade = round(sum(trade["pnl"] for trade in trades) / total_trades, 8) if total_trades else 0.0
    profit_factor = round(gross_profit / gross_loss, 8) if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)
    risk_values = [trade["risk"] for trade in trades if trade["risk"] > 0]
    average_risk = round(sum(risk_values) / len(risk_values), 8) if risk_values else 0.0
    expectancy_r = round(expectancy_per_trade / average_risk, 8) if average_risk > 0 else 0.0
    starting_balance = _safe_float(
        replay_evidence.get("starting_balance", replay_evidence.get("balance_start", 10000.0)) if isinstance(replay_evidence, Mapping) else 10000.0,
        10000.0,
    )
    balances, balance_reasons = _balance_values(balance_history, starting_balance, trades)
    for reason in balance_reasons:
        _append_once(blocked_reasons, reason)
    max_drawdown = _max_drawdown(balances)
    consecutive_loss_count = _max_consecutive_losses(trades)

    sample_size_met = total_trades >= _safe_int(caps["minimum_trades"])
    if not sample_size_met:
        blocked_reasons.append("insufficient_sample_size")
    if expectancy_per_trade <= _safe_float(caps["minimum_expectancy_per_trade"]):
        blocked_reasons.append("negative_expectancy")
    if expectancy_r <= _safe_float(caps["minimum_expectancy_r"]):
        blocked_reasons.append("negative_expectancy_r")
    if profit_factor < _safe_float(caps["minimum_profit_factor"]):
        blocked_reasons.append("profit_factor_below_threshold")
    if max_drawdown > _safe_float(caps["maximum_drawdown"]):
        blocked_reasons.append("excessive_drawdown")

    risk_quality_passed = not any(reason in {"excessive_drawdown", "invalid_balance_history"} for reason in blocked_reasons)
    evidence_quality_passed = not any(
        reason
        in {
            "missing_ledger_evidence",
            "missing_replay_evidence",
            "invalid_ledger_evidence",
            "invalid_replay_evidence",
            "inconsistent_ledger_replay_evidence",
            "inconsistent_replay_evidence",
        }
        for reason in blocked_reasons
    )
    profitability_ready = (
        sample_size_met
        and expectancy_per_trade > _safe_float(caps["minimum_expectancy_per_trade"])
        and expectancy_r > _safe_float(caps["minimum_expectancy_r"])
        and profit_factor >= _safe_float(caps["minimum_profit_factor"])
        and risk_quality_passed
        and evidence_quality_passed
        and not blocked_reasons
    )
    allowed = profitability_ready

    return {
        "allowed": allowed,
        "decision": "REVIEW_FOR_DEMO_VALIDATION" if allowed else "CONTINUE_PAPER_TRADING",
        "blocked_reasons": blocked_reasons,
        "profitability_ready": profitability_ready,
        "sample_size_met": sample_size_met,
        "expectancy_per_trade": expectancy_per_trade,
        "expectancy_r": expectancy_r,
        "profit_factor": profit_factor,
        "win_rate_pct": win_rate_pct,
        "average_win": average_win,
        "average_loss": average_loss,
        "max_drawdown": max_drawdown,
        "risk_quality_passed": risk_quality_passed,
        "evidence_quality_passed": evidence_quality_passed,
        "next_safe_action": "review_for_demo_validation" if allowed else "continue_paper_trading_collect_more_evidence",
        "safety": _safety(),
        "mode": MODE,
        "metrics": {
            "total_trades": total_trades,
            "winners": len(winners),
            "losers": len(losers),
            "breakeven": len(breakeven),
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "consecutive_loss_count": consecutive_loss_count,
            "average_risk": average_risk,
            "balance_points": balances,
        },
    }
