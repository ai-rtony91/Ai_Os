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

import automation.forex_engine.strategy_proof_engine_v1 as engine  # noqa: E402
from automation.forex_engine.strategy_proof_engine_v1 import (  # noqa: E402
    REQUIRED_STRATEGY_OUTPUT_FIELDS,
    STRATEGY_RECOMMENDATION_IMPROVE,
    STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY,
    STRATEGY_RECOMMENDATION_REJECT,
    StrategySeedEvidence,
    build_sample_all_blocked_strategy_evidence,
    build_sample_mixed_strategy_evidence,
    build_strategy_seed_catalog,
    evaluate_strategy_proof_candidate,
    evaluate_strategy_proof_engine,
    result_to_jsonable_dict,
    strategy_proof_to_markdown,
)
from scripts.forex_delivery.run_strategy_proof_engine_v1 import main  # noqa: E402


def custom_strategy(**overrides):
    raw = {
        "strategy_id": "unit_test_strategy",
        "strategy_name": "Unit Test Strategy",
        "total_trades": 40,
        "wins": 26,
        "losses": 14,
        "realized_pl": "20.00",
        "expectancy": "0.50",
        "profit_factor": "1.70",
        "max_drawdown": "0.020",
        "consecutive_losses": 2,
        "walk_forward_passed": True,
        "out_of_sample_passed": True,
        "market_regime_coverage": 4,
        "spread_sensitivity_passed": True,
        "slippage_sensitivity_passed": True,
        "latency_sensitivity_passed": True,
        "risk_controls_present": True,
    }
    raw.update(overrides)
    return StrategySeedEvidence.from_mapping(raw)


def test_supertrend_exists_in_seed_catalog() -> None:
    assert any(seed["strategy_id"] == "supertrend" for seed in build_strategy_seed_catalog())


def test_all_ten_strategy_seeds_exist() -> None:
    seed_ids = {seed["strategy_id"] for seed in build_strategy_seed_catalog()}

    assert seed_ids == {
        "supertrend",
        "ema_crossover",
        "vwap_bias",
        "donchian_breakout",
        "atr_trend_filter",
        "adx_trend_filter",
        "rsi_mean_reversion",
        "macd_confirmation",
        "market_structure_break",
        "multi_timeframe_alignment",
    }


def test_mixed_sample_contains_all_ten_strategy_records() -> None:
    assert len(build_sample_mixed_strategy_evidence()) == 10


def test_all_blocked_sample_contains_all_ten_strategy_records() -> None:
    assert len(build_sample_all_blocked_strategy_evidence()) == 10


def test_strategies_rank_deterministically() -> None:
    left = [candidate.strategy_id for candidate in evaluate_strategy_proof_engine().strategy_results]
    right = [candidate.strategy_id for candidate in evaluate_strategy_proof_engine().strategy_results]

    assert left == right


def test_top_strategy_has_positive_expectancy_in_mixed_sample() -> None:
    result = evaluate_strategy_proof_engine()

    assert result.top_strategy is not None
    assert result.top_strategy.expectancy > 0


def test_top_strategy_has_positive_profit_factor_in_mixed_sample() -> None:
    result = evaluate_strategy_proof_engine()

    assert result.top_strategy is not None
    assert result.top_strategy.profit_factor > 1


def test_supertrend_is_top_mixed_candidate() -> None:
    result = evaluate_strategy_proof_engine()

    assert result.top_strategy is not None
    assert result.top_strategy.strategy_id == "supertrend"


def test_bad_strategies_are_blocked_in_all_blocked_sample() -> None:
    result = evaluate_strategy_proof_engine(build_sample_all_blocked_strategy_evidence())

    assert all(candidate.recommendation == STRATEGY_RECOMMENDATION_REJECT for candidate in result.strategy_results)


def test_negative_expectancy_is_rejected() -> None:
    result = evaluate_strategy_proof_candidate(custom_strategy(expectancy="-0.01"))

    assert result.recommendation == STRATEGY_RECOMMENDATION_REJECT
    assert "expectancy is not positive" in result.blockers


def test_low_profit_factor_is_improve_or_reject() -> None:
    result = evaluate_strategy_proof_candidate(custom_strategy(profit_factor="1.10"))

    assert result.recommendation in {
        STRATEGY_RECOMMENDATION_IMPROVE,
        STRATEGY_RECOMMENDATION_REJECT,
    }
    assert any("profit factor" in blocker for blocker in result.blockers)


