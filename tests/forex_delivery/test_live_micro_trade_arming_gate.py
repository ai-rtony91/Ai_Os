from pathlib import Path
import json
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from forex_delivery.live_micro_trade_arming_gate import (  # noqa: E402
    NEXT_PACKET_CANDIDATE,
    REQUIRED_HUMAN_PHRASE,
    build_live_micro_trade_arming_gate_result,
    build_sanitized_report,
    cli_summary,
)


def paper_evidence() -> dict[str, object]:
    return {
        "signal_side": "BUY",
        "risk_approval": True,
        "paper_entry_created": True,
        "exit_plan_status": "READY",
        "paper_close_reconcile": True,
        "realized_paper_pl": 1.2,
        "trading_history_row_written": True,
        "live_execution_allowed": False,
        "stop_loss_policy": {"status": "REQUIRED_PRESENT"},
        "take_profit_policy": {"status": "REQUIRED_PRESENT"},
        "max_time_policy": {"status": "REQUIRED_PRESENT"},
    }


def read_only_evidence() -> dict[str, object]:
    return {
        "source_type": "fixture",
        "source_label": "FIXTURE_NOT_LIVE",
        "stale_status": "BLOCKED",
        "freshness_utc": "2026-06-19T12:00:00Z",
        "broker_state": {"account_reachable": False},
        "positions": {"positions_reconciled": False},
        "risk_pl": {"daily_pl_available": False},
        "trading_history": {"trading_history_available": False},
    }


def test_default_gate_is_not_armable_and_never_allows_execution():
    result = build_live_micro_trade_arming_gate_result(
        read_only_evidence={},
        paper_evidence={},
        generated_at_utc="2026-06-19T12:00:00Z",
    )

    assert result["LIVE_ARMABLE"] is False
    assert result["live_execution_allowed"] is False
    assert result["broker_write_calls_allowed"] is False
    assert result["order_placement_allowed"] is False
    assert result["close_trade_allowed"] is False
    assert "read_only_bridge_evidence_missing" in result["blocked_reasons"]
    assert "paper_loop_evidence_missing" in result["blocked_reasons"]


def test_missing_evidence_blocks_arming():
    result = build_live_micro_trade_arming_gate_result(
        read_only_evidence={},
        paper_evidence={},
    )

    assert "read_only_live_data_bridge_evidence" in result["evidence_missing"]
    assert "paper_signal_execution_loop_evidence" in result["evidence_missing"]
    assert result["next_packet_candidate"] == NEXT_PACKET_CANDIDATE


def test_paper_evidence_reduces_paper_blockers_but_does_not_execute():
    result = build_live_micro_trade_arming_gate_result(
        read_only_evidence=read_only_evidence(),
        paper_evidence=paper_evidence(),
        human_phrase=REQUIRED_HUMAN_PHRASE,
    )

    assert "paper_signal_execution_loop_evidence" in result["evidence_present"]
    assert "paper_signal_missing" not in result["blocked_reasons"]
    assert "paper_history_writeback_missing" not in result["blocked_reasons"]
    assert result["LIVE_ARMABLE"] is False
    assert result["live_execution_allowed"] is False
    assert result["order_placement_allowed"] is False


def test_required_human_phrase_is_present_in_model():
    result = build_live_micro_trade_arming_gate_result(
        read_only_evidence=read_only_evidence(),
        paper_evidence=paper_evidence(),
    )

    assert result["required_human_phrase"] == REQUIRED_HUMAN_PHRASE
    assert "required_human_phrase_not_provided" in result["blocked_reasons"]


def test_output_contains_no_secret_or_private_identifier_values():
    result = build_live_micro_trade_arming_gate_result(
        read_only_evidence=read_only_evidence(),
        paper_evidence=paper_evidence(),
    )
    payload = json.dumps(result, sort_keys=True)

    for forbidden in (
        "OANDA_API_TOKEN",
        "OANDA_ACCOUNT_ID",
        "transactionID",
        "orderID",
        "accountID",
        "Bearer ",
        "rawBroker",
    ):
        assert forbidden not in payload


def test_report_and_cli_summary_are_sanitized():
    result = build_live_micro_trade_arming_gate_result(
        read_only_evidence=read_only_evidence(),
        paper_evidence=paper_evidence(),
        generated_at_utc="2026-06-19T12:00:00Z",
    )
    report = build_sanitized_report(result)
    summary = cli_summary(result)

    assert "AIOS Forex Live Micro-Trade Arming Gate Dry Run V1" in report
    assert "no live trade" in report.lower()
    assert summary["LIVE_ARMABLE"] is False
    assert summary["broker_write_calls_allowed"] is False
    assert summary["close_trade_allowed"] is False
    assert "OANDA_API_TOKEN" not in report
    assert "OANDA_ACCOUNT_ID" not in report


def test_dashboard_references_arming_status_without_browser_broker_calls():
    dashboard_path = REPO_ROOT / "apps" / "dashboard" / "src" / "MinimalOperatorDashboard.jsx"
    source = dashboard_path.read_text(encoding="utf-8")

    assert "buildArmingGateStatus" in source
    assert "ArmingGateStatusPanel" in source
    assert "LIVE_ARMABLE" in source
    assert REQUIRED_HUMAN_PHRASE in source
    for forbidden in ("fetch(", "XMLHttpRequest", "axios", "OANDA_API_TOKEN", "OANDA_ACCOUNT_ID"):
        assert forbidden not in source


def test_no_broker_write_or_live_order_endpoint_appears_in_arming_code():
    paths = [
        REPO_ROOT / "src" / "forex_delivery" / "live_micro_trade_arming_gate.py",
        REPO_ROOT / "scripts" / "forex_delivery" / "run_live_micro_trade_arming_gate.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in paths)

    for forbidden in (
        "requests.",
        "urllib.request",
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
        assert forbidden not in combined
