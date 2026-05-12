from __future__ import annotations

import pandas as pd


def add_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["ema20"] = data["close"].ewm(span=20, adjust=False).mean()
    data["ema50"] = data["close"].ewm(span=50, adjust=False).mean()
    typical = (data["high"] + data["low"] + data["close"]) / 3
    cumulative_volume = data["volume"].replace(0, 1).cumsum()
    data["vwap"] = (typical * data["volume"].replace(0, 1)).cumsum() / cumulative_volume
    return data


def generate_signals(frame: pd.DataFrame, pullback_tolerance: float = 0.003) -> pd.DataFrame:
    data = add_indicators(frame)
    data["signal"] = "flat"
    data["risk_note"] = "paper_only"

    near_ema20 = (data["close"] - data["ema20"]).abs() / data["close"] <= pullback_tolerance
    near_vwap = (data["close"] - data["vwap"]).abs() / data["close"] <= pullback_tolerance
    bullish_momentum = data["close"] > data["open"]
    bearish_momentum = data["close"] < data["open"]

    long_condition = (
        (data["close"] > data["ema50"])
        & (data["ema20"] > data["ema50"])
        & (near_ema20 | near_vwap)
        & bullish_momentum
    )
    short_condition = (
        (data["close"] < data["ema50"])
        & (data["ema20"] < data["ema50"])
        & (near_ema20 | near_vwap)
        & bearish_momentum
    )
    data.loc[long_condition, "signal"] = "long"
    data.loc[short_condition, "signal"] = "short"
    return data


def recent_swing_stop(data: pd.DataFrame, index: int, side: str, lookback: int = 5) -> float:
    window = data.iloc[max(0, index - lookback): index + 1]
    if side == "long":
        return float(window["low"].min())
    return float(window["high"].max())
