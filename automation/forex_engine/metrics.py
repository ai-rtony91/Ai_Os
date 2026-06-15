"""PAPER_ONLY edge metrics for deterministic strategy research."""

from collections import Counter


def _trade_value(trade, key, default=0.0):
    if isinstance(trade, dict):
        return trade.get(key, default)
    return getattr(trade, key, default)


def calculate_edge_metrics(trades, starting_balance_usd=500.0, no_trade_reasons=None):
    closed = list(trades)
    total = len(closed)
    wins = [trade for trade in closed if float(_trade_value(trade, "pnl_usd", 0.0)) > 0]
    losses = [trade for trade in closed if float(_trade_value(trade, "pnl_usd", 0.0)) < 0]
    gross_profit = round(sum(float(_trade_value(trade, "pnl_usd", 0.0)) for trade in wins), 2)
    gross_loss = round(abs(sum(float(_trade_value(trade, "pnl_usd", 0.0)) for trade in losses)), 2)
    net_pnl = round(gross_profit - gross_loss, 2)
    r_values = [float(_trade_value(trade, "r_multiple", 0.0)) for trade in closed]
    average_r = round(sum(r_values) / total, 4) if total else 0.0
    expectancy_r = average_r
    win_rate = round((len(wins) / total) * 100, 2) if total else 0.0
    profit_factor = round(gross_profit / gross_loss, 4) if gross_loss else None
    drawdown = _max_drawdown([float(_trade_value(trade, "pnl_usd", 0.0)) for trade in closed], starting_balance_usd)

    return {
        "mode": "PAPER_ONLY",
        "total_trades": total,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": win_rate,
        "average_r": average_r,
        "expectancy_r": expectancy_r,
        "profit_factor": profit_factor,
        "net_pnl_usd": net_pnl,
        "max_drawdown_usd": drawdown["max_drawdown_usd"],
        "max_drawdown_pct": drawdown["max_drawdown_pct"],
        "longest_losing_streak": _longest_losing_streak(closed),
        "no_trade_reason_counts": dict(Counter(no_trade_reasons or [])),
        "pass": total > 0 and expectancy_r > 0,
        "claim_blocker": "paper-only evidence; not a profitability claim",
    }


def _longest_losing_streak(trades):
    longest = 0
    current = 0
    for trade in trades:
        if float(_trade_value(trade, "pnl_usd", 0.0)) < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _max_drawdown(pnls, starting_balance):
    equity = starting_balance
    peak = starting_balance
    max_drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return {
        "max_drawdown_usd": round(max_drawdown, 2),
        "max_drawdown_pct": round((max_drawdown / starting_balance) * 100, 2) if starting_balance else 0.0,
    }
