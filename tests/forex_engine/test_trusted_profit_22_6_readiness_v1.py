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

import automation.forex_engine.trusted_profit_22_6_readiness_v1 as readiness  # noqa: E402
from automation.forex_engine.strategy_proof_engine_v1 import (  # noqa: E402
    StrategySeedEvidence,
    evaluate_strategy_proof_engine,
)
from automation.forex_engine.trusted_profit_22_6_readiness_v1 import (  # noqa: E402
    TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE,
    TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY,
    TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY,
    VALID_READINESS_CLASSIFICATIONS,
    build_sample_all_blocked_strategy_proof_result,
    build_sample_mixed_strategy_proof_result,
    evaluate_trusted_profit_22_6_readiness,
    readiness_to_markdown,
    result_to_jsonable_dict,
)
from scripts.forex_delivery.run_trusted_profit_22_6_readiness_v1 import (  # noqa: E402
    main,
)


def insufficient_supertrend_sample():
    return (
        StrategySeedEvidence.from_mapping(
            {
                "strategy_id": "supertrend",
                "strategy_name": "Supertrend",
                "total_trades": 12,
                "wins": 8,
                "losses": 4,
                "realized_pl": "6.00",
                "expectancy": "0.50",
                "profit_factor": "1.80",
                "max_drawdown": "0.020",
                "consecutive_losses": 2,
                "walk_forward_passed": True,
                "out_of_sample_passed": True,
                "market_regime_coverage": 3,
                "spread_sensitivity_passed": True,
                "slippage_sensitivity_passed": True,
                "latency_sensitivity_passed": True,
                "risk_controls_present": True,
            }
        ),
    )


def test_22_6_readiness_is_not_falsely_approved() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert result.enough_proof_for_22_6 is False
    assert result.readiness_status == TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY


def test_top_candidate_is_surfaced() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert result.strongest_candidate_id == "supertrend"
    assert result.strongest_candidate is not None


def test_missing_proof_is_surfaced() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert "minimum_22_6_observation_window" in result.missing_proof


def test_supertrend_status_is_surfaced() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert result.supertrend_status["strategy_id"] == "supertrend"


def test_supertrend_answer_splits_strategy_review_from_22_6_operation() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert result.supertrend_good_enough_for_strategy_review is True
    assert result.supertrend_good_enough_for_22_6_operation is False
    assert "not for 22/6 operation approval" in result.supertrend_answer


def test_more_proof_required_when_sample_is_insufficient() -> None:
    strategy_result = evaluate_strategy_proof_engine(insufficient_supertrend_sample())
    result = evaluate_trusted_profit_22_6_readiness(strategy_result)

    assert result.readiness_status == TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE


def test_all_blocked_sample_blocks_no_expectancy() -> None:
    result = evaluate_trusted_profit_22_6_readiness(
        build_sample_all_blocked_strategy_proof_result()
    )

    assert result.readiness_status == TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY


def test_real_money_allowed_false() -> None:
    assert evaluate_trusted_profit_22_6_readiness().real_money_allowed is False


def test_compounding_allowed_false() -> None:
    assert evaluate_trusted_profit_22_6_readiness().compounding_allowed is False


def test_broker_action_allowed_false() -> None:
    assert evaluate_trusted_profit_22_6_readiness().broker_action_allowed is False


def test_bank_movement_allowed_false() -> None:
    assert evaluate_trusted_profit_22_6_readiness().bank_movement_allowed is False


def test_live_trading_allowed_false() -> None:
    assert evaluate_trusted_profit_22_6_readiness().live_trading_allowed is False


def test_json_output_contains_required_keys() -> None:
    parsed = result_to_jsonable_dict(evaluate_trusted_profit_22_6_readiness())

    for key in (
        "readiness_status",
        "strategy_worth_proof_review",
        "enough_proof_for_22_6",
        "missing_proof",
        "strongest_candidate",
        "supertrend_status",
        "permissions",
    ):
        assert key in parsed


def test_runner_json_emits_valid_json() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["readiness_status"] == TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY


def test_markdown_output_contains_title_and_missing_proof() -> None:
    markdown = readiness_to_markdown(evaluate_trusted_profit_22_6_readiness())

    assert "# AIOS Forex Trusted Profit 22/6 Readiness V1" in markdown
    assert "## Missing Proof" in markdown


def test_runner_markdown_emits_markdown() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--markdown"], stdout=stdout)

    assert exit_code == 0
    assert "# AIOS Forex Trusted Profit 22/6 Readiness V1" in stdout.getvalue()


def test_deterministic_output() -> None:
    left = json.dumps(result_to_jsonable_dict(evaluate_trusted_profit_22_6_readiness()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(evaluate_trusted_profit_22_6_readiness()), sort_keys=True)

    assert left == right


def test_runner_all_blocked_output_contains_blocked_status() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-all-blocked"], stdout=stdout)

    assert exit_code == 0
    assert TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY in stdout.getvalue()


def test_strategy_worth_proof_review_true_for_mixed_sample() -> None:
    result = evaluate_trusted_profit_22_6_readiness(build_sample_mixed_strategy_proof_result())

    assert result.strategy_worth_proof_review is True


def test_enough_proof_false_because_missing_22_6_items() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert result.enough_proof_for_22_6 is False
    assert result.missing_proof


def test_fastest_safe_next_action_is_specific() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert "supertrend" in result.fastest_safe_next_action


def test_permissions_mapping_keeps_every_runtime_permission_false() -> None:
    permissions = evaluate_trusted_profit_22_6_readiness().permissions

    assert permissions == {
        "real_money_allowed": False,
        "compounding_allowed": False,
        "broker_action_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
    }


def test_all_required_classifications_are_exposed() -> None:
    assert {
        "TRUSTED_PROFIT_22_6_NOT_READY",
        "TRUSTED_PROFIT_22_6_MORE_PROOF_REQUIRED",
        "TRUSTED_PROFIT_22_6_STRATEGY_REVIEW_READY",
        "TRUSTED_PROFIT_22_6_BLOCKED_NO_STRATEGY",
        "TRUSTED_PROFIT_22_6_BLOCKED_NO_EXPECTANCY",
        "TRUSTED_PROFIT_22_6_BLOCKED_TOO_MUCH_DRAWDOWN",
        "TRUSTED_PROFIT_22_6_BLOCKED_INSUFFICIENT_SAMPLE",
        "TRUSTED_PROFIT_22_6_BLOCKED_REAL_MONEY",
        "TRUSTED_PROFIT_22_6_BLOCKED_COMPOUNDING",
    } <= VALID_READINESS_CLASSIFICATIONS


def test_operator_answer_does_not_claim_profit_guarantee() -> None:
    result = evaluate_trusted_profit_22_6_readiness()

    assert "not approved" in result.operator_answer


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(readiness))
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
