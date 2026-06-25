from __future__ import annotations

from decimal import Decimal
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.review_ready_candidate_selector_v1 import (  # noqa: E402
    REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY,
    REVIEW_READY_CANDIDATE_SELECTED,
    ReviewReadyCandidateSelectorInput,
    build_sample_all_blocked_selector_input,
    build_sample_mixed_selector_input,
    result_to_operator_text,
    select_review_ready_candidate,
)
from scripts.forex_delivery.run_review_ready_candidate_selector_v1 import (  # noqa: E402
    main,
)


def all_blocked_result():
    return select_review_ready_candidate(build_sample_all_blocked_selector_input())


def mixed_result():
    return select_review_ready_candidate(build_sample_mixed_selector_input())


def review_ready_candidate(
    candidate_id: str,
    *,
    expectancy: str = "0.50",
    profit_factor: str = "1.50",
    max_drawdown: str = "0.020",
    total_trades: int = 25,
    wins: int = 15,
    losses: int = 10,
) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "strategy_name": "paper_long_run_supervisor_v2",
        "symbol": "EUR_USD",
        "direction": "LONG",
        "timeframe": "DEMO_REVIEW",
        "evidence_source": f"synthetic_{candidate_id}",
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "realized_pl_total": "10.00",
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown": max_drawdown,
        "consecutive_losses": 2,
        "average_win": "1.20",
        "average_loss": "-0.75",
        "sample_depth_sufficient": True,
        "walk_forward_gate_cleared": True,
        "risk_controls_present": True,
        "stop_loss_required": True,
        "take_profit_required": True,
        "kill_switch_clear": True,
        "daily_loss_limit_clear": True,
    }


def select_from_candidates(*candidates: dict[str, object]):
    return select_review_ready_candidate(
        ReviewReadyCandidateSelectorInput(candidate_evidence_records=candidates)
    )


def test_all_blocked_sample_returns_blocked_none_ready() -> None:
    result = all_blocked_result()

    assert result.classification == REVIEW_READY_CANDIDATE_BLOCKED_NONE_READY


def test_all_blocked_sample_selects_no_candidate() -> None:
    result = all_blocked_result()

    assert result.selected_candidate is None
    assert result.selected_candidate_id == "NONE"


def test_all_blocked_sample_blocks_candidate_review() -> None:
    result = all_blocked_result()

    assert result.candidate_review_allowed is False


def test_all_blocked_sample_blocks_next_demo_trade() -> None:
    result = all_blocked_result()

    assert result.next_demo_trade_allowed is False


def test_all_blocked_sample_blocks_real_money() -> None:
    result = all_blocked_result()

    assert result.real_money_allowed is False


def test_all_blocked_sample_blocks_compounding() -> None:
    result = all_blocked_result()

    assert result.compounding_allowed is False


def test_all_blocked_sample_keeps_broker_action_allowed_false() -> None:
    result = all_blocked_result()

    assert result.broker_action_allowed is False


def test_all_blocked_sample_keeps_live_trading_allowed_false() -> None:
    result = all_blocked_result()

    assert result.live_trading_allowed is False


def test_mixed_sample_returns_selected() -> None:
    result = mixed_result()

    assert result.classification == REVIEW_READY_CANDIDATE_SELECTED


def test_mixed_sample_selects_stronger_candidate() -> None:
    result = mixed_result()

    assert result.selected_candidate_id == "c2-eur-buy-stronger-review-ready"


def test_mixed_sample_includes_at_least_two_blocked_candidate_records() -> None:
    result = mixed_result()

    blocked_records = [record for record in result.candidate_records if not record.review_ready]
    assert len(blocked_records) >= 2


def test_mixed_sample_includes_at_least_two_review_ready_candidate_records() -> None:
    result = mixed_result()

    assert len(result.rankings) >= 2


def test_selected_candidate_has_highest_deterministic_score() -> None:
    result = mixed_result()
    selected = result.selected_candidate

    assert selected is not None
    assert selected.score == max(record.score for record in result.rankings)


