"""Tests for the read-only Big-Winner Watchtower 22H6D V1."""

from __future__ import annotations

import importlib
import inspect

from automation.forex_engine.big_winner_watchtower_22h6d_v1 import (
    MODE,
    SCHEMA,
    evaluate_big_winner_watchtower_22h6d_v1,
)


def _candidate(pair: str = "EURUSD", **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pair": pair,
        "direction": "long",
        "setup_type": "breakout continuation",
        "market_session": "London/New York overlap",
        "catalyst": "session expansion",
        "confidence_score": 88.0,
        "reward_risk_ratio": 4.2,
        "expected_r_multiple": 3.1,
        "upside_capture_score": 84.0,
        "expectancy_score": 78.0,
        "volatility_expansion_score": 76.0,
        "trend_alignment_score": 74.0,
        "liquidity_score": 86.0,
        "spread_score": 88.0,
        "slippage_score": 90.0,
        "drawdown_risk_score": 72.0,
        "evidence_quality_score": 84.0,
        "invalidation_quality_score": 82.0,
        "sample_size": 64,
        "recent_win_rate": 58.0,
        "max_drawdown_percent": 7.0,
        "spread_pips": 0.6,
        "slippage_pips": 0.2,
        "risk_percent": 0.6,
        "stop_loss_defined": True,
        "take_profit_defined": True,
        "invalidation_defined": True,
        "owner_approved_for_paper": False,
        "sizing_model": "fixed fractional capped risk",
    }
    payload.update(overrides)
    return payload


def _first_reasons(**overrides: object) -> list[str]:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(**overrides)]}
    )
    return result["ranked_opportunities"][0]["rejection_reasons"]


def test_output_is_read_only_and_paper_only() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate()]}
    )

    assert result["schema"] == SCHEMA
    assert result["mode"] == MODE
    assert result["read_only"] is True
    assert result["paper_only"] is True
    assert result["live_trading_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["auto_entry_allowed"] is False
    assert result["leverage_escalation_allowed"] is False
    assert result["owner_decision_required"] is True
    assert result["safety"]["read_only"] is True
    assert result["safety"]["paper_only"] is True
    assert result["safety"]["live_trading_allowed"] is False
    assert result["safety"]["broker_api_allowed"] is False
    assert result["safety"]["auto_entry_allowed"] is False
    assert result["safety"]["leverage_escalation_allowed"] is False


def test_watch_schedule_is_22h_6d_alert_only_without_runtime_creation() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1({"candidates": []})

    assert result["watch_schedule"] == {
        "status": "REVIEW_ONLY_22H_6D",
        "hours_per_day": 22,
        "days_per_week": 6,
        "alert_only": True,
        "execution_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
    }


def test_strong_asymmetric_candidate_qualifies_and_alerts_owner_review() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate()]}
    )

    top = result["top_opportunity"]
    assert top["pair"] == "EURUSD"
    assert top["big_winner_candidate"] is True
    assert top["rejection_reasons"] == []
    assert result["big_winner_candidate_count"] == 1
    assert result["alert_level"] == "BIG_WINNER_REVIEW"
    assert result["alert_queue"][0]["alert_type"] == "ASYMMETRIC_BIG_WINNER_CANDIDATE"
    assert result["alert_queue"][0]["review_only"] is True
    assert result["alert_queue"][0]["paper_only"] is True
    assert result["alert_queue"][0]["owner_decision_required"] is True
    assert result["alert_queue"][0]["execution_allowed"] is False


def test_ranked_opportunities_are_sorted_by_opportunity_score() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {
            "candidates": [
                _candidate("EURUSD", expectancy_score=70.0, evidence_quality_score=72.0),
                _candidate("GBPUSD", expectancy_score=88.0, evidence_quality_score=92.0),
                _candidate("USDJPY", expectancy_score=80.0, evidence_quality_score=84.0),
            ]
        }
    )

    scores = [
        candidate["opportunity_score"]
        for candidate in result["ranked_opportunities"]
    ]
    assert scores == sorted(scores, reverse=True)
    assert result["ranked_opportunities"][0]["pair"] == "GBPUSD"


def test_weak_reward_risk_is_rejected() -> None:
    reasons = _first_reasons(reward_risk_ratio=1.2, expected_r_multiple=1.0)
    assert "reward_risk_too_low" in reasons


