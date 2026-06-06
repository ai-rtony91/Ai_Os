"""Signal validation and demo signals for PAPER_ONLY simulation."""

from automation.forex_engine.models import Direction, ForexSignal, utc_now_iso


def validate_signal(signal: ForexSignal, config) -> list:
    reasons = []
    if signal.symbol not in config.symbols:
        raise ValueError(f"Unsupported symbol for PAPER_ONLY config: {signal.symbol}")
    reasons.append("Symbol is configured for PAPER_ONLY simulation.")

    if signal.timeframe not in config.timeframes:
        raise ValueError(f"Unsupported timeframe for PAPER_ONLY config: {signal.timeframe}")
    reasons.append("Timeframe is configured for PAPER_ONLY simulation.")

    if signal.direction not in (Direction.BUY, Direction.SELL):
        raise ValueError("Direction must be BUY or SELL.")
    if signal.entry_price <= 0:
        raise ValueError("Entry price must be positive.")
    if signal.stop_loss <= 0:
        raise ValueError("Stop loss must be positive.")
    if signal.take_profit <= 0:
        raise ValueError("Take profit must be positive.")
    if not signal.strategy_name:
        raise ValueError("Strategy name must not be empty.")

    if signal.direction == Direction.BUY:
        if not signal.stop_loss < signal.entry_price < signal.take_profit:
            raise ValueError("BUY signal requires stop below entry and target above entry.")
    if signal.direction == Direction.SELL:
        if not signal.take_profit < signal.entry_price < signal.stop_loss:
            raise ValueError("SELL signal requires stop above entry and target below entry.")

    reasons.append("Price structure is valid for PAPER_ONLY simulation.")
    return reasons


def create_demo_signals():
    timestamp = utc_now_iso()
    return [
        ForexSignal(
            symbol="EURUSD",
            timeframe="5m",
            direction=Direction.BUY,
            entry_price=1.0800,
            stop_loss=1.0790,
            take_profit=1.0820,
            timestamp=timestamp,
            strategy_name="paper_intraday_breakout",
            metadata={"setup_quality": "clean", "session": "london"},
        ),
        ForexSignal(
            symbol="GBPUSD",
            timeframe="15m",
            direction=Direction.SELL,
            entry_price=1.2700,
            stop_loss=1.2720,
            take_profit=1.2660,
            timestamp=timestamp,
            strategy_name="paper_intraday_reversal",
            metadata={"setup_quality": "clean", "session": "new_york"},
        ),
        ForexSignal(
            symbol="USDJPY",
            timeframe="5m",
            direction=Direction.BUY,
            entry_price=155.20,
            stop_loss=155.00,
            take_profit=155.55,
            timestamp=timestamp,
            strategy_name="paper_intraday_momentum",
            metadata={"setup_quality": "watch", "session": "asia"},
        ),
        ForexSignal(
            symbol="XAUUSD",
            timeframe="15m",
            direction=Direction.SELL,
            entry_price=2350.0,
            stop_loss=2355.0,
            take_profit=2340.0,
            timestamp=timestamp,
            strategy_name="paper_gold_pullback",
            metadata={"setup_quality": "clean", "session": "new_york"},
        ),
    ]
