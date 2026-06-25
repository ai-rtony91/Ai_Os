from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.trade_latency_baseline_reporter_v1 import (  # noqa: E402
    BLOCK_LATENCY_INVALID_EVIDENCE,
    BLOCK_LATENCY_MISSING_TIMESTAMPS,
    BLOCK_LATENCY_SLOW_SEGMENT,
    LATENCY_READY_FOR_REVIEW,
    evaluate_trade_latency_baseline,
)


def fast_evidence() -> dict:
    return {
        "timestamps": {
            "quote_received_utc": "2026-06-25T12:00:00Z",
            "signal_generated_utc": "2026-06-25T12:00:01Z",
            "preview_started_utc": "2026-06-25T12:00:02Z",
            "preview_completed_utc": "2026-06-25T12:00:03Z",
            "risk_gate_started_utc": "2026-06-25T12:00:04Z",
            "risk_gate_completed_utc": "2026-06-25T12:00:05Z",
            "owner_approval_utc": "2026-06-25T12:00:10Z",
            "order_submit_started_utc": "2026-06-25T12:00:11Z",
            "order_filled_utc": "2026-06-25T12:00:12Z",
            "monitor_started_utc": "2026-06-25T12:00:13Z",
            "pl_classified_utc": "2026-06-25T12:00:14Z",
            "audit_written_utc": "2026-06-25T12:00:15Z",
        },
        "trade_context": {
            "instrument": "EUR_USD",
            "direction": "LONG",
            "strategy_name": "paper_edge_candidate",
            "candidate_id": "c1-eur-buy",
            "order_fill_transaction_id": 334,
            "pl_capture_classification": "FILLED_TRADE_PL_NEGATIVE",
            "profit_claimed": False,
        },
    }


def test_missing_evidence_blocks() -> None:
    result = evaluate_trade_latency_baseline()

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_INVALID_EVIDENCE


def test_missing_timestamp_blocks() -> None:
    evidence = fast_evidence()
    del evidence["timestamps"]["quote_received_utc"]

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_MISSING_TIMESTAMPS
    assert "quote_received_utc" in result["missing_timestamps"]


def test_missing_trade_context_field_blocks() -> None:
    evidence = fast_evidence()
    del evidence["trade_context"]["candidate_id"]

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_INVALID_EVIDENCE
    assert "candidate_id" in result["blocked_reasons"][0]


def test_malformed_timestamp_blocks() -> None:
    evidence = fast_evidence()
    evidence["timestamps"]["signal_generated_utc"] = "not-a-timestamp"

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_INVALID_EVIDENCE
    assert "signal_generated_utc" in result["invalid_timestamps"]


def test_non_chronological_timestamp_blocks() -> None:
    evidence = fast_evidence()
    evidence["timestamps"]["preview_completed_utc"] = "2026-06-25T11:59:59Z"

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_INVALID_EVIDENCE
    assert result["invalid_timestamps"]


def test_complete_fast_evidence_returns_ready_and_allowed() -> None:
    result = evaluate_trade_latency_baseline(fast_evidence())

    assert result["allowed"] is True
    assert result["decision"] == LATENCY_READY_FOR_REVIEW
    assert result["latency_ready_for_review"] is True
    assert result["total_trade_cycle_ms"] == 15000.0


def test_slow_quote_to_signal_segment_blocks() -> None:
    evidence = fast_evidence()
    evidence["timestamps"]["quote_received_utc"] = "2026-06-25T11:59:55Z"

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_SLOW_SEGMENT
    assert result["slow_segments"][0]["segment"] == "quote_to_signal_ms"


def test_slow_submit_to_fill_segment_blocks() -> None:
    evidence = fast_evidence()
    evidence["timestamps"]["order_filled_utc"] = "2026-06-25T12:00:20Z"
    evidence["timestamps"]["monitor_started_utc"] = "2026-06-25T12:00:21Z"
    evidence["timestamps"]["pl_classified_utc"] = "2026-06-25T12:00:22Z"
    evidence["timestamps"]["audit_written_utc"] = "2026-06-25T12:00:23Z"

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_SLOW_SEGMENT
    assert any(
        segment["segment"] == "submit_to_fill_ms"
        for segment in result["slow_segments"]
    )


def test_slow_monitor_to_pl_classification_segment_blocks() -> None:
    evidence = fast_evidence()
    evidence["timestamps"]["pl_classified_utc"] = "2026-06-25T12:00:50Z"
    evidence["timestamps"]["audit_written_utc"] = "2026-06-25T12:00:51Z"

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_SLOW_SEGMENT
    assert any(
        segment["segment"] == "monitor_to_pl_classification_ms"
        for segment in result["slow_segments"]
    )


def test_total_cycle_too_slow_blocks() -> None:
    evidence = fast_evidence()
    evidence["timestamps"]["owner_approval_utc"] = "2026-06-25T12:01:55Z"
    evidence["timestamps"]["order_submit_started_utc"] = "2026-06-25T12:01:56Z"
    evidence["timestamps"]["order_filled_utc"] = "2026-06-25T12:01:57Z"
    evidence["timestamps"]["monitor_started_utc"] = "2026-06-25T12:01:58Z"
    evidence["timestamps"]["pl_classified_utc"] = "2026-06-25T12:01:59Z"
    evidence["timestamps"]["audit_written_utc"] = "2026-06-25T12:02:01Z"

    result = evaluate_trade_latency_baseline(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_LATENCY_SLOW_SEGMENT
    assert any(
        segment["segment"] == "total_trade_cycle_ms"
        for segment in result["slow_segments"]
    )


def test_output_includes_slowest_and_fastest_segment() -> None:
    result = evaluate_trade_latency_baseline(fast_evidence())

    assert result["fastest_segment"]["segment"]
    assert result["fastest_segment"]["ms"] >= 0
    assert result["slowest_segment"]["segment"]
    assert result["slowest_segment"]["ms"] >= result["fastest_segment"]["ms"]


def test_operator_benefit_text_exists_for_anthony_operator() -> None:
    result = evaluate_trade_latency_baseline(fast_evidence())
    benefit = result["operator_benefit"].lower()

    assert "anthony" in benefit
    assert "operator" in benefit
    assert "shows where time is being lost" in benefit
    assert "continue/stop answer" in benefit


def test_safety_flags_remain_conservative() -> None:
    result = evaluate_trade_latency_baseline(fast_evidence())
    safety = result["safety"]

    assert safety["local_only"] is True
    assert safety["broker_calls_allowed"] is False
    assert safety["credential_access_allowed"] is False
    assert safety["order_placement_allowed"] is False
    assert safety["order_close_allowed"] is False
    assert safety["live_endpoint_allowed"] is False
    assert safety["repo_mutation_outside_allowed_files"] is False
    assert safety["uses_current_time"] is False


def test_function_never_raises_for_malformed_input() -> None:
    malformed_values = [
        ["not", "a", "mapping"],
        {"timestamps": "bad", "trade_context": {}},
        {"timestamps": {"quote_received_utc": object()}, "trade_context": object()},
    ]

    for value in malformed_values:
        result = evaluate_trade_latency_baseline(value)  # type: ignore[arg-type]
        assert result["allowed"] is False
        assert result["decision"] in {
            BLOCK_LATENCY_INVALID_EVIDENCE,
            BLOCK_LATENCY_MISSING_TIMESTAMPS,
        }
