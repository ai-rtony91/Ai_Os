from __future__ import annotations

import pandas as pd

from .engine import load_candles, run_backtest


def run_walk_forward(symbol: str, timeframe: str, windows: int = 3) -> dict:
    candles = load_candles(symbol, timeframe)
    if candles.empty or len(candles) < windows * 60:
        return {"status": "insufficient_data", "windows": []}
    candles = candles.sort_values("timestamp")
    splits = [frame for frame in pd.array_split(candles, windows) if not frame.empty]
    results = []
    for index, window in enumerate(splits, start=1):
        start = window["timestamp"].min().isoformat()
        end = window["timestamp"].max().isoformat()
        result = run_backtest(symbol=symbol, timeframe=timeframe, start_date=start, end_date=end)
        result["window"] = index
        result["start_date"] = start
        result["end_date"] = end
        results.append(result)
    return {"status": "paper_walk_forward_complete", "windows": results}
