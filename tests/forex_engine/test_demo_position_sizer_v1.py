from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from automation.forex_engine.demo_position_sizer_v1 import (
    DEMO_POSITION_SIZE_BLOCKED_ABOVE_MAX_UNITS,
    DEMO_POSITION_SIZE_BLOCKED_BAD_REWARD_RISK,
    DEMO_POSITION_SIZE_BLOCKED_BELOW_MIN_UNITS,
    DEMO_POSITION_SIZE_BLOCKED_INVALID_BALANCE,
    DEMO_POSITION_SIZE_BLOCKED_INVALID_RISK,
    DEMO_POSITION_SIZE_BLOCKED_INVALID_STOP_DISTANCE,
    DEMO_POSITION_SIZE_READY,
    build_sample_position_size_input,
    calculate_demo_position_size,
    demo_position_size_to_jsonable_dict,
)


def test_valid_size_calculates_units() -> None:
    result = calculate_demo_position_size(build_sample_position_size_input())
    assert result.sizing_status == DEMO_POSITION_SIZE_READY
    assert result.proposed_units == 20000


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"balance": Decimal("0")}, DEMO_POSITION_SIZE_BLOCKED_INVALID_BALANCE),
        ({"risk_percent": Decimal("0")}, DEMO_POSITION_SIZE_BLOCKED_INVALID_RISK),
        ({"stop_distance_pips": Decimal("0")}, DEMO_POSITION_SIZE_BLOCKED_INVALID_STOP_DISTANCE),
        ({"min_units": 50000}, DEMO_POSITION_SIZE_BLOCKED_BELOW_MIN_UNITS),
        ({"max_units": 1000}, DEMO_POSITION_SIZE_BLOCKED_ABOVE_MAX_UNITS),
        ({"take_profit_price": Decimal("1.1010")}, DEMO_POSITION_SIZE_BLOCKED_BAD_REWARD_RISK),
    ],
)
def test_position_sizer_blocks_invalid_inputs(updates: dict[str, object], expected: str) -> None:
    result = calculate_demo_position_size(replace(build_sample_position_size_input(), **updates))
    assert result.sizing_status == expected


def test_sizing_output_includes_proposed_units() -> None:
    data = demo_position_size_to_jsonable_dict(calculate_demo_position_size())
    assert data["proposed_units"] == 20000


def test_sizing_output_includes_max_loss() -> None:
    data = demo_position_size_to_jsonable_dict(calculate_demo_position_size())
    assert data["max_loss"] == "100.00"


def test_sizing_output_includes_expected_reward() -> None:
    data = demo_position_size_to_jsonable_dict(calculate_demo_position_size())
    assert data["expected_reward"] == "200.00"


def test_sizing_repeated_output_is_deterministic() -> None:
    first = demo_position_size_to_jsonable_dict(calculate_demo_position_size())
    second = demo_position_size_to_jsonable_dict(calculate_demo_position_size())
    assert first == second