def test_tie_breaker_prefers_higher_expectancy() -> None:
    result = select_from_candidates(
        review_ready_candidate(
            "higher-expectancy",
            expectancy="0.60",
            profit_factor="1.50",
            total_trades=20,
            wins=12,
            losses=8,
        ),
        review_ready_candidate(
            "lower-expectancy",
            expectancy="0.50",
            profit_factor="1.50",
            total_trades=30,
            wins=18,
            losses=12,
        ),
    )

    assert result.rankings[0].score == result.rankings[1].score
    assert result.selected_candidate_id == "higher-expectancy"


def test_tie_breaker_prefers_higher_profit_factor_when_expectancy_ties() -> None:
    result = select_from_candidates(
        review_ready_candidate(
            "higher-profit-factor",
            expectancy="0.50",
            profit_factor="1.70",
            total_trades=20,
            wins=12,
            losses=8,
        ),
        review_ready_candidate(
            "lower-profit-factor",
            expectancy="0.50",
            profit_factor="1.50",
            total_trades=30,
            wins=18,
            losses=12,
        ),
    )

    assert result.rankings[0].score == result.rankings[1].score
    assert result.selected_candidate_id == "higher-profit-factor"


def test_tie_breaker_prefers_lower_drawdown_when_expectancy_and_profit_factor_tie() -> None:
    result = select_from_candidates(
        review_ready_candidate(
            "lower-drawdown",
            expectancy="0.50",
            profit_factor="1.50",
            max_drawdown="0.010",
            total_trades=20,
            wins=12,
            losses=8,
        ),
        review_ready_candidate(
            "higher-drawdown",
            expectancy="0.50",
            profit_factor="1.50",
            max_drawdown="0.020",
            total_trades=30,
            wins=18,
            losses=12,
        ),
    )

    assert result.rankings[0].score == result.rankings[1].score
    assert result.selected_candidate_id == "lower-drawdown"


def test_tie_breaker_prefers_lexicographic_candidate_id_when_numeric_values_tie() -> None:
    result = select_from_candidates(
        review_ready_candidate("b-candidate"),
        review_ready_candidate("a-candidate"),
    )

    assert result.rankings[0].score == result.rankings[1].score
    assert result.selected_candidate_id == "a-candidate"


def test_selected_candidate_allows_candidate_review_true() -> None:
    result = mixed_result()

    assert result.candidate_review_allowed is True


def test_selected_candidate_still_keeps_next_demo_trade_false() -> None:
    result = mixed_result()

    assert result.next_demo_trade_allowed is False


def test_selected_candidate_still_keeps_real_money_false() -> None:
    result = mixed_result()

    assert result.real_money_allowed is False


def test_selected_candidate_still_keeps_compounding_false() -> None:
    result = mixed_result()

    assert result.compounding_allowed is False


def test_selected_candidate_still_keeps_broker_action_false() -> None:
    result = mixed_result()

    assert result.broker_action_allowed is False


def test_selected_candidate_still_keeps_live_trading_false() -> None:
    result = mixed_result()

    assert result.live_trading_allowed is False


def test_operator_text_for_all_blocked_contains_required_terms() -> None:
    text = result_to_operator_text(all_blocked_result())

    assert "No review-ready Forex candidate is selected" in text
    assert "No next demo trade" in text


def test_operator_text_for_mixed_contains_required_terms() -> None:
    text = result_to_operator_text(mixed_result())

    assert "c2-eur-buy-stronger-review-ready" in text
    assert "review-ready only" in text


def test_json_output_contains_required_sections() -> None:
    stdout = io.StringIO()
    exit_code = main(["--sample-mixed", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["selector_classification"] == REVIEW_READY_CANDIDATE_SELECTED
    assert "selected_candidate" in parsed
    assert "rankings" in parsed
    assert "candidate_records" in parsed
    assert "permissions" in parsed
    assert "blockers" in parsed
    assert "next_safe_action" in parsed
