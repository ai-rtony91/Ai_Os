"""Deterministic paper position sizing."""
from __future__ import annotations

from typing import Any


def calculate_paper_position_size(
    balance: float,
    risk_percent: float,
    entry: float,
    stop: float,
    max_units: float = 100000.0,
    min_units: float = 1.0,
    pip_value: float = 1.0,
    max_risk_percent: float = 2.0,
) -> dict[str, Any]:
    """Calculate paper units from balance, risk percent, and stop distance."""
    rejection_reasons: list[str] = []
    balance_value = float(balance)
    risk_percent_value = float(risk_percent)
    entry_value = float(entry)
    stop_value = float(stop)
    pip_value_amount = float(pip_value)
    stop_distance = round(abs(entry_value - stop_value), 8)

    if balance_value <= 0:
        rejection_reasons.append("negative_balance")
    if stop_distance <= 0:
        rejection_reasons.append("zero_stop_distance")
    if risk_percent_value <= 0 or risk_percent_value > float(max_risk_percent):
        rejection_reasons.append("excessive_risk_percent")
    if pip_value_amount <= 0:
        rejection_reasons.append("invalid_pip_value")

    risk_dollars = round(max(0.0, balance_value) * risk_percent_value / 100.0, 8)
    units = 0.0
    if not rejection_reasons:
        units = round(risk_dollars / (stop_distance * pip_value_amount), 8)
        if units < float(min_units):
            rejection_reasons.append("units_below_minimum")
        if units > float(max_units):
            rejection_reasons.append("units_above_maximum")

    return {
        "risk_dollars": risk_dollars,
        "risk_percent": risk_percent_value,
        "stop_distance": stop_distance,
        "pip_value": pip_value_amount,
        "units": units if not rejection_reasons else 0.0,
        "min_units": float(min_units),
        "max_units": float(max_units),
        "sizing_passed": not rejection_reasons,
        "rejection_reasons": rejection_reasons,
        "paper_only": True,
    }
