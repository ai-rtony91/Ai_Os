from __future__ import annotations

from decimal import Decimal
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.candidate_evidence_intake_v1 import (  # noqa: E402
    CANDIDATE_EVIDENCE_REVIEW_READY,
)
from automation.forex_engine.candidate_to_gate_bridge_v1 import (  # noqa: E402
    CANDIDATE_TO_GATE_BLOCKED_INTAKE,
    CANDIDATE_TO_GATE_REVIEW_READY,
    bridge_candidate_evidence_to_gate,
    build_sample_incomplete_bridge_input,
    build_sample_review_ready_bridge_input,
    result_to_operator_text,
)
from automation.forex_engine.loss_to_next_profit_candidate_gate_v1 import (  # noqa: E402
    NEXT_PROFIT_CANDIDATE_REVIEW_READY,
)
from scripts.forex_delivery.run_candidate_to_gate_bridge_v1 import main  # noqa: E402


def incomplete_result():
    return bridge_candidate_evidence_to_gate(build_sample_incomplete_bridge_input())


def review_ready_result():
    return bridge_candidate_evidence_to_gate(build_sample_review_ready_bridge_input())


def test_incomplete_sample_returns_blocked_intake() -> None:
    result = incomplete_result()

    assert result.classification == CANDIDATE_TO_GATE_BLOCKED_INTAKE


def test_incomplete_sample_does_not_call_successful_gate_review_path() -> None:
    result = incomplete_result()

    assert result.gate_result is None
    assert result.gate_classification != NEXT_PROFIT_CANDIDATE_REVIEW_READY


def test_incomplete_sample_blocks_candidate_review() -> None:
    result = incomplete_result()

    assert result.candidate_review_allowed is False


def test_incomplete_sample_blocks_next_demo_trade() -> None:
    result = incomplete_result()

    assert result.next_demo_trade_allowed is False


def test_incomplete_sample_blocks_real_money() -> None:
    result = incomplete_result()

    assert result.real_money_allowed is False


def test_incomplete_sample_blocks_compounding() -> None:
    result = incomplete_result()

    assert result.compounding_allowed is False


def test_incomplete_sample_keeps_broker_action_allowed_false() -> None:
    result = incomplete_result()

    assert result.broker_action_allowed is False


def test_incomplete_sample_keeps_live_trading_allowed_false() -> None:
    result = incomplete_result()

    assert result.live_trading_allowed is False


def test_review_ready_sample_returns_review_ready() -> None:
    result = review_ready_result()

    assert result.classification == CANDIDATE_TO_GATE_REVIEW_READY


def test_review_ready_sample_includes_intake_review_ready() -> None:
    result = review_ready_result()

    assert result.intake_classification == CANDIDATE_EVIDENCE_REVIEW_READY


def test_review_ready_sample_includes_gate_review_ready() -> None:
    result = review_ready_result()

    assert result.gate_classification == NEXT_PROFIT_CANDIDATE_REVIEW_READY


def test_review_ready_sample_allows_candidate_review() -> None:
    result = review_ready_result()

    assert result.candidate_review_allowed is True


def test_review_ready_sample_still_keeps_next_demo_trade_false() -> None:
    result = review_ready_result()

    assert result.next_demo_trade_allowed is False


def test_review_ready_sample_still_keeps_real_money_false() -> None:
    result = review_ready_result()

    assert result.real_money_allowed is False


def test_review_ready_sample_still_keeps_compounding_false() -> None:
    result = review_ready_result()

    assert result.compounding_allowed is False


def test_review_ready_sample_still_keeps_broker_action_false() -> None:
    result = review_ready_result()

    assert result.broker_action_allowed is False


def test_review_ready_sample_still_keeps_live_trading_false() -> None:
    result = review_ready_result()

    assert result.live_trading_allowed is False


def test_conversion_preserves_candidate_fields() -> None:
    result = review_ready_result()
    converted = result.converted_candidate

    assert converted is not None
    assert converted.candidate_id == "c1-eur-buy-review-ready"
    assert converted.strategy_name == "paper_long_run_supervisor_v2"
    assert converted.symbol == "EUR_USD"
    assert converted.direction == "LONG"
    assert converted.expectancy == Decimal("0.50")
    assert converted.profit_factor == Decimal("1.60")
    assert converted.max_drawdown == Decimal("0.025")
    assert converted.total_trades == 25
    assert converted.wins == 16
    assert converted.losses == 9


def test_operator_text_for_incomplete_sample_contains_required_terms() -> None:
    text = result_to_operator_text(incomplete_result())

    assert "intake blocked" in text
    assert "No next demo trade" in text


def test_operator_text_for_review_ready_contains_required_terms() -> None:
    text = result_to_operator_text(review_ready_result())

    assert "review-ready only" in text
    assert "broker action" in text


def test_json_output_contains_required_sections() -> None:
    stdout = io.StringIO()
    exit_code = main(["--sample-review-ready", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["bridge_classification"] == CANDIDATE_TO_GATE_REVIEW_READY
    assert "intake" in parsed
    assert "gate" in parsed
    assert "converted_candidate" in parsed
    assert "permissions" in parsed
    assert "blockers" in parsed
    assert "next_safe_action" in parsed
