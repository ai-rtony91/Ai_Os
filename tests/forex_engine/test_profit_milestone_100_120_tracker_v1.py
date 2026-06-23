from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DASHBOARD_MONEY_STRIP = REPO_ROOT / "apps" / "dashboard" / "src" / "BrokerMoneyStrip.jsx"
DASHBOARD_MONEY_FIXTURE = (
    REPO_ROOT
    / "apps"
    / "dashboard"
    / "mock-data"
    / "aios-oanda-money-strip-v1.example.json"
)

from automation.forex_engine.profit_milestone_100_120_tracker_v1 import (  # noqa: E402
    TARGET_BLOCKED_BY_BROKER,
    TARGET_BLOCKED_BY_EVIDENCE,
    TARGET_BLOCKED_BY_RISK,
    TARGET_READY_FOR_OWNER_REVIEW,
    TARGET_NOT_PROVEN,
    evaluate_profit_milestone_100_120_tracker_v1,
)  # noqa: E402
from automation.forex_engine.read_only_live_data_sanitizer import (  # noqa: E402
    build_money_strip_payload,
    sanitize_account_summary,
    source_fields,
)  # noqa: E402


def base_valid_candidate():
    return {
        "candidate_id": "c1-eur-buy",
        "strategy_id": "s1",
        "instrument": "EUR_USD",
        "direction": "LONG",
        "long_only": True,
        "short_side_disabled": True,
        "starting_balance": 10000.0,
        "current_balance": 11200.0,
        "realized_pl": 1200.0,
        "unrealized_pl": 0.0,
        "open_trades": 2,
        "closed_trades": 35,
        "sample_size": 35,
        "expectancy": 1.1,
        "profit_factor": 1.3,
        "max_drawdown": 12.0,
        "walk_forward_status": "passed",
        "walk_forward_folds": 3,
        "out_of_sample_folds": 3,
        "out_of_sample_folds_passed": True,
        "min_required_trades": 30,
        "min_required_walk_forward_folds": 3,
        "min_required_out_of_sample_folds": 3,
        "min_expectancy": 0.0,
        "min_profit_factor": 1.2,
        "max_drawdown_allowed": 25.0,
        "broker_readiness_status": "READY",
        "risk_gate_status": "READY",
        "broker_readiness_passed": True,
        "risk_gate_passed": True,
        "current_return_source": "fixture",
    }


