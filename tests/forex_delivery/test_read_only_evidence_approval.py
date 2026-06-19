from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.one_shot_live_micro_trade_execution_review import (  # noqa: E402
    REQUIRED_HUMAN_PHRASE,
    build_one_shot_live_micro_trade_execution_review_result,
)
from src.forex_delivery.read_only_evidence_approval import (  # noqa: E402
    build_read_only_evidence_approval_model,
    build_sanitized_report,
    cli_summary,
)


def fixture_evidence() -> dict[str, object]:
    return {
        "source_type": "fixture",
        "source_label": "FIXTURE_NOT_LIVE",
        "freshness_utc": "2026-06-19T14:33:27Z",
        "stale_status": "BLOCKED",
        "broker_state": {
            "account_reachable": False,
            "open_position_count": 0,
            "open_positions_reconciled": False,
            "daily_pl_available": False,
            "realized_pl": "UNAVAILABLE",
            "unrealized_pl": "UNAVAILABLE",
            "margin_risk_available": False,
        },
        "trading_history": {
            "trading_history_available": False,
            "block_reason": "fixture_history_not_real_closed_trade_evidence",
        },
        "capabilities": {
            "broker_write_calls_allowed": False,
            "order_placement_allowed": False,
            "close_trade_allowed": False,
        },
    }


def sanitized_oanda_evidence(
    *, daily_pl_available: bool = True, account_pl_available: bool = True, rows: bool = True
) -> dict[str, object]:
    realized_pl = "1.25" if account_pl_available else "UNAVAILABLE"
    unrealized_pl = "0.00" if account_pl_available else "UNAVAILABLE"
    return {
        "source_type": "broker-live-read-only",
        "source_label": "OANDA_READ_ONLY_SANITIZED",
        "freshness_utc": "2026-06-19T14:33:27Z",
        "stale_status": "VALID",
        "broker_state": {
            "account_reachable": True,
            "open_position_count": 0,
            "open_positions_reconciled": True,
            "daily_pl_available": daily_pl_available,
            "daily_pl_ledger_available": daily_pl_available,
            "realized_pl": realized_pl,
            "unrealized_pl": unrealized_pl,
            "margin_risk_available": True,
        },
        "positions": {
            "open_position_count": 0,
            "positions_reconciled": True,
        },
        "risk_pl": {
            "daily_pl_available": daily_pl_available,
            "daily_pl_ledger_available": daily_pl_available,
            "realized_pl": realized_pl,
            "unrealized_pl": unrealized_pl,
            "margin_risk_available": True,
        },
        "trading_history": {
            "trading_history_available": True,
            "history_rows": [
                {
                    "pair": "EUR_USD",
                    "side": "BUY",
                    "units": 1,
                    "realized_pl": "1.25",
                    "source": "OANDA_READ_ONLY_SANITIZED",
                    "freshness": "2026-06-19T14:33:27Z",
                }
            ]
            if rows
            else [],
        },
        "capabilities": {
            "broker_write_calls_allowed": False,
            "order_placement_allowed": False,
            "close_trade_allowed": False,
        },
    }


