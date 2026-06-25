from __future__ import annotations

import io
import json
from decimal import Decimal
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.profit_validation_loop_v1 import (  # noqa: E402
    PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED,
    PROFIT_VALIDATION_BLOCKED_DRAWDOWN,
    PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE,
    PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW,
    PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY,
    PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE,
    PROFIT_VALIDATION_PASS,
    ProfitValidationConfig,
    ProfitValidationInput,
    TradeEvidence,
    build_sample_trade_334_input,
    evaluate_profit_validation_loop,
    result_to_jsonable_dict,
)
from scripts.forex_delivery.run_profit_validation_loop_v1 import main  # noqa: E402


def strong_profitable_input() -> ProfitValidationInput:
    return ProfitValidationInput(
        config=ProfitValidationConfig(
            minimum_sample_size=20,
            minimum_profit_factor=Decimal("1.25"),
            maximum_drawdown_allowed=Decimal("0.05"),
            maximum_consecutive_losses_allowed=3,
        ),
        evidence=TradeEvidence(
            total_trades=30,
            wins=18,
            losses=12,
            realized_pl_total=Decimal("0.0180"),
            average_win=Decimal("0.0020"),
            average_loss=Decimal("0.0010"),
            max_drawdown=Decimal("0.0200"),
            consecutive_losses=2,
            open_trades=0,
            open_positions=0,
            pending_orders=0,
            stop_loss_present=True,
            take_profit_present=True,
            daily_loss_limit_clear=True,
            kill_switch_clear=True,
            owner_approval_required=True,
            owner_approved=False,
            live_trading_allowed=False,
            compounding_requested=True,
        ),
    )


def test_sample_trade_334_returns_loss_review() -> None:
    result = evaluate_profit_validation_loop(build_sample_trade_334_input())

    assert result.classification == PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW


def test_sample_trade_334_never_allows_real_money() -> None:
    result = evaluate_profit_validation_loop(build_sample_trade_334_input())

    assert result.real_money_allowed is False


def test_sample_trade_334_never_allows_next_trade() -> None:
    result = evaluate_profit_validation_loop(build_sample_trade_334_input())

    assert result.next_trade_allowed is False


def test_sample_trade_334_never_allows_compounding() -> None:
    result = evaluate_profit_validation_loop(build_sample_trade_334_input())

    assert result.compounding_allowed is False


def test_negative_realized_pl_blocks_profit_validation() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    negative = TradeEvidence(
        **{
            **evidence.__dict__,
            "realized_pl_total": Decimal("-0.0001"),
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=negative, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW
    assert result.profitability_proven is False


def test_insufficient_sample_size_blocks_profit_validation() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    small_sample = TradeEvidence(
        **{
            **evidence.__dict__,
            "total_trades": 5,
            "wins": 3,
            "losses": 2,
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=small_sample, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_INSUFFICIENT_SAMPLE
    assert result.compounding_allowed is False


def test_profit_factor_below_minimum_blocks_compounding() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    weak_factor = TradeEvidence(
        **{
            **evidence.__dict__,
            "wins": 15,
            "losses": 15,
            "average_win": Decimal("0.0011"),
            "average_loss": Decimal("0.0010"),
            "realized_pl_total": Decimal("0.0015"),
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=weak_factor, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_COMPOUNDING_NOT_ALLOWED
    assert result.compounding_allowed is False


def test_drawdown_above_maximum_blocks_compounding() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    high_drawdown = TradeEvidence(
        **{
            **evidence.__dict__,
            "max_drawdown": Decimal("0.0600"),
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=high_drawdown, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_DRAWDOWN
    assert result.compounding_allowed is False


def test_open_exposure_blocks_compounding() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    open_exposure = TradeEvidence(
        **{
            **evidence.__dict__,
            "open_trades": 1,
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=open_exposure, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE
    assert result.compounding_allowed is False


def test_pending_orders_block_compounding() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    pending = TradeEvidence(
        **{
            **evidence.__dict__,
            "pending_orders": 1,
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=pending, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE
    assert result.compounding_allowed is False


def test_kill_switch_failure_blocks_compounding() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    blocked = TradeEvidence(
        **{
            **evidence.__dict__,
            "kill_switch_clear": False,
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=blocked, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE
    assert result.compounding_allowed is False


def test_daily_loss_limit_failure_blocks_compounding() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    blocked = TradeEvidence(
        **{
            **evidence.__dict__,
            "daily_loss_limit_clear": False,
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(evidence=blocked, config=validation_input.config)
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_RISK_CONTROL_FAILURE
    assert result.compounding_allowed is False


def test_operator_answer_contains_required_trade_334_terms() -> None:
    result = evaluate_profit_validation_loop(build_sample_trade_334_input())
    answer = result.operator_answer

    assert "Trade 334" in answer
    assert "stop loss" in answer
    assert "negative realized P/L" in answer
    assert "not proven" in answer


def test_json_output_contains_required_sections() -> None:
    stdout = io.StringIO()
    exit_code = main(["--sample-trade-334", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["classification"] == PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW
    assert "blockers" in parsed
    assert "metrics" in parsed
    assert "permissions" in parsed
    assert "next_safe_action" in parsed


def test_result_to_jsonable_dict_contains_required_sections() -> None:
    result = evaluate_profit_validation_loop(build_sample_trade_334_input())
    parsed = result_to_jsonable_dict(result)

    assert parsed["classification"] == PROFIT_VALIDATION_BLOCKED_LOSS_REVIEW
    assert "blockers" in parsed
    assert "metrics" in parsed
    assert "permissions" in parsed
    assert "next_safe_action" in parsed


def test_strong_profitable_demo_sample_can_pass_without_real_money() -> None:
    result = evaluate_profit_validation_loop(strong_profitable_input())

    assert result.classification == PROFIT_VALIDATION_PASS
    assert result.profitability_proven is True
    assert result.compounding_allowed is True
    assert result.real_money_allowed is False
    assert result.permissions["live_trading_allowed"] is False
    assert result.permissions["owner_approved"] is False


def test_negative_expectancy_blocks_profit_validation() -> None:
    validation_input = strong_profitable_input()
    evidence = validation_input.evidence
    negative_expectancy = TradeEvidence(
        **{
            **evidence.__dict__,
            "wins": 10,
            "losses": 20,
            "average_win": Decimal("0.0010"),
            "average_loss": Decimal("0.0020"),
            "realized_pl_total": Decimal("0.0010"),
        }
    )

    result = evaluate_profit_validation_loop(
        ProfitValidationInput(
            evidence=negative_expectancy,
            config=validation_input.config,
        )
    )

    assert result.classification == PROFIT_VALIDATION_BLOCKED_NEGATIVE_EXPECTANCY
