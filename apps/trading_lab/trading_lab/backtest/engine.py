from __future__ import annotations

from datetime import datetime

import pandas as pd

from ..config import load_settings
from ..database import session_scope
from ..models import BacktestRun, BacktestTrade, Candle, StrategyMetric
from ..strategies.ema_vwap_pullback import generate_signals, recent_swing_stop
from .metrics import calculate_metrics


def load_candles(symbol: str, timeframe: str, start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    with session_scope() as session:
        query = session.query(Candle).filter(Candle.symbol == symbol, Candle.timeframe == timeframe)
        if start_date:
            query = query.filter(Candle.timestamp >= pd.to_datetime(start_date).to_pydatetime())
        if end_date:
            query = query.filter(Candle.timestamp <= pd.to_datetime(end_date).to_pydatetime())
        rows = query.order_by(Candle.timestamp.asc()).all()
    return pd.DataFrame([
        {
            "timestamp": row.timestamp,
            "symbol": row.symbol,
            "timeframe": row.timeframe,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in rows
    ])


def run_backtest(
    symbol: str,
    timeframe: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    settings = load_settings()
    settings.assert_paper_mode()
    candles = load_candles(symbol, timeframe, start_date, end_date)
    if candles.empty or len(candles) < 60:
        return {"status": "insufficient_data", "total_trades": 0}
    signals = generate_signals(candles)
    trades = []
    reward_risk = settings.reward_risk
    for index in range(51, len(signals) - 1):
        row = signals.iloc[index]
        side = row["signal"]
        if side not in {"long", "short"}:
            continue
        next_row = signals.iloc[index + 1]
        entry = float(next_row["open"])
        stop = recent_swing_stop(signals, index, side)
        stop_distance = abs(entry - stop)
        if stop_distance <= 0:
            continue
        target = entry + stop_distance * reward_risk if side == "long" else entry - stop_distance * reward_risk
        future = signals.iloc[index + 1: min(index + 25, len(signals))]
        result_r = None
        exit_price = float(future.iloc[-1]["close"])
        exit_time = future.iloc[-1]["timestamp"]
        for future_row in future.itertuples(index=False):
            if side == "long" and future_row.low <= stop:
                result_r = -1.0
                exit_price = stop
                exit_time = future_row.timestamp
                break
            if side == "long" and future_row.high >= target:
                result_r = reward_risk
                exit_price = target
                exit_time = future_row.timestamp
                break
            if side == "short" and future_row.high >= stop:
                result_r = -1.0
                exit_price = stop
                exit_time = future_row.timestamp
                break
            if side == "short" and future_row.low <= target:
                result_r = reward_risk
                exit_price = target
                exit_time = future_row.timestamp
                break
        if result_r is None:
            result_r = ((exit_price - entry) / stop_distance) * (1 if side == "long" else -1)
        trades.append({
            "symbol": symbol,
            "side": side,
            "entry_time": next_row["timestamp"],
            "exit_time": exit_time,
            "entry_price": entry,
            "exit_price": float(exit_price),
            "result_r": float(result_r),
        })
    metrics = calculate_metrics([trade["result_r"] for trade in trades])
    with session_scope() as session:
        run = BacktestRun(
            strategy_name="ema_vwap_pullback",
            symbol=symbol,
            timeframe=timeframe,
            start_date=pd.to_datetime(start_date).to_pydatetime() if start_date else None,
            end_date=pd.to_datetime(end_date).to_pydatetime() if end_date else None,
        )
        session.add(run)
        session.flush()
        for trade in trades:
            session.add(BacktestTrade(run_id=run.id, **trade))
        session.add(StrategyMetric(
            run_id=run.id,
            strategy_name="ema_vwap_pullback",
            symbol=symbol,
            timeframe=timeframe,
            total_trades=metrics.total_trades,
            win_rate=metrics.win_rate,
            average_r=metrics.average_r,
            max_drawdown=metrics.max_drawdown,
            profit_factor=metrics.profit_factor,
            expectancy=metrics.expectancy,
            consecutive_losses=metrics.consecutive_losses,
            metadata_json={"live_execution": "BLOCKED"},
        ))
        run_id = run.id
    return {"status": "paper_backtest_complete", "run_id": run_id, **metrics.__dict__}
