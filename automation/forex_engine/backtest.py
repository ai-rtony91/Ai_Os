"""Local PAPER_ONLY backtest runner for AI_OS Forex Engine v1 Sprint 3."""

from automation.forex_engine.analytics import ForexAnalytics
from automation.forex_engine.confidence import ConfidenceEngine
from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import load_fixture_candles, validate_candle_sequence
from automation.forex_engine.models import (
    BacktestConfig,
    BacktestResult,
    BacktestTradeResult,
    Direction,
    EngineMode,
    ForexSignal,
)
from automation.forex_engine.paper_execution import PaperExecutionEngine
from automation.forex_engine.risk import RiskEngine


STOP_LOSS = "STOP_LOSS"
TAKE_PROFIT = "TAKE_PROFIT"
END_OF_BACKTEST = "END_OF_BACKTEST"


class BacktestEngine:
    def __init__(self, config, risk_engine, confidence_engine, journal_writer=None):
        self.config = config
        self.risk_engine = risk_engine
        self.confidence_engine = confidence_engine
        self.journal_writer = journal_writer
        self.paper_execution_engine = PaperExecutionEngine(config, risk_engine, journal_writer)

    def run_backtest(self, candles, backtest_config=None):
        if not candles:
            raise ValueError("Backtest candles must not be empty.")
        validate_candle_sequence(candles)

        limited_candles = list(candles)
        base_config = backtest_config or BacktestConfig(
            symbol=limited_candles[0].symbol,
            timeframe=limited_candles[0].timeframe,
            starting_balance_usd=self.config.starting_balance_usd,
        )
        if base_config.mode != EngineMode.PAPER_ONLY:
            raise ValueError("BacktestConfig mode must be PAPER_ONLY.")
        if base_config.max_candles is not None:
            limited_candles = limited_candles[: base_config.max_candles]
            validate_candle_sequence(limited_candles)

        paper_engine = PaperExecutionEngine(self.config, self.risk_engine, self.journal_writer)
        paper_engine.current_balance_usd = base_config.starting_balance_usd

        signals_generated = 0
        signals_accepted = 0
        signals_blocked = 0
        previous_candle = None

        for candle in limited_candles:
            evaluate_open_trades_against_candle(paper_engine, candle)
            signal = generate_demo_signal_from_candle(candle, previous_candle, self.config)
            previous_candle = candle
            if signal is None:
                continue

            signals_generated += 1
            assessment = self.confidence_engine.score_signal(signal)
            if not assessment.allowed:
                signals_blocked += 1
                continue
            try:
                paper_engine.submit_signal(signal, assessment)
                signals_accepted += 1
            except ValueError:
                signals_blocked += 1

        close_remaining_trades_at_end(paper_engine, limited_candles[-1])
        return build_backtest_result(
            backtest_config=base_config,
            candles_processed=len(limited_candles),
            signals_generated=signals_generated,
            signals_accepted=signals_accepted,
            signals_blocked=signals_blocked,
            paper_execution_engine=paper_engine,
        )


def run_backtest(candles, backtest_config=None):
    config = ForexEngineConfig()
    engine = BacktestEngine(config, RiskEngine(config), ConfidenceEngine(config))
    return engine.run_backtest(candles, backtest_config)


def generate_demo_signal_from_candle(candle, previous_candle, config):
    if previous_candle is None:
        return None
    if candle.close == previous_candle.close:
        return None

    candle_range = max(candle.high - candle.low, candle.close * 0.001)
    stop_distance = candle_range * 0.5
    target_distance = candle_range
    direction = Direction.BUY if candle.close > previous_candle.close else Direction.SELL
    if direction == Direction.BUY:
        stop_loss = candle.close - stop_distance
        take_profit = candle.close + target_distance
    else:
        stop_loss = candle.close + stop_distance
        take_profit = candle.close - target_distance

    return ForexSignal(
        symbol=candle.symbol,
        timeframe=candle.timeframe,
        direction=direction,
        entry_price=candle.close,
        stop_loss=round(stop_loss, 5),
        take_profit=round(take_profit, 5),
        timestamp=candle.timestamp,
        strategy_name="sprint_3_demo_strategy",
        metadata={
            "source": "local_backtest_demo",
            "setup_quality": "demo",
            "session": "fixture",
            "warning": "demo strategy only",
        },
    )


