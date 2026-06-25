from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.loss_to_next_profit_candidate_gate_v1 import (  # noqa: E402
    NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE,
    NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW,
    NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE,
    NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN,
    NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS,
    NEXT_PROFIT_CANDIDATE_REVIEW_READY,
    LossReviewConfig,
    LossToNextProfitCandidateInput,
    NextProfitCandidateEvidence,
    Trade334LossEvidence,
    build_sample_trade_334_input,
    evaluate_loss_to_next_profit_candidate_gate,
)
from scripts.forex_delivery.run_loss_to_next_profit_candidate_gate_v1 import (  # noqa: E402
    main,
)


def reviewed_trade_334() -> Trade334LossEvidence:
    return Trade334LossEvidence(
        trade_id=334,
        close_reason="STOP_LOSS_ORDER",
        realized_pl_total=Decimal("-0.0010"),
        pl_capture_classification="FILLED_TRADE_PL_NEGATIVE",
        profit_claimed=False,
        stop_loss_used=True,
        take_profit_order_cancelled_after_stop=True,
        open_trade_count=0,
        open_position_count=0,
        pending_order_count=0,
        loss_acknowledged=True,
        loss_review_completed=True,
    )


def strong_candidate() -> NextProfitCandidateEvidence:
    return NextProfitCandidateEvidence(
        candidate_id="CANDIDATE-DEMO-EURUSD-001",
        strategy_name="mean_reversion_demo",
        symbol="EUR_USD",
        direction="LONG",
        total_trades=30,
        wins=19,
        losses=11,
        expectancy=Decimal("0.0012"),
        profit_factor=Decimal("1.70"),
        max_drawdown=Decimal("0.0200"),
        consecutive_losses=2,
        walk_forward_gate_cleared=True,
        sample_depth_sufficient=True,
        risk_controls_present=True,
        stop_loss_required=True,
        take_profit_required=True,
        kill_switch_clear=True,
        daily_loss_limit_clear=True,
    )


def strong_input() -> LossToNextProfitCandidateInput:
    return LossToNextProfitCandidateInput(
        trade_334_loss=reviewed_trade_334(),
        candidate=strong_candidate(),
        config=LossReviewConfig(
            minimum_sample_size=20,
            minimum_profit_factor=Decimal("1.25"),
            maximum_drawdown_allowed=Decimal("0.05"),
            maximum_consecutive_losses_allowed=3,
        ),
        next_demo_trade_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        owner_approval_required=True,
        broker_action_allowed=False,
        live_trading_allowed=False,
    )


def test_sample_trade_334_returns_loss_review() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(build_sample_trade_334_input())

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW


def test_sample_trade_334_blocks_next_demo_trade() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(build_sample_trade_334_input())

    assert result.next_demo_trade_allowed is False


def test_sample_trade_334_blocks_real_money() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(build_sample_trade_334_input())

    assert result.real_money_allowed is False


def test_sample_trade_334_blocks_compounding() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(build_sample_trade_334_input())

    assert result.compounding_allowed is False


def test_sample_trade_334_keeps_broker_action_false() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(build_sample_trade_334_input())

    assert result.broker_action_allowed is False


def test_sample_trade_334_keeps_live_trading_false() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(build_sample_trade_334_input())

    assert result.live_trading_allowed is False


def test_missing_candidate_blocks_review() -> None:
    gate_input = replace(strong_input(), candidate=replace(strong_candidate(), candidate_id="NONE"))

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_NO_CANDIDATE


def test_negative_expectancy_blocks_review() -> None:
    gate_input = replace(
        strong_input(),
        candidate=replace(strong_candidate(), expectancy=Decimal("-0.0001")),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN


def test_insufficient_sample_blocks_review() -> None:
    gate_input = replace(
        strong_input(),
        candidate=replace(
            strong_candidate(),
            total_trades=5,
            sample_depth_sufficient=False,
        ),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_INSUFFICIENT_SAMPLE


def test_low_profit_factor_blocks_review() -> None:
    gate_input = replace(
        strong_input(),
        candidate=replace(strong_candidate(), profit_factor=Decimal("1.10")),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_PROFIT_NOT_PROVEN


def test_excessive_drawdown_blocks_review() -> None:
    gate_input = replace(
        strong_input(),
        candidate=replace(strong_candidate(), max_drawdown=Decimal("0.0600")),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS


def test_uncleared_walk_forward_blocks_review() -> None:
    gate_input = replace(
        strong_input(),
        candidate=replace(strong_candidate(), walk_forward_gate_cleared=False),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS


def test_missing_risk_controls_block_review() -> None:
    gate_input = replace(
        strong_input(),
        candidate=replace(strong_candidate(), risk_controls_present=False),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_RISK_LIMITS


def test_open_exposure_blocks_review() -> None:
    gate_input = replace(
        strong_input(),
        trade_334_loss=replace(reviewed_trade_334(), open_trade_count=1),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW


def test_pending_orders_block_review() -> None:
    gate_input = replace(
        strong_input(),
        trade_334_loss=replace(reviewed_trade_334(), pending_order_count=1),
    )

    result = evaluate_loss_to_next_profit_candidate_gate(gate_input)

    assert result.classification == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW


def test_strong_synthetic_candidate_can_reach_review_ready_without_real_money() -> None:
    result = evaluate_loss_to_next_profit_candidate_gate(strong_input())

    assert result.classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY
    assert result.real_money_allowed is False
    assert result.compounding_allowed is False
    assert result.broker_action_allowed is False
    assert result.live_trading_allowed is False


def test_operator_text_contains_required_terms() -> None:
    stdout = io.StringIO()
    exit_code = main(["--sample-trade-334"], stdout=stdout)
    output = stdout.getvalue()

    assert exit_code == 0
    assert "Trade 334" in output
    assert "loss review" in output
    assert "profit is not proven" in output
    assert "No next trade" in output


def test_json_output_contains_required_sections() -> None:
    stdout = io.StringIO()
    exit_code = main(["--sample-trade-334", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["classification"] == NEXT_PROFIT_CANDIDATE_BLOCKED_LOSS_REVIEW
    assert "blockers" in parsed
    assert "candidate_metrics" in parsed
    assert "permissions" in parsed
    assert "next_safe_action" in parsed