def test_low_expectancy_is_rejected() -> None:
    assert "expectancy_too_low" in _first_reasons(expectancy_score=40.0)


def test_low_upside_capture_is_rejected() -> None:
    assert "upside_capture_too_low" in _first_reasons(upside_capture_score=40.0)


def test_low_volatility_expansion_is_rejected() -> None:
    assert "volatility_expansion_too_low" in _first_reasons(
        volatility_expansion_score=40.0
    )


def test_wide_spread_is_rejected() -> None:
    assert "spread_too_wide" in _first_reasons(spread_score=35.0)


def test_high_slippage_risk_is_rejected() -> None:
    assert "slippage_risk_too_high" in _first_reasons(slippage_score=35.0)


def test_excessive_drawdown_risk_is_rejected() -> None:
    assert "drawdown_risk_too_high" in _first_reasons(drawdown_risk_score=25.0)


def test_missing_stop_loss_is_rejected() -> None:
    assert "missing_stop_loss" in _first_reasons(stop_loss_defined=False)


def test_missing_take_profit_is_rejected() -> None:
    assert "missing_take_profit" in _first_reasons(take_profit_defined=False)


def test_missing_invalidation_is_rejected() -> None:
    assert "missing_invalidation" in _first_reasons(invalidation_defined=False)


def test_insufficient_sample_size_is_rejected() -> None:
    assert "insufficient_sample_size" in _first_reasons(sample_size=8)


def test_risk_percent_above_cap_is_rejected() -> None:
    assert "risk_percent_above_cap" in _first_reasons(risk_percent=1.25)


def test_martingale_is_rejected() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(is_martingale=True)]}
    )

    reasons = result["ranked_opportunities"][0]["rejection_reasons"]
    assert "martingale_detected" in reasons
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"


def test_revenge_trade_is_rejected() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(is_revenge=True)]}
    )

    reasons = result["ranked_opportunities"][0]["rejection_reasons"]
    assert "revenge_trade_detected" in reasons
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"


def test_live_execution_request_is_rejected() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(request_live_execution=True)]}
    )

    assert "live_execution_requested" in result["rejection_reasons"]
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"


def test_broker_api_request_is_rejected() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(request_broker_api=True)]}
    )

    assert "broker_api_requested" in result["rejection_reasons"]
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"


def test_auto_entry_request_is_rejected() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(request_auto_entry=True)]}
    )

    assert "auto_entry_requested" in result["rejection_reasons"]
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"


def test_leverage_escalation_request_is_rejected() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(request_leverage_escalation=True)]}
    )

    assert "leverage_escalation_requested" in result["rejection_reasons"]
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"


def test_credential_secret_payload_is_rejected_and_not_echoed() -> None:
    secret_value = "DO_NOT_ECHO_SECRET_VALUE"
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {
            "api_key": secret_value,
            "candidates": [_candidate()],
        }
    )

    assert "credential_or_secret_supplied" in result["rejection_reasons"]
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"
    assert secret_value not in repr(result)


def test_credential_secret_payload_without_candidates_is_blocked_and_not_echoed() -> None:
    secret_value = "DO_NOT_ECHO_SECRET_VALUE"
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {
            "api_key": secret_value,
            "candidates": [],
        }
    )

    assert result["ranked_opportunities"] == []
    assert "credential_or_secret_supplied" in result["rejection_reasons"]
    assert result["alert_level"] == "BLOCKED_UNSAFE_REQUEST"
    assert result["safe_next_action"] == (
        "Unsafe request blocked. Remove live/broker/auto-entry/leverage/"
        "credential/revenge/martingale fields and rerun read-only scan."
    )
    assert secret_value not in repr(result)


def test_no_qualified_candidates_returns_continue_scan_safe_next_action() -> None:
    result = evaluate_big_winner_watchtower_22h6d_v1(
        {"candidates": [_candidate(reward_risk_ratio=1.0, expected_r_multiple=1.0)]}
    )

    assert result["top_opportunity"] is None
    assert result["big_winner_candidate_count"] == 0
    assert result["safe_next_action"] == (
        "No qualified asymmetric big-winner candidate. Continue read-only 22h/6d scan."
    )


def test_source_contains_no_forbidden_runtime_tokens() -> None:
    module = importlib.import_module(
        "automation.forex_engine.big_winner_watchtower_22h6d_v1"
    )
    source = inspect.getsource(module)

    for token in (
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ):
        assert token not in source
