from __future__ import annotations

import ast
import inspect
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import automation.forex_engine.expectancy_strength_router_v1 as router  # noqa: E402
from automation.forex_engine.expectancy_strength_router_v1 import (  # noqa: E402
    EXPECTANCY_BLOCKED,
    EXPECTANCY_PROMISING,
    EXPECTANCY_STRONG,
    EXPECTANCY_UNKNOWN,
    EXPECTANCY_WEAK,
    ExpectancyStrengthInput,
    build_sample_blocked_expectancy_input,
    build_sample_mixed_expectancy_input,
    expectancy_strength_to_markdown,
    result_to_jsonable_dict,
    route_expectancy_strength,
)
from scripts.forex_delivery.run_expectancy_strength_router_v1 import main  # noqa: E402


def sample_input(**overrides):
    raw = {
        "strategy_id": "unit",
        "strategy_name": "Unit",
        "expectancy": "0.50",
        "total_trades": 70,
        "profit_factor": "1.80",
        "max_drawdown": "0.020",
        "win_rate": "0.6500",
        "proof_score": "100.00",
    }
    raw.update(overrides)
    return ExpectancyStrengthInput.from_mapping(raw)


def test_mixed_sample_routes_strong() -> None:
    result = route_expectancy_strength(build_sample_mixed_expectancy_input())

    assert result.expectancy_status == EXPECTANCY_STRONG
    assert result.strategy_id == "supertrend"


def test_all_blocked_sample_routes_blocked() -> None:
    result = route_expectancy_strength(build_sample_blocked_expectancy_input())

    assert result.expectancy_status == EXPECTANCY_BLOCKED


def test_promising_expectancy_classification() -> None:
    result = route_expectancy_strength(
        sample_input(expectancy="0.25", total_trades=35, profit_factor="1.30", max_drawdown="0.030")
    )

    assert result.expectancy_status == EXPECTANCY_PROMISING


def test_weak_expectancy_classification() -> None:
    result = route_expectancy_strength(
        sample_input(expectancy="0.10", total_trades=12, profit_factor="1.10", max_drawdown="0.030")
    )

    assert result.expectancy_status == EXPECTANCY_WEAK


def test_unknown_expectancy_classification() -> None:
    result = route_expectancy_strength(sample_input(expectancy=None))

    assert result.expectancy_status == EXPECTANCY_UNKNOWN


def test_negative_expectancy_blocks() -> None:
    result = route_expectancy_strength(sample_input(expectancy="-0.01"))

    assert result.expectancy_status == EXPECTANCY_BLOCKED
    assert "EXPECTANCY_BLOCKED" in result.blockers


def test_sample_depth_check_fails_when_low() -> None:
    result = route_expectancy_strength(sample_input(total_trades=10))

    assert "sample_depth_minimum" in result.failed_checks


def test_profit_factor_check_fails_when_low() -> None:
    result = route_expectancy_strength(sample_input(profit_factor="1.10"))

    assert "profit_factor_minimum" in result.failed_checks


def test_drawdown_check_fails_when_high() -> None:
    result = route_expectancy_strength(sample_input(max_drawdown="0.080"))

    assert "drawdown_acceptable" in result.failed_checks


def test_real_money_allowed_false() -> None:
    assert route_expectancy_strength().real_money_allowed is False


def test_compounding_allowed_false() -> None:
    assert route_expectancy_strength().compounding_allowed is False


def test_broker_action_allowed_false() -> None:
    assert route_expectancy_strength().broker_action_allowed is False


def test_bank_movement_allowed_false() -> None:
    assert route_expectancy_strength().bank_movement_allowed is False


def test_demo_trade_allowed_false() -> None:
    assert route_expectancy_strength().demo_trade_allowed is False


def test_json_output_valid() -> None:
    parsed = result_to_jsonable_dict(route_expectancy_strength())

    assert parsed["expectancy_status"] == EXPECTANCY_STRONG
    assert parsed["permissions"]["real_money_allowed"] is False


def test_markdown_output_valid() -> None:
    markdown = expectancy_strength_to_markdown(route_expectancy_strength())

    assert "# AIOS Forex Expectancy Strength Router V1" in markdown
    assert "## Safety Locks" in markdown


def test_runner_json_valid() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["expectancy_status"] == EXPECTANCY_STRONG


def test_runner_markdown_valid() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--markdown"], stdout=stdout)

    assert exit_code == 0
    assert "# AIOS Forex Expectancy Strength Router V1" in stdout.getvalue()


def test_deterministic_json() -> None:
    left = json.dumps(result_to_jsonable_dict(route_expectancy_strength()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(route_expectancy_strength()), sort_keys=True)

    assert left == right


def test_money_path_signal_is_surfaced() -> None:
    result = route_expectancy_strength()

    assert result.money_path_signal == "MONEY_PATH_STRONGER_FOR_PROOF_REVIEW_ONLY"


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(router))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.lower() for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module.lower())

    forbidden_fragments = (
        "oanda",
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "dotenv",
        "credential",
        "secret",
    )
    assert not any(
        fragment in module_name
        for module_name in imported
        for fragment in forbidden_fragments
    )
