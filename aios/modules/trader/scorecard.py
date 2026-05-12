"""Paper-only scorecard metrics."""

from __future__ import annotations

from aios.modules.trader.execution_quality import build_execution_quality_metrics


def build_paper_scorecard(
    outcomes: list[dict[str, object]],
    starting_cash: float = 100000.0,
    blocked_decisions: int = 0,
    execution_records: list[dict[str, object]] | None = None,
    rejected_order_count: int = 0,
    risk_block_count: int = 0,
    live_execution_status: str = "BLOCKED",
    execution_allowed: bool = False,
) -> dict[str, object]:
    if live_execution_status != "BLOCKED":
        raise ValueError("Paper scorecard requires live execution to remain BLOCKED.")
    if execution_allowed:
        raise ValueError("Paper scorecard requires execution_allowed to remain false.")

    closed_outcomes = [
        outcome for outcome in outcomes if outcome.get("status") == "CLOSED_PAPER"
    ]
    pnl_values = [_paper_pnl(outcome) for outcome in closed_outcomes]
    wins = [pnl for pnl in pnl_values if pnl > 0]
    losses = [pnl for pnl in pnl_values if pnl < 0]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    total_trades = len(pnl_values)
    ending_cash = starting_cash + sum(pnl_values)
    execution_quality = build_execution_quality_metrics(
        execution_records,
        rejected_order_count=rejected_order_count,
        risk_block_count=risk_block_count,
    )

    scorecard = {
        "total_trades": total_trades,
        "paper_wins": len(wins),
        "paper_losses": len(losses),
        "win_rate": _safe_divide(len(wins), total_trades),
        "average_win": _safe_divide(gross_profit, len(wins)),
        "average_loss": _safe_divide(sum(losses), len(losses)),
        "expectancy": _safe_divide(sum(pnl_values), total_trades),
        "profit_factor": None if gross_loss == 0.0 else gross_profit / gross_loss,
        "max_drawdown": _max_drawdown(starting_cash, pnl_values),
        "starting_cash": starting_cash,
        "ending_cash": ending_cash,
        "blocked_decisions": blocked_decisions,
        "paper_only": True,
        "live_execution_status": live_execution_status,
        "execution_allowed": execution_allowed,
    }
    scorecard.update(execution_quality)
    return scorecard


def _paper_pnl(outcome: dict[str, object]) -> float:
    if "pnl" in outcome:
        return float(outcome["pnl"])

    side = str(outcome["side"]).upper()
    entry = float(outcome["entry_price"])
    exit_price = float(outcome["exit_price"])
    quantity = int(outcome["quantity"])
    if side in {"LONG", "BUY", "BUY_REVIEW"}:
        return (exit_price - entry) * quantity
    if side in {"SHORT", "SELL", "SELL_REVIEW"}:
        return (entry - exit_price) * quantity
    raise ValueError(f"Unsupported paper outcome side: {side}")


def _safe_divide(numerator: float, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _max_drawdown(starting_cash: float, pnl_values: list[float]) -> float:
    equity = starting_cash
    peak = starting_cash
    max_drawdown = 0.0
    for pnl in pnl_values:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return max_drawdown