def test_tracker_defaults_to_not_proven_when_missing_evidence():
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=None)
    assert result["target_status"] == TARGET_NOT_PROVEN
    assert result["execution_allowed"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_order_allowed"] is False


def test_tracker_blocks_weak_sample():
    candidate = base_valid_candidate()
    candidate["sample_size"] = 12
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_BLOCKED_BY_EVIDENCE
    assert "insufficient_sample" in result["blockers"]


def test_tracker_blocks_bad_drawdown():
    candidate = base_valid_candidate()
    candidate["max_drawdown"] = 35.0
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_BLOCKED_BY_EVIDENCE
    assert "weak_drawdown_gate" in result["blockers"]


def test_tracker_blocks_weak_profit_factor():
    candidate = base_valid_candidate()
    candidate["profit_factor"] = 1.0
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_BLOCKED_BY_EVIDENCE
    assert "weak_profit_factor" in result["blockers"]


def test_tracker_blocks_missing_broker_proof():
    candidate = base_valid_candidate()
    candidate["broker_readiness_passed"] = False
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_BLOCKED_BY_BROKER
    assert "broker_readiness_not_proven" in result["blockers"]


def test_tracker_blocks_missing_risk_gate():
    candidate = base_valid_candidate()
    candidate["risk_gate_passed"] = False
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_BLOCKED_BY_RISK
    assert "risk_gate_not_proven" in result["blockers"]


def test_tracker_100_percent_ready_path():
    candidate = base_valid_candidate()
    candidate["current_balance"] = 20100.0
    candidate["profit_factor"] = 1.6
    candidate["expectancy"] = 2.0
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_READY_FOR_OWNER_REVIEW
    assert result["execution_allowed"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_order_allowed"] is False


def test_tracker_120_percent_ready_path_is_ready():
    candidate = base_valid_candidate()
    candidate["current_balance"] = 21900.0
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_READY_FOR_OWNER_REVIEW
    assert result["execution_allowed"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_order_allowed"] is False


def test_tracker_no_sensitive_data_leak():
    candidate = base_valid_candidate()
    candidate["proof"] = "token=abc"
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=candidate)
    assert result["target_status"] == TARGET_BLOCKED_BY_EVIDENCE
    assert "sensitive_payload_present" in result["blockers"]


def test_tracker_money_fields_stay_read_only_flags():
    result = evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence=base_valid_candidate())
    assert result["execution_allowed"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_order_allowed"] is False


def test_read_only_money_strip_exposes_money_fields_without_execution():
    context = source_fields(
        source_type="broker-live-read-only",
        source_label="OANDA_READ_ONLY_SANITIZED",
        freshness_utc="2026-06-19T12:00:00Z",
        stale_status="VALID",
        block_reason="read-only",
    )
    broker_state = sanitize_account_summary(
        {
            "account": {
                "balance": "1000.00",
                "NAV": "1004.50",
                "currency": "USD",
                "marginAvailable": "900.00",
                "marginUsed": "100.00",
                "withdrawalLimit": "800.00",
                "openPositionCount": 1,
                "openTradeCount": 1,
                "pendingOrderCount": 2,
                "pl": "12.34",
                "unrealizedPL": "4.50",
            }
        },
        broker_mode="practice",
        freshness_utc="2026-06-19T12:00:00Z",
        source_context=context,
    )
    money_strip = build_money_strip_payload(
        "practice",
        source_context=context,
        broker_state=broker_state,
        positions={**context, "open_trade_count": 1, "open_position_count": 1},
        risk_pl={
            **context,
            "realized_pl": broker_state["realized_pl"],
            "unrealized_pl": broker_state["unrealized_pl"],
        },
        market={
            **context,
            "selected_pair": "EUR_USD",
            "bid": "1.10000",
            "ask": "1.10020",
            "spread": "0.00020",
        },
    )

    assert money_strip["balance"] == "1000.00"
    assert money_strip["nav"] == "1004.50"
    assert money_strip["margin_available"] == "900.00"
    assert money_strip["margin_used"] == "100.00"
    assert money_strip["pending_order_count"] == 2
    assert money_strip["selected_pair"] == "EUR_USD"
    assert money_strip["spread"] == "0.00020"
    assert money_strip["execution_allowed"] is False
    assert money_strip["order_placement_allowed"] is False
    assert money_strip["live_order_allowed"] is False


def test_dashboard_money_strip_has_no_direct_oanda_or_credentials():
    source = DASHBOARD_MONEY_STRIP.read_text(encoding="utf-8")
    lowered = source.lower()

    assert "/api/forex/oanda/money-strip" in source
    assert "api-fxtrade" not in lowered
    assert "api-fxpractice" not in lowered
    assert "https://api" not in lowered
    assert "oanda_api_token" not in lowered
    assert "oanda_account_id" not in lowered
    assert "authorization" not in lowered
    assert ".env" not in lowered


def test_dashboard_money_strip_shows_exec_off_without_order_buttons():
    source = DASHBOARD_MONEY_STRIP.read_text(encoding="utf-8")
    lowered = source.lower()

    assert "EXEC OFF" in source
    assert "<button" not in lowered
    assert ">BUY<" not in source
    assert ">SELL<" not in source
    assert ">CLOSE<" not in source


def test_dashboard_money_strip_fixture_is_blocked_and_read_only():
    fixture = json.loads(DASHBOARD_MONEY_FIXTURE.read_text(encoding="utf-8"))
    text = json.dumps(fixture).lower()

    assert fixture["status"] == "BLOCKED"
    assert fixture["balance"] == "UNKNOWN"
    assert fixture["execution_allowed"] is False
    assert fixture["order_placement_allowed"] is False
    assert fixture["demo_order_allowed"] is False
    assert fixture["live_order_allowed"] is False
    assert fixture["broker_mutation_allowed"] is False
    assert "token" not in text
    assert "account_id" not in text
    assert "raw broker payload" not in text