def paper_evidence() -> dict[str, object]:
    return {
        "selected_pair": "EUR_USD",
        "signal_side": "BUY",
        "risk_approval": True,
        "paper_entry_created": True,
        "paper_units": 1000,
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


def arming_evidence() -> dict[str, object]:
    return {
        "LIVE_ARMABLE": False,
        "max_units": 1,
        "required_human_phrase": "I AUTHORIZE ONE LIVE MICRO TRADE DRY-RUN ARMING REVIEW",
        "live_execution_allowed": False,
        "broker_write_calls_allowed": False,
        "order_placement_allowed": False,
        "close_trade_allowed": False,
    }


def test_fixture_evidence_is_not_approved():
    result = build_read_only_evidence_approval_model(
        fixture_evidence(), generated_at_utc="2026-06-19T00:00:00Z"
    )

    assert result["READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"] is False
    assert "read_only_bridge_fixture_source_not_live_permitted" in result["blocked_reasons"]
    assert result["live_execution_allowed"] is False
    assert result["broker_write_calls_allowed"] is False
    assert result["order_placement_allowed"] is False
    assert result["close_trade_allowed"] is False


def test_sanitized_oanda_read_only_evidence_can_be_approved_for_future_review():
    result = build_read_only_evidence_approval_model(
        sanitized_oanda_evidence(), generated_at_utc="2026-06-19T00:00:00Z"
    )

    assert result["READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"] is True
    assert result["source_type"] == "broker-live-read-only"
    assert result["source_label"] == "OANDA_READ_ONLY_SANITIZED"
    assert result["open_positions_reconciled"] is True
    assert result["open_position_count"] == 0
    assert result["daily_pl_available"] is True
    assert result["trading_history_writeback_verified"] is True
    assert result["live_execution_allowed"] is False


def test_daily_pl_blocker_is_removed_only_when_daily_pl_is_available():
    result = build_read_only_evidence_approval_model(
        sanitized_oanda_evidence(daily_pl_available=False),
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"] is False
    assert result["account_pl_available"] is True
    assert result["daily_pl_available"] is False
    assert result["daily_pl_block_reason"] == "daily P/L ledger not verified"
    assert "daily_pl_not_available_in_read_only_evidence" in result["blocked_reasons"]


def test_safe_status_field_names_do_not_trigger_private_identifier_blocker():
    evidence = sanitized_oanda_evidence()
    evidence["OANDA_ACCOUNT_ID_STATUS"] = "NOT_RECORDED"
    evidence["no_account_id_status"] = "PASS_NO_ACCOUNT_IDENTIFIER_VALUES_RECORDED"
    evidence["no_order_id_status"] = "PASS_NO_ORDER_IDENTIFIER_VALUES_RECORDED"
    evidence["no_transaction_id_status"] = "PASS_NO_TRANSACTION_IDENTIFIER_VALUES_RECORDED"
    evidence["ACCOUNT_ID_RECORDED"] = False
    evidence["RAW_BROKER_PAYLOAD_RECORDED"] = False

    result = build_read_only_evidence_approval_model(
        evidence, generated_at_utc="2026-06-19T00:00:00Z"
    )

    assert result["READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"] is True
    assert "secret_or_private_identifier_marker_present" not in result["blocked_reasons"]


def test_actual_unsafe_private_values_still_block_approval():
    evidence = sanitized_oanda_evidence()
    evidence["runtime_headers"] = {"Authorization": "Bearer FAKE_RUNTIME_TOKEN"}
    evidence["account_identifier"] = "ACCOUNT-IDENTIFIER-RAW-VALUE"
    evidence["order_identifier"] = "ORDER-IDENTIFIER-RAW-VALUE"
    evidence["transaction_identifier"] = "TRANSACTION-IDENTIFIER-RAW-VALUE"

    result = build_read_only_evidence_approval_model(
        evidence, generated_at_utc="2026-06-19T00:00:00Z"
    )

    assert result["READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"] is False
    assert "secret_or_private_identifier_marker_present" in result["blocked_reasons"]


def test_trading_history_writeback_remains_blocked_unless_verified():
    result = build_read_only_evidence_approval_model(
        sanitized_oanda_evidence(rows=False),
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["READ_ONLY_EVIDENCE_APPROVED_FOR_FUTURE_LIVE_REVIEW"] is True
    assert result["trading_history_available"] is True
    assert result["trading_history_writeback_verified"] is False
    assert "real_trading_history_writeback_not_verified" in result["blocked_reasons"]


def test_execution_review_reduces_only_satisfied_read_only_blockers():
    result = build_one_shot_live_micro_trade_execution_review_result(
        read_only_evidence=sanitized_oanda_evidence(),
        paper_loop_evidence=paper_evidence(),
        arming_gate_evidence=arming_evidence(),
        future_execution_phrase=REQUIRED_HUMAN_PHRASE,
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    for removed in (
        "read_only_data_not_approved_for_future_live_execution",
        "broker_account_not_reachable_in_read_only_evidence",
        "open_positions_not_reconciled_in_read_only_evidence",
        "daily_pl_not_available_in_read_only_evidence",
        "open_live_position_state_not_reconciled",
    ):
        assert removed not in result["blocked_reasons"]

    assert "live_micro_trade_arming_gate_not_armable" in result["blocked_reasons"]
    assert "auto_exit_readiness_not_implemented_for_live_execution" in result["blocked_reasons"]
    assert "execution_review_packet_is_not_an_execution_packet" in result["blocked_reasons"]
    assert result["live_execution_allowed"] is False
    assert result["live_trade_placed"] is False


def test_output_contains_no_secret_or_private_identifier_values():
    result = build_read_only_evidence_approval_model(
        sanitized_oanda_evidence(), generated_at_utc="2026-06-19T00:00:00Z"
    )
    serialized = (
        json.dumps(result, sort_keys=True)
        + build_sanitized_report(result)
        + json.dumps(cli_summary(result), sort_keys=True)
    )

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