def test_high_drawdown_is_blocked() -> None:
    result = evaluate_strategy_proof_candidate(custom_strategy(max_drawdown="0.090"))

    assert result.recommendation == STRATEGY_RECOMMENDATION_REJECT
    assert any("drawdown" in blocker for blocker in result.blockers)


def test_insufficient_sample_is_blocked() -> None:
    result = evaluate_strategy_proof_candidate(custom_strategy(total_trades=10, wins=6, losses=4))

    assert result.recommendation == STRATEGY_RECOMMENDATION_IMPROVE
    assert any("sample depth" in blocker for blocker in result.blockers)


def test_supertrend_status_is_reported() -> None:
    status = evaluate_strategy_proof_engine().supertrend_status

    assert status["strategy_id"] == "supertrend"
    assert status["status"] == "SUPER_TREND_PROOF_REVIEW_READY"


def test_supertrend_improvement_reason_is_reported() -> None:
    status = evaluate_strategy_proof_engine().supertrend_status

    assert status["improvement_reason"]


def test_real_money_allowed_false() -> None:
    assert evaluate_strategy_proof_engine().real_money_allowed is False


def test_compounding_allowed_false() -> None:
    assert evaluate_strategy_proof_engine().compounding_allowed is False


def test_broker_action_allowed_false() -> None:
    assert evaluate_strategy_proof_engine().broker_action_allowed is False


def test_bank_movement_allowed_false() -> None:
    assert evaluate_strategy_proof_engine().bank_movement_allowed is False


def test_demo_trade_allowed_false() -> None:
    assert evaluate_strategy_proof_engine().demo_trade_allowed is False


def test_live_trading_allowed_false() -> None:
    assert evaluate_strategy_proof_engine().live_trading_allowed is False


def test_json_output_contains_required_keys() -> None:
    parsed = result_to_jsonable_dict(evaluate_strategy_proof_engine())

    for key in (
        "top_strategy",
        "supertrend_status",
        "top_expectancy",
        "top_profit_factor",
        "safest_candidate",
        "fastest_candidate_to_prove",
        "strategies_to_improve",
        "strategies_to_reject",
        "permissions",
    ):
        assert key in parsed


def test_every_strategy_output_contains_required_fields() -> None:
    parsed = result_to_jsonable_dict(evaluate_strategy_proof_engine())

    for candidate in parsed["strategy_results"]:
        for field in REQUIRED_STRATEGY_OUTPUT_FIELDS:
            assert field in candidate


def test_runner_json_emits_valid_json() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["top_strategy"]["strategy_id"] == "supertrend"


def test_markdown_output_contains_title_and_rankings() -> None:
    markdown = strategy_proof_to_markdown(evaluate_strategy_proof_engine())

    assert "# AIOS Forex Strategy Proof Engine V1" in markdown
    assert "## Rankings" in markdown


def test_runner_markdown_emits_markdown() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-mixed", "--markdown"], stdout=stdout)

    assert exit_code == 0
    assert "# AIOS Forex Strategy Proof Engine V1" in stdout.getvalue()


def test_runner_all_blocked_operator_text_contains_locks() -> None:
    stdout = io.StringIO()

    exit_code = main(["--sample-all-blocked"], stdout=stdout)

    assert exit_code == 0
    assert "real_money_allowed: false" in stdout.getvalue()


def test_json_output_is_deterministic() -> None:
    left = json.dumps(result_to_jsonable_dict(evaluate_strategy_proof_engine()), sort_keys=True)
    right = json.dumps(result_to_jsonable_dict(evaluate_strategy_proof_engine()), sort_keys=True)

    assert left == right


def test_safest_candidate_is_surfaced() -> None:
    assert evaluate_strategy_proof_engine().safest_candidate is not None


def test_fastest_candidate_to_prove_is_surfaced() -> None:
    assert evaluate_strategy_proof_engine().fastest_candidate_to_prove is not None


def test_strategy_lists_to_improve_and_reject_are_surfaced() -> None:
    result = evaluate_strategy_proof_engine()

    assert result.strategies_to_improve
    assert result.strategies_to_reject


def test_proof_review_candidate_recommendation_is_present() -> None:
    result = evaluate_strategy_proof_engine()

    assert any(
        candidate.recommendation == STRATEGY_RECOMMENDATION_PROOF_REVIEW_READY
        for candidate in result.strategy_results
    )


def test_module_imports_no_forbidden_runtime_modules() -> None:
    tree = ast.parse(inspect.getsource(engine))
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
