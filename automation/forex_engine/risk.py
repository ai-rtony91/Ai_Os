"""Risk controls for the AI_OS Forex Engine v1 paper-only scaffold."""

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import EngineMode, RiskDecision, TradeOutcome


class RiskEngine:
    def __init__(self, config: ForexEngineConfig):
        self.config = config

    def calculate_risk_amount(self, balance_usd: float) -> float:
        return round(balance_usd * (self.config.paper_risk_per_trade_pct / 100), 2)

    def calculate_daily_drawdown_limit(self, balance_usd: float) -> float:
        return round(balance_usd * (self.config.max_daily_drawdown_pct / 100), 2)

    def count_consecutive_losses(self, closed_trades) -> int:
        streak = 0
        for trade in reversed(list(closed_trades)):
            if trade.outcome == TradeOutcome.LOSS:
                streak += 1
                continue
            break
        return streak

    def can_open_new_trade(
        self,
        open_trades,
        closed_trades,
        current_balance_usd: float,
        current_daily_pnl_usd: float,
    ) -> RiskDecision:
        risk_amount = self.calculate_risk_amount(current_balance_usd)
        daily_limit = self.calculate_daily_drawdown_limit(current_balance_usd)
        open_count = len(open_trades)
        loss_streak = self.count_consecutive_losses(closed_trades)

        blocked_reason = None
        if self.config.mode != EngineMode.PAPER_ONLY:
            blocked_reason = "Sprint 1 only allows PAPER_ONLY mode."
        elif open_count >= self.config.max_open_trades_paper:
            blocked_reason = "Max open PAPER_ONLY trades reached."
        elif loss_streak >= self.config.pause_after_consecutive_losses:
            blocked_reason = "Consecutive loss pause threshold reached."
        elif current_daily_pnl_usd <= -daily_limit:
            blocked_reason = "Daily drawdown limit reached."
        elif risk_amount <= 0:
            blocked_reason = "Calculated risk amount must be positive."

        return RiskDecision(
            allowed=blocked_reason is None,
            risk_amount_usd=risk_amount,
            max_daily_loss_usd=daily_limit,
            open_trade_count=open_count,
            max_open_trades=self.config.max_open_trades_paper,
            consecutive_losses=loss_streak,
            blocked_reason=blocked_reason,
        )

    def calculate_position_size_units(self, signal, risk_amount_usd: float) -> float:
        """Sprint 1 position sizing is simulation-grade only and is not broker-ready.

        Pip value, contract size, lot size, XAUUSD tick value, spread, slippage,
        swaps, and commissions are later sprint work.
        """
        stop_distance = abs(signal.entry_price - signal.stop_loss)
        if stop_distance <= 0:
            raise ValueError("Stop distance must be greater than zero.")
        return risk_amount_usd / stop_distance
