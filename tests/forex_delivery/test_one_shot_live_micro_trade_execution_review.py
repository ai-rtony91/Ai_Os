from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.one_shot_live_micro_trade_execution_review import (
    NEXT_PACKET_CANDIDATE,
    REQUIRED_HUMAN_PHRASE,
    build_one_shot_live_micro_trade_execution_review_result,
    build_sanitized_report,
    cli_summary,
)


def read_only_evidence() -> dict[str, object]:
    return {
        "source_type": "fixture",
        "source_label": "FIXTURE_NOT_LIVE",
        "freshness_utc": "2026-06-19T00:00:00Z",
        "live_trading_allowed_from_this_data": False,
        "broker_state": {
            "account_reachable": False,
            "open_positions_reconciled": False,
            "daily_pl_available": False,
        },
        "trading_history": {
            "available": False,
            "block_reason": "fixture_history_not_real_closed_trade_evidence",
        },
    }


def paper_evidence() -> dict[str, object]:
    return {
        "selected_pair": "EUR_USD",
        "signal_side": "BUY",
        "risk_approval": True,
        "paper_entry_created": True,
        "paper_units": 1,
        "exit_plan_status": "READY",
        "stop_loss_policy": "REQUIRED_BEFORE_OR_WITH_ENTRY",
        "take_profit_policy": "FIXTURE_TAKE_PROFIT_POLICY",
        "max_time_policy": "FIXTURE_MAX_TIME_POLICY",
        "manual_close_fallback": "MANUAL_BROKER_UI_FALLBACK_REQUIRED",
        "paper_close_reconcile": True,
        "realized_paper_pl": 1.2,
        "trading_history_row_written": True,
        "live_execution_allowed": False,
    }


def arming_evidence(live_armable: bool = False) -> dict[str, object]:
    return {
        "LIVE_ARMABLE": live_armable,
        "max_units": 1,
        "required_human_phrase": "I AUTHORIZE ONE LIVE MICRO TRADE DRY-RUN ARMING REVIEW",
        "live_execution_allowed": False,
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
    }


def test_default_review_is_not_ready_and_never_allows_execution():
    result = build_one_shot_live_micro_trade_execution_review_result(
        read_only_evidence={},
        paper_loop_evidence={},
        arming_gate_evidence={},
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["EXECUTION_REVIEW_READY"] is False
    assert result["live_execution_allowed"] is False
    assert result["live_trade_placed"] is False
    assert result["broker_write_calls_allowed"] is False
    assert result["order_placement_allowed"] is False
    assert result["close_trade_allowed"] is False
    assert result["proposed_units"] == 1
    assert result["proposed_units"] <= result["max_units"]
    assert "read_only_live_data_bridge_evidence_report_missing" in result["blocked_reasons"]


def test_paper_and_arming_evidence_are_recognized_without_execution():
    paper = paper_evidence()
    paper["paper_units"] = 1000
    result = build_one_shot_live_micro_trade_execution_review_result(
        read_only_evidence=read_only_evidence(),
        paper_loop_evidence=paper,
        arming_gate_evidence=arming_evidence(live_armable=False),
        future_execution_phrase=REQUIRED_HUMAN_PHRASE,
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["EXECUTION_REVIEW_READY"] is False
    assert result["proposed_units"] == 1
    assert result["max_units"] == 1
    assert result["proposed_units"] <= result["max_units"]
    assert "proposed_units_exceed_micro_trade_limit" not in result["blocked_reasons"]
    assert result["paper_loop_status"]["paper_entry_created"] is True
    assert result["paper_loop_status"]["trading_history_row_written"] is True
    assert result["arming_gate_status"]["LIVE_ARMABLE"] is False
    assert "paper_entry_created" in result["evidence_present"]
    assert "read_only_bridge_fixture_source_not_live_permitted" in result["blocked_reasons"]
    assert result["live_trade_placed"] is False


def test_required_future_execution_phrase_and_next_packet_are_present():
    result = build_one_shot_live_micro_trade_execution_review_result(
        read_only_evidence={},
        paper_loop_evidence={},
        arming_gate_evidence={},
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["required_human_phrase"] == REQUIRED_HUMAN_PHRASE
    assert result["next_packet_candidate"] == NEXT_PACKET_CANDIDATE
    assert "future_execution_human_phrase_not_provided" in result["blocked_reasons"]


def test_missing_arming_max_units_defaults_to_one_micro_unit():
    arming = arming_evidence()
    del arming["max_units"]
    paper = paper_evidence()
    paper["paper_units"] = 1000

    result = build_one_shot_live_micro_trade_execution_review_result(
        read_only_evidence=read_only_evidence(),
        paper_loop_evidence=paper,
        arming_gate_evidence=arming,
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["max_units"] == 1
    assert result["proposed_units"] == 1
    assert result["proposed_units"] <= result["max_units"]
    assert "proposed_units_exceed_micro_trade_limit" not in result["blocked_reasons"]
    assert result["live_execution_allowed"] is False
    assert result["live_trade_placed"] is False


def test_report_and_cli_summary_are_sanitized():
    result = build_one_shot_live_micro_trade_execution_review_result(
        read_only_evidence=read_only_evidence(),
        paper_loop_evidence=paper_evidence(),
        arming_gate_evidence=arming_evidence(),
        generated_at_utc="2026-06-19T00:00:00Z",
    )
    report = build_sanitized_report(result)
    summary = cli_summary(result)
    serialized = report + json.dumps(summary, sort_keys=True)

    assert summary["EXECUTION_REVIEW_READY"] is False
    assert summary["live_execution_allowed"] is False
    assert summary["live_trade_placed"] is False
    for forbidden in (
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "Authorization",
        "Bearer ",
        "accountID",
        "orderID",
        "transactionID",
        "rawBroker",
    ):
        assert forbidden not in serialized


def test_dashboard_references_execution_review_without_browser_broker_calls():
    source = (REPO_ROOT / "apps/dashboard/src/MinimalOperatorDashboard.jsx").read_text(
        encoding="utf-8"
    )
    start = source.index("function buildExecutionReviewStatus")
    end = source.index("function buildLiveReadinessModel", start)
    panel_start = source.index("function ExecutionReviewStatusPanel")
    panel_end = source.index("function ExecutionReadinessPage", panel_start)
    review_source = source[start:end] + source[panel_start:panel_end]

    assert "EXECUTION_REVIEW_READY" in review_source
    assert "LIVE_TRADE_PLACED" in review_source
    assert REQUIRED_HUMAN_PHRASE in review_source
    assert NEXT_PACKET_CANDIDATE in review_source
    for forbidden in (
        "fetch(",
        "XMLHttpRequest",
        "axios",
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
    ):
        assert forbidden not in review_source


def test_no_broker_write_or_live_order_endpoint_appears_in_review_code():
    checked_paths = [
        REPO_ROOT / "src/forex_delivery/one_shot_live_micro_trade_execution_review.py",
        REPO_ROOT / "scripts/forex_delivery/run_one_shot_live_micro_trade_execution_review.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)
    lowered = combined.lower()

    for forbidden in (
        ".post(",
        ".put(",
        ".patch(",
        ".delete(",
        "/orders",
        "/trades/",
        "/positions/",
        "createorder",
        "cancelorder",
        "closetrade",
        "closeposition",
    ):
        assert forbidden not in lowered
