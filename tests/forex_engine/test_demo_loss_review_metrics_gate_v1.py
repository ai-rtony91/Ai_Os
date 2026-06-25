from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.demo_loss_review_metrics_gate_v1 import (  # noqa: E402
    BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED,
    BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS,
    BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE,
    BLOCK_NEXT_DEMO_ORDER_WEAK_MARKET_REGIME,
    BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY,
    BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL,
    REVIEW_READY_FOR_OWNER_APPROVAL,
    evaluate_demo_loss_review_metrics_gate,
)


def passing_evidence() -> dict:
    return {
        "trade_result": {
            "trade_id": 334,
            "close_reason": "STOP_LOSS_ORDER",
            "realized_pl_total": -0.0010,
            "pl_capture_classification": "FILLED_TRADE_PL_NEGATIVE",
            "open_trade_count": 0,
            "open_position_count": 0,
            "pending_order_count": 0,
            "profit_claimed": False,
        },
        "entry_metrics": {
            "signal_time_utc": "2026-06-25T12:00:00Z",
            "order_submit_time_utc": "2026-06-25T12:00:05Z",
            "fill_time_utc": "2026-06-25T12:00:06Z",
            "instrument": "EUR_USD",
            "direction": "LONG",
            "entry_price": 1.1000,
            "bid": 1.0999,
            "ask": 1.1001,
            "mid": 1.1000,
            "quote_age_ms": 500,
            "candle_timestamp_utc": "2026-06-25T11:59:00Z",
        },
        "signal_metrics": {
            "strategy_name": "paper_edge_candidate",
            "strategy_version": "v1",
            "candidate_id": "c1-eur-buy",
            "candidate_rank": 1,
            "signal_confidence": 0.7,
            "signal_threshold": 0.5,
            "signal_passed": True,
            "reason_code": "paper_to_demo_review",
        },
        "market_regime_metrics": {
            "regime_label": "TRENDING",
            "trend_state": "UP",
            "atr": 0.0012,
            "volatility_bucket": "NORMAL",
            "session": "NEW_YORK",
            "news_filter_passed": True,
        },
        "spread_slippage_metrics": {
            "spread_at_signal": 0.0001,
            "spread_at_preview": 0.0001,
            "spread_at_submit": 0.0001,
            "spread_at_fill": 0.0001,
            "expected_price": 1.1000,
            "fill_price": 1.1000,
            "slippage": 0.0,
            "cost_model_expected": 0.00015,
            "actual_cost": 0.0001,
        },
        "risk_geometry_metrics": {
            "stop_distance": 0.0010,
            "take_profit_distance": 0.0015,
            "r_multiple": 1.5,
            "units": 10,
            "risk_amount": 0.01,
            "risk_percent": 0.01,
            "reward_amount": 0.015,
            "max_spread_gate_passed": True,
            "max_data_age_gate_passed": True,
            "kill_switch_passed": True,
            "daily_loss_gate_passed": True,
            "cooldown_after_loss_passed": True,
            "duplicate_setup_gate_passed": True,
        },
        "timing_latency_metrics": {
            "signal_to_preview_ms": 100,
            "preview_to_risk_gate_ms": 100,
            "risk_gate_to_approval_ms": 200,
            "approval_to_submit_ms": 300,
            "submit_to_fill_ms": 400,
            "fill_to_monitor_ms": 500,
            "monitor_to_pl_classification_ms": 600,
            "polling_interval_ms": 5000,
            "broker_round_trip_ms": 800,
        },
        "paper_to_demo_lineage_metrics": {
            "paper_sample_size": 30,
            "minimum_sample_size": 30,
            "expectancy": 1.0,
            "profit_factor": 1.5,
            "max_drawdown": 100.0,
            "win_rate": 0.55,
            "walk_forward_passed": True,
            "market_regime_coverage_passed": True,
            "freshness_passed": True,
            "proof_bundle_passed": True,
            "promotion_verdict": "PROMOTION_GATE_PASS",
        },
    }


def test_missing_evidence_blocks() -> None:
    result = evaluate_demo_loss_review_metrics_gate()

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS
    assert result["missing_metrics"]


def test_complete_passing_evidence_returns_review_ready() -> None:
    result = evaluate_demo_loss_review_metrics_gate(passing_evidence())

    assert result["allowed"] is True
    assert result["decision"] == REVIEW_READY_FOR_OWNER_APPROVAL
    assert result["blocked_reasons"] == []


