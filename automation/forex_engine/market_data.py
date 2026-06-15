"""Local CSV candle loading for PAPER_ONLY market data research."""

import csv
from pathlib import Path

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.models import Candle


FIXTURE_COLUMNS = ("timestamp", "symbol", "timeframe", "open", "high", "low", "close", "volume")
LOCAL_IMPORT_REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close")
LOCAL_IMPORT_OPTIONAL_COLUMNS = ("volume", "symbol", "timeframe")
REQUIRED_COLUMNS = FIXTURE_COLUMNS


def load_candles_from_csv(path, config: ForexEngineConfig):
    csv_path = Path(path)
    candles = []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if fieldnames == list(FIXTURE_COLUMNS):
            symbol = None
            timeframe = None
        else:
            _validate_local_import_header(fieldnames)
            symbol = config.symbols[0]
            timeframe = config.timeframes[1] if len(config.timeframes) > 1 else config.timeframes[0]
        for row in reader:
            row_symbol = row.get("symbol") or symbol
            row_timeframe = row.get("timeframe") or timeframe
            for column in LOCAL_IMPORT_REQUIRED_COLUMNS:
                if row.get(column) in (None, ""):
                    raise ValueError(f"Candle CSV missing required value: {column}")
            candle = Candle(
                symbol=row_symbol,
                timeframe=row_timeframe,
                timestamp=row["timestamp"],
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row.get("volume") or 0),
                source=str(csv_path),
            )
            validate_candle(candle, config)
            candles.append(candle)
    validate_candle_sequence(candles)
    return candles


def load_local_candle_csv(path, config=None, symbol=None, timeframe=None):
    """Load a local-only exported candle CSV. No network or broker access is used."""
    active_config = config or ForexEngineConfig()
    candles = load_candles_from_csv(path, active_config)
    if symbol:
        for candle in candles:
            candle.symbol = symbol
    if timeframe:
        for candle in candles:
            candle.timeframe = timeframe
    validate_candle_sequence(candles)
    return candles


def _validate_local_import_header(fieldnames):
    missing = [column for column in LOCAL_IMPORT_REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"CSV missing required OHLC columns: {', '.join(missing)}")
    allowed = set(LOCAL_IMPORT_REQUIRED_COLUMNS + LOCAL_IMPORT_OPTIONAL_COLUMNS)
    unknown = [column for column in fieldnames if column not in allowed]
    if unknown:
        raise ValueError(f"CSV contains unsupported columns for local import: {', '.join(unknown)}")


def validate_candle(candle: Candle, config: ForexEngineConfig) -> None:
    if candle.symbol not in config.symbols:
        raise ValueError(f"Candle symbol is not configured: {candle.symbol}")
    if candle.timeframe not in config.timeframes:
        raise ValueError(f"Candle timeframe is not configured: {candle.timeframe}")
    if not candle.timestamp:
        raise ValueError("Candle timestamp must not be empty.")
    if min(candle.open, candle.high, candle.low, candle.close) <= 0:
        raise ValueError("Candle prices must be positive.")
    if candle.high < max(candle.open, candle.low, candle.close):
        raise ValueError("Candle high must be greater than or equal to open, low, and close.")
    if candle.low > min(candle.open, candle.high, candle.close):
        raise ValueError("Candle low must be less than or equal to open, high, and close.")
    if candle.volume < 0:
        raise ValueError("Candle volume must be zero or positive.")
    if not candle.source:
        raise ValueError("Candle source must not be empty.")


def validate_candle_sequence(candles) -> None:
    if not candles:
        raise ValueError("Candle sequence must not be empty.")

    symbols = {candle.symbol for candle in candles}
    if len(symbols) != 1:
        raise ValueError("Candle sequence must contain one symbol.")

    timeframes = {candle.timeframe for candle in candles}
    if len(timeframes) != 1:
        raise ValueError("Candle sequence must contain one timeframe.")

    timestamps = [candle.timestamp for candle in candles]
    if len(set(timestamps)) != len(timestamps):
        raise ValueError("Candle timestamps must be unique.")
    if timestamps != sorted(timestamps):
        raise ValueError("Candle timestamps must be sorted ascending.")


def load_fixture_candles(symbol: str, timeframe: str, config: ForexEngineConfig):
    fixture_path = Path(config.fixture_data_dir) / f"{symbol}_{timeframe}_sample.csv"
    if not fixture_path.exists():
        raise ValueError(f"Local PAPER_ONLY fixture not found: {fixture_path}")
    return load_candles_from_csv(fixture_path, config)


def summarize_candles(candles):
    validate_candle_sequence(candles)
    return {
        "symbol": candles[0].symbol,
        "timeframe": candles[0].timeframe,
        "count": len(candles),
        "first_timestamp": candles[0].timestamp,
        "last_timestamp": candles[-1].timestamp,
        "min_low": min(candle.low for candle in candles),
        "max_high": max(candle.high for candle in candles),
        "first_close": candles[0].close,
        "last_close": candles[-1].close,
    }