def evaluate_open_trades_against_candle(paper_execution_engine, candle):
    closed = []
    for trade in list(paper_execution_engine.open_trades):
        close_price = None
        close_reason = None
        if trade.direction == Direction.BUY:
            if candle.low <= trade.stop_loss:
                close_price = trade.stop_loss
                close_reason = STOP_LOSS
            elif candle.high >= trade.take_profit:
                close_price = trade.take_profit
                close_reason = TAKE_PROFIT
        elif trade.direction == Direction.SELL:
            if candle.high >= trade.stop_loss:
                close_price = trade.stop_loss
                close_reason = STOP_LOSS
            elif candle.low <= trade.take_profit:
                close_price = trade.take_profit
                close_reason = TAKE_PROFIT

        if close_reason:
            trade.metadata["close_reason"] = close_reason
            closed.append(paper_execution_engine.close_trade(trade.trade_id, close_price, candle.timestamp))
    return closed


def close_remaining_trades_at_end(paper_execution_engine, last_candle):
    closed = []
    for trade in list(paper_execution_engine.open_trades):
        trade.metadata["close_reason"] = END_OF_BACKTEST
        closed.append(paper_execution_engine.close_trade(trade.trade_id, last_candle.close, last_candle.timestamp))
    return closed


def build_backtest_result(
    backtest_config,
    candles_processed,
    signals_generated,
    signals_accepted,
    signals_blocked,
    paper_execution_engine,
):
    summary = ForexAnalytics().summarize(
        backtest_config.starting_balance_usd,
        paper_execution_engine.current_balance_usd,
        paper_execution_engine.open_trades,
        paper_execution_engine.closed_trades,
    )
    trade_results = [
        BacktestTradeResult(
            trade_id=trade.trade_id,
            symbol=trade.symbol,
            timeframe=trade.timeframe,
            direction=trade.direction,
            entry_price=trade.entry_price,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            exit_price=trade.exit_price,
            opened_at=trade.opened_at,
            closed_at=trade.closed_at,
            outcome=trade.outcome,
            pnl_usd=trade.pnl_usd,
            confidence_score=trade.confidence_score,
            close_reason=trade.metadata.get("close_reason", END_OF_BACKTEST),
            metadata=dict(trade.metadata),
        )
        for trade in paper_execution_engine.closed_trades
    ]
    return BacktestResult(
        mode=EngineMode.PAPER_ONLY,
        symbol=backtest_config.symbol,
        timeframe=backtest_config.timeframe,
        strategy_name=backtest_config.strategy_name,
        candles_processed=candles_processed,
        signals_generated=signals_generated,
        signals_accepted=signals_accepted,
        signals_blocked=signals_blocked,
        trades_opened=len(trade_results),
        trades_closed=len(trade_results),
        starting_balance_usd=backtest_config.starting_balance_usd,
        ending_balance_usd=paper_execution_engine.current_balance_usd,
        net_pnl_usd=summary.net_pnl_usd,
        win_rate_pct=summary.win_rate_pct,
        profit_factor=summary.profit_factor,
        max_drawdown_usd=summary.max_drawdown_usd,
        max_drawdown_pct=summary.max_drawdown_pct,
        results=trade_results,
        summary_note=summary.consistency_note,
    )


def run_backtest_for_fixture(symbol, timeframe, config):
    candles = load_fixture_candles(symbol, timeframe, config)
    engine = BacktestEngine(config, RiskEngine(config), ConfidenceEngine(config))
    backtest_config = BacktestConfig(
        symbol=symbol,
        timeframe=timeframe,
        starting_balance_usd=config.starting_balance_usd,
        mode=EngineMode.PAPER_ONLY,
    )
    return engine.run_backtest(candles, backtest_config)
