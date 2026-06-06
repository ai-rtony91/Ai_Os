"""Basic analytics for PAPER_ONLY forex simulation results."""

from automation.forex_engine.models import PerformanceSummary, TradeOutcome


class ForexAnalytics:
    def summarize(self, starting_balance_usd, current_balance_usd, open_trades, closed_trades) -> PerformanceSummary:
        closed_count = len(closed_trades)
        open_count = len(open_trades)
        wins = sum(1 for trade in closed_trades if trade.outcome == TradeOutcome.WIN)
        losses = sum(1 for trade in closed_trades if trade.outcome == TradeOutcome.LOSS)
        breakeven = sum(1 for trade in closed_trades if trade.outcome == TradeOutcome.BREAKEVEN)
        gross_profit = round(sum(trade.pnl_usd for trade in closed_trades if trade.pnl_usd > 0), 2)
        gross_loss = round(abs(sum(trade.pnl_usd for trade in closed_trades if trade.pnl_usd < 0)), 2)
        net_pnl = round(sum(trade.pnl_usd for trade in closed_trades), 2)
        win_rate = round((wins / closed_count) * 100, 2) if closed_count else 0.0

        profit_factor = None
        if gross_loss > 0:
            profit_factor = round(gross_profit / gross_loss, 2)

        max_drawdown_usd = round(max(0.0, starting_balance_usd - current_balance_usd), 2)
        max_drawdown_pct = round((max_drawdown_usd / starting_balance_usd) * 100, 2) if starting_balance_usd else 0.0
        loss_streak = self._count_consecutive_losses(closed_trades)
        consistency_note = self._consistency_note(closed_count, wins, losses, gross_profit, gross_loss)

        return PerformanceSummary(
            starting_balance_usd=starting_balance_usd,
            current_balance_usd=current_balance_usd,
            total_trades=open_count + closed_count,
            open_trades=open_count,
            closed_trades=closed_count,
            wins=wins,
            losses=losses,
            breakeven=breakeven,
            win_rate_pct=win_rate,
            gross_profit_usd=gross_profit,
            gross_loss_usd=gross_loss,
            net_pnl_usd=net_pnl,
            profit_factor=profit_factor,
            max_drawdown_usd=max_drawdown_usd,
            max_drawdown_pct=max_drawdown_pct,
            consecutive_losses=loss_streak,
            consistency_note=consistency_note,
        )

    def _count_consecutive_losses(self, closed_trades) -> int:
        streak = 0
        for trade in reversed(list(closed_trades)):
            if trade.outcome == TradeOutcome.LOSS:
                streak += 1
                continue
            break
        return streak

    def _consistency_note(self, closed_count, wins, losses, gross_profit, gross_loss) -> str:
        if closed_count == 0:
            return "No closed trades yet"
        if gross_loss == 0 and gross_profit > 0:
            return "Positive sample; more data required. Profit factor is undefined without gross loss."
        if wins > 0 and losses > 0:
            return "Mixed sample; more data required"
        if losses > wins:
            return "Negative sample; review required"
        return "Positive sample; more data required"
