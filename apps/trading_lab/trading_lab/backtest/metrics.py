from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metrics:
    total_trades: int
    win_rate: float
    average_r: float
    max_drawdown: float
    profit_factor: float
    expectancy: float
    consecutive_losses: int


def calculate_metrics(results: list[float]) -> Metrics:
    if not results:
        return Metrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
    wins = [value for value in results if value > 0]
    losses = [value for value in results if value < 0]
    total = len(results)
    win_rate = len(wins) / total
    average_r = sum(results) / total
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_win / gross_loss if gross_loss else float(len(wins) > 0)
    equity = 0.0
    peak = 0.0
    max_drawdown = 0.0
    current_losses = 0
    consecutive_losses = 0
    for result in results:
        equity += result
        peak = max(peak, equity)
        max_drawdown = min(max_drawdown, equity - peak)
        if result < 0:
            current_losses += 1
            consecutive_losses = max(consecutive_losses, current_losses)
        else:
            current_losses = 0
    return Metrics(
        total_trades=total,
        win_rate=win_rate,
        average_r=average_r,
        max_drawdown=max_drawdown,
        profit_factor=profit_factor,
        expectancy=average_r,
        consecutive_losses=consecutive_losses,
    )
