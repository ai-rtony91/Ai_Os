"""PAPER_ONLY execution simulation for the AI_OS Forex Engine v1 scaffold."""

from uuid import uuid4

from automation.forex_engine.models import Direction, EngineMode, PaperTrade, TradeOutcome, TradeStatus, utc_now_iso
from automation.forex_engine.signals import validate_signal


class PaperExecutionEngine:
    def __init__(self, config, risk_engine, journal_writer=None):
        self.config = config
        self.risk_engine = risk_engine
        self.journal_writer = journal_writer
        self.current_balance_usd = config.starting_balance_usd
        self.open_trades = []
        self.closed_trades = []

    def submit_signal(self, signal, confidence_assessment, current_daily_pnl_usd=0.0):
        if self.config.mode != EngineMode.PAPER_ONLY:
            raise ValueError("PaperExecutionEngine only supports PAPER_ONLY mode in Sprint 1.")
        if not confidence_assessment.allowed:
            raise ValueError(confidence_assessment.blocked_reason or "Signal confidence blocked.")

        validate_signal(signal, self.config)
        risk_decision = self.risk_engine.can_open_new_trade(
            self.open_trades,
            self.closed_trades,
            self.current_balance_usd,
            current_daily_pnl_usd,
        )
        if not risk_decision.allowed:
            raise ValueError(risk_decision.blocked_reason or "Risk engine blocked PAPER_ONLY trade.")

        position_size_units = self.risk_engine.calculate_position_size_units(
            signal,
            risk_decision.risk_amount_usd,
        )
        trade = PaperTrade(
            trade_id=f"PAPER-{uuid4().hex[:12]}",
            mode=EngineMode.PAPER_ONLY,
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            position_size_units=position_size_units,
            risk_amount_usd=risk_decision.risk_amount_usd,
            confidence_score=confidence_assessment.score,
            status=TradeStatus.OPEN,
            opened_at=signal.timestamp or utc_now_iso(),
            metadata=dict(signal.metadata),
        )
        self.open_trades.append(trade)
        if self.journal_writer:
            self.journal_writer.write_trade_opened(trade)
        return trade

    def close_trade(self, trade_id, exit_price, closed_at=None):
        trade = next((open_trade for open_trade in self.open_trades if open_trade.trade_id == trade_id), None)
        if trade is None:
            raise ValueError(f"Open PAPER_ONLY trade not found: {trade_id}")
        if exit_price <= 0:
            raise ValueError("Exit price must be positive.")

        if trade.direction == Direction.BUY:
            pnl = (exit_price - trade.entry_price) * trade.position_size_units
        elif trade.direction == Direction.SELL:
            pnl = (trade.entry_price - exit_price) * trade.position_size_units
        else:
            raise ValueError("Trade direction must be BUY or SELL.")

        trade.pnl_usd = round(pnl, 2)
        trade.exit_price = exit_price
        trade.closed_at = closed_at or utc_now_iso()
        trade.status = TradeStatus.CLOSED
        if trade.pnl_usd > 0:
            trade.outcome = TradeOutcome.WIN
        elif trade.pnl_usd < 0:
            trade.outcome = TradeOutcome.LOSS
        else:
            trade.outcome = TradeOutcome.BREAKEVEN

        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.current_balance_usd = round(self.current_balance_usd + trade.pnl_usd, 2)
        if self.journal_writer:
            self.journal_writer.write_trade_closed(trade)
        return trade