def test_insufficient_sample_size_blocks_weak_lineage() -> None:
    evidence = passing_evidence()
    evidence["paper_to_demo_lineage_metrics"]["paper_sample_size"] = 1

    result = evaluate_demo_loss_review_metrics_gate(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE
    assert result["gate_status"]["lineage_passed"] is False


def test_failed_signal_blocks_weak_signal() -> None:
    evidence = passing_evidence()
    evidence["signal_metrics"]["signal_passed"] = False

    result = evaluate_demo_loss_review_metrics_gate(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_SIGNAL
    assert result["gate_status"]["signal_passed"] is False


def test_failed_news_filter_blocks_weak_market_regime() -> None:
    evidence = passing_evidence()
    evidence["market_regime_metrics"]["news_filter_passed"] = False

    result = evaluate_demo_loss_review_metrics_gate(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_MARKET_REGIME
    assert result["gate_status"]["market_regime_passed"] is False


def test_failed_kill_switch_or_daily_loss_blocks_weak_risk_geometry() -> None:
    kill_switch_evidence = passing_evidence()
    kill_switch_evidence["risk_geometry_metrics"]["kill_switch_passed"] = False
    kill_switch_result = evaluate_demo_loss_review_metrics_gate(kill_switch_evidence)

    daily_loss_evidence = passing_evidence()
    daily_loss_evidence["risk_geometry_metrics"]["daily_loss_gate_passed"] = False
    daily_loss_result = evaluate_demo_loss_review_metrics_gate(daily_loss_evidence)

    assert kill_switch_result["allowed"] is False
    assert kill_switch_result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY
    assert daily_loss_result["allowed"] is False
    assert daily_loss_result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY


def test_stale_quote_or_slow_broker_round_trip_blocks_latency() -> None:
    stale_quote_evidence = passing_evidence()
    stale_quote_evidence["entry_metrics"]["quote_age_ms"] = 6000
    stale_quote_result = evaluate_demo_loss_review_metrics_gate(stale_quote_evidence)

    slow_broker_evidence = passing_evidence()
    slow_broker_evidence["timing_latency_metrics"]["broker_round_trip_ms"] = 6000
    slow_broker_result = evaluate_demo_loss_review_metrics_gate(slow_broker_evidence)

    assert stale_quote_result["allowed"] is False
    assert stale_quote_result["decision"] == BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED
    assert slow_broker_result["allowed"] is False
    assert slow_broker_result["decision"] == BLOCK_NEXT_DEMO_ORDER_LATENCY_NOT_MEASURED


def test_trade_result_with_pending_orders_blocks() -> None:
    evidence = passing_evidence()
    evidence["trade_result"]["pending_order_count"] = 1

    result = evaluate_demo_loss_review_metrics_gate(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_RISK_GEOMETRY


def test_profit_claimed_true_with_non_positive_pl_blocks() -> None:
    evidence = passing_evidence()
    evidence["trade_result"]["profit_claimed"] = True
    evidence["trade_result"]["realized_pl_total"] = 0.0

    result = evaluate_demo_loss_review_metrics_gate(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_WEAK_LINEAGE


def test_malformed_input_never_raises_and_blocks() -> None:
    malformed_results = [
        evaluate_demo_loss_review_metrics_gate(["not", "a", "mapping"]),  # type: ignore[arg-type]
        evaluate_demo_loss_review_metrics_gate({"trade_result": "not a mapping"}),
        evaluate_demo_loss_review_metrics_gate(
            {"trade_result": {"trade_id": object()}}
        ),
    ]

    for result in malformed_results:
        assert result["allowed"] is False
        assert result["decision"] == BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS


def test_operator_benefit_text_exists_and_references_operator_usefulness() -> None:
    result = evaluate_demo_loss_review_metrics_gate(passing_evidence())
    benefit = result["operator_benefit"].lower()

    assert "anthony" in benefit
    assert "operator" in benefit
    assert "prevents another blind demo trade" in benefit
    assert "yes/no review" in benefit


def test_safety_flags_all_remain_conservative() -> None:
    result = evaluate_demo_loss_review_metrics_gate(passing_evidence())
    safety = result["safety"]

    assert safety["local_only"] is True
    assert safety["broker_calls_allowed"] is False
    assert safety["credential_access_allowed"] is False
    assert safety["order_placement_allowed"] is False
    assert safety["order_close_allowed"] is False
    assert safety["live_endpoint_allowed"] is False
    assert safety["repo_mutation_outside_allowed_files"] is False


def test_input_is_not_mutated() -> None:
    evidence = passing_evidence()
    original = deepcopy(evidence)

    evaluate_demo_loss_review_metrics_gate(evidence)

    assert evidence == original
