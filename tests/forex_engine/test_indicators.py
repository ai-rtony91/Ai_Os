import pytest

from automation.forex_engine.daily_edge_report import deterministic_supertrend_sample
from automation.forex_engine.indicators import DOWN, FLAT, UP, atr, supertrend, true_range


def test_true_range_basic_correctness():
    candles = deterministic_supertrend_sample(count=4)
    ranges = true_range(candles)
    assert len(ranges) == 4
    assert ranges[0] == pytest.approx(candles[0].high - candles[0].low)
    assert all(value > 0 for value in ranges)


def test_atr_same_length_output_and_initial_none():
    candles = deterministic_supertrend_sample(count=8)
    values = atr(candles, period=3)
    assert len(values) == len(candles)
    assert values[:2] == [None, None]
    assert values[-1] is not None


def test_supertrend_direction_values_are_constrained():
    candles = deterministic_supertrend_sample(count=12)
    trend = supertrend(candles, period=3, multiplier=2)
    assert len(trend) == len(candles)
    assert {item["direction"] for item in trend}.issubset({UP, DOWN, FLAT})


def test_supertrend_handles_insufficient_data_cleanly():
    candles = deterministic_supertrend_sample(count=2)
    trend = supertrend(candles, period=3, multiplier=2)
    assert [item["supertrend"] for item in trend] == [None, None]
