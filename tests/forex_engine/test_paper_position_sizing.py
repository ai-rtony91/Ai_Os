"""Tests for deterministic paper position sizing."""
from __future__ import annotations

from automation.forex_engine.paper_position_sizing import calculate_paper_position_size


def test_position_sizing_normal_case():
    result = calculate_paper_position_size(10000.0, 1.0, 1.1, 1.095)
    assert result["sizing_passed"] is True
    assert result["risk_dollars"] == 100.0
    assert result["stop_distance"] == 0.005
    assert result["units"] == 20000.0


def test_position_sizing_rejects_zero_stop_distance():
    result = calculate_paper_position_size(10000.0, 1.0, 1.1, 1.1)
    assert result["sizing_passed"] is False
    assert "zero_stop_distance" in result["rejection_reasons"]
