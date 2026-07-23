from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_extended_evidence_campaign_v1 import (  # noqa: E402
    COLLECTING_MARKET_DEMO_EVIDENCE,
    evaluate_extended_evidence_campaign,
)
from automation.forex_engine.oanda_practice_closed_trade_receipt_intake_v1 import (  # noqa: E402
    APPENDED,
    BLOCKED_CONFIRMATION,
    BLOCKED_DUPLICATE_RECEIPT,
    BLOCKED_LEDGER_LOCKED,
    BLOCKED_NOT_CLOSED,
    BLOCKED_RECEIPT_INVALID,
    BLOCKED_RECEIPT_MISSING,
    BLOCKED_RECEIPT_UNSAFE,
    LOCK_RELATIVE_PATH,
    READY_TO_APPEND,
    evaluate_receipt,
    intake_receipt,
)


def _receipt(**overrides: object) -> dict[str, object]:
    receipt: dict[str, object] = {
        "schema": "aios.forex.oanda_practice_closed_trade_receipt.v1",
        "broker": "OANDA",
        "environment": "PRACTICE",
        "trade_status": "CLOSED",
        "broker_trade_reference": "OANDA-PRACTICE-TRADE-0001",
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 1000,
        "entry_time_utc": "2026-07-23T13:00:00Z",
        "exit_time_utc": "2026-07-23T13:30:00Z",
        "entry_price": 1.17000,
        "exit_price": 1.17100,
        "net_realized_pnl_usd": 1.00,
        "pre_balance_usd": 1000.00,
        "post_balance_usd": 1001.00,
        "balance_adjustment_usd": 0.00,
        "close_reason": "TAKE_PROFIT",
        "close_reason_note": None,
        "strategy_name": "governed_market_demo_v1",
        "timeframe": "M15",
        "market_session": "NEW_YORK",
        "walk_forward_window_id": "WF-2026-W01",
        "spread_pips": 0.8,
        "absolute_slippage_pips": 0.1,
        "trade_drawdown_pct": 0.2,
        "broker_reported_closed_trade": True,
        "stop_loss_attached": True,
        "stop_loss_price": 1.16900,
        "take_profit_attached": True,
        "take_profit_price": 1.17100,
        "raw_broker_payload_included": False,
        "credential_data_included": False,
        "account_identifier_included": False,
        "live_money_used": False,
        "order_created_by_intake": False,
    }
    receipt.update(overrides)
    return receipt


def _confirmations(**overrides: object) -> dict[str, object]:
    confirmations: dict[str, object] = {
        "owner_confirmed_receipt_reviewed": True,
        "owner_confirmed_demo_practice_only": True,
        "owner_confirmed_closed_trade_only": True,
        "owner_confirmed_no_credentials_or_account_id": True,
        "owner_confirmed_no_raw_broker_payload": True,
        "owner_confirmed_no_order_created_by_intake": True,
        "owner_confirmed_append_only": True,
    }
    confirmations.update(overrides)
    return confirmations


def _ledger_path(root: Path) -> Path:
    return root / "telemetry" / "forex" / "demo_proof_ledger.jsonl"


def _read_rows(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_missing_receipt_blocks() -> None:
    result = evaluate_receipt(None, confirmations=_confirmations())
    assert result["status"] == BLOCKED_RECEIPT_MISSING
    assert result["passed"] is False


def test_open_trade_blocks() -> None:
    result = evaluate_receipt(
        _receipt(trade_status="OPEN"), confirmations=_confirmations()
    )
    assert result["status"] == BLOCKED_NOT_CLOSED
    assert "trade_status_must_be_CLOSED" in result["blockers"]


def test_sensitive_key_blocks_before_validation() -> None:
    receipt = _receipt()
    receipt["access_token"] = "never-store-this"
    result = evaluate_receipt(receipt, confirmations=_confirmations())
    assert result["status"] == BLOCKED_RECEIPT_UNSAFE
    assert any("sensitive_key_detected" in item for item in result["blockers"])


def test_bearer_value_blocks() -> None:
    receipt = _receipt(close_reason_note="Bearer abcdef")
    result = evaluate_receipt(receipt, confirmations=_confirmations())
    assert result["status"] == BLOCKED_RECEIPT_UNSAFE
    assert any("authorization_value_detected" in item for item in result["blockers"])


def test_balance_mismatch_blocks() -> None:
    result = evaluate_receipt(
        _receipt(post_balance_usd=1002.00), confirmations=_confirmations()
    )
    assert result["status"] == BLOCKED_RECEIPT_INVALID
    assert "post_balance_does_not_reconcile_to_net_pnl" in result["blockers"]


def test_nonzero_balance_adjustment_blocks() -> None:
    result = evaluate_receipt(
        _receipt(balance_adjustment_usd=5.0, post_balance_usd=1006.0),
        confirmations=_confirmations(),
    )
    assert result["status"] == BLOCKED_RECEIPT_INVALID
    assert "balance_adjustment_usd_must_be_zero" in result["blockers"]


def test_invalid_time_order_blocks() -> None:
    result = evaluate_receipt(
        _receipt(exit_time_utc="2026-07-23T12:59:59Z"),
        confirmations=_confirmations(),
    )
    assert result["status"] == BLOCKED_RECEIPT_INVALID
    assert "exit_time_must_be_after_entry_time" in result["blockers"]


def test_missing_confirmation_blocks() -> None:
    result = evaluate_receipt(
        _receipt(),
        confirmations=_confirmations(owner_confirmed_append_only=False),
    )
    assert result["status"] == BLOCKED_CONFIRMATION
    assert "owner_confirmed_append_only_required" in result["blockers"]


def test_valid_receipt_builds_market_demo_ledger_entry() -> None:
    result = evaluate_receipt(_receipt(), confirmations=_confirmations())
    assert result["status"] == READY_TO_APPEND
    entry = result["ledger_entry"]
    assert entry["record_type"] == "REAL_DEMO_DAY"
    assert entry["session_mode"] == "OANDA_PRACTICE"
    assert entry["session_source"] == "oanda_practice_closed_trade_receipt_intake_v1"
    assert entry["fills"] == 1
    assert entry["wins"] == 1
    assert entry["live_trading_allowed"] is False
    assert entry["automatic_evidence_append_allowed"] is False
    assert entry["trade_rows"][0]["realized_pnl_usd"] == 1.0


def test_dry_run_does_not_create_ledger(tmp_path: Path) -> None:
    result = intake_receipt(
        tmp_path,
        _receipt(),
        confirmations=_confirmations(),
        apply=False,
    )
    assert result["status"] == READY_TO_APPEND
    assert result["appended"] is False
    assert not _ledger_path(tmp_path).exists()


def test_apply_appends_exactly_one_line(tmp_path: Path) -> None:
    result = intake_receipt(
        tmp_path,
        _receipt(),
        confirmations=_confirmations(),
        apply=True,
    )
    assert result["status"] == APPENDED
    assert result["appended"] is True
    rows = _read_rows(_ledger_path(tmp_path))
    assert len(rows) == 1
    assert rows[0]["trade_rows"][0]["broker_trade_reference"] == "OANDA-PRACTICE-TRADE-0001"


def test_duplicate_reference_is_blocked(tmp_path: Path) -> None:
    first = intake_receipt(
        tmp_path,
        _receipt(),
        confirmations=_confirmations(),
        apply=True,
    )
    second = intake_receipt(
        tmp_path,
        _receipt(exit_price=1.17200),
        confirmations=_confirmations(),
        apply=True,
    )
    assert first["status"] == APPENDED
    assert second["status"] == BLOCKED_DUPLICATE_RECEIPT
    assert "duplicate_broker_trade_reference" in second["blockers"]
    assert len(_read_rows(_ledger_path(tmp_path))) == 1


def test_loss_and_breakeven_classification(tmp_path: Path) -> None:
    loss = _receipt(
        broker_trade_reference="OANDA-PRACTICE-TRADE-LOSS",
        net_realized_pnl_usd=-2.0,
        post_balance_usd=998.0,
        exit_price=1.1680,
        close_reason="STOP_LOSS",
    )
    flat = _receipt(
        broker_trade_reference="OANDA-PRACTICE-TRADE-FLAT",
        entry_time_utc="2026-07-23T14:00:00Z",
        exit_time_utc="2026-07-23T14:30:00Z",
        net_realized_pnl_usd=0.0,
        post_balance_usd=1000.0,
        exit_price=1.1700,
        close_reason="MANUAL",
    )
    loss_result = evaluate_receipt(loss, confirmations=_confirmations())
    flat_result = evaluate_receipt(flat, confirmations=_confirmations())
    assert loss_result["ledger_entry"]["losses"] == 1
    assert loss_result["ledger_entry"]["wins"] == 0
    assert flat_result["ledger_entry"]["losses"] == 0
    assert flat_result["ledger_entry"]["wins"] == 0


def test_window_count_increments_only_for_new_window(tmp_path: Path) -> None:
    receipts = [
        _receipt(),
        _receipt(
            broker_trade_reference="OANDA-PRACTICE-TRADE-0002",
            entry_time_utc="2026-07-24T13:00:00Z",
            exit_time_utc="2026-07-24T13:30:00Z",
            pre_balance_usd=1001.0,
            post_balance_usd=1002.0,
        ),
        _receipt(
            broker_trade_reference="OANDA-PRACTICE-TRADE-0003",
            entry_time_utc="2026-07-25T13:00:00Z",
            exit_time_utc="2026-07-25T13:30:00Z",
            pre_balance_usd=1002.0,
            post_balance_usd=1003.0,
            walk_forward_window_id="WF-2026-W02",
        ),
    ]
    for receipt in receipts:
        result = intake_receipt(
            tmp_path,
            receipt,
            confirmations=_confirmations(),
            apply=True,
        )
        assert result["status"] == APPENDED
    rows = _read_rows(_ledger_path(tmp_path))
    assert [row["windows_toward_verdict"] for row in rows] == [1, 1, 2]


def test_drawdown_tracks_prior_peak(tmp_path: Path) -> None:
    first = _receipt(
        broker_trade_reference="OANDA-PRACTICE-TRADE-PEAK",
        net_realized_pnl_usd=10.0,
        post_balance_usd=1010.0,
    )
    second = _receipt(
        broker_trade_reference="OANDA-PRACTICE-TRADE-DD",
        entry_time_utc="2026-07-24T13:00:00Z",
        exit_time_utc="2026-07-24T13:30:00Z",
        net_realized_pnl_usd=-10.0,
        pre_balance_usd=1010.0,
        post_balance_usd=1000.0,
        exit_price=1.1680,
        close_reason="STOP_LOSS",
        trade_drawdown_pct=0.5,
    )
    assert intake_receipt(tmp_path, first, confirmations=_confirmations(), apply=True)["status"] == APPENDED
    result = intake_receipt(tmp_path, second, confirmations=_confirmations(), apply=True)
    assert result["status"] == APPENDED
    assert result["ledger_entry"]["max_drawdown_pct"] == pytest.approx(0.99009901)


def test_existing_lock_blocks_without_deleting_foreign_lock(tmp_path: Path) -> None:
    lock_path = tmp_path / LOCK_RELATIVE_PATH
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text("foreign-process\n", encoding="utf-8")
    result = intake_receipt(
        tmp_path,
        _receipt(),
        confirmations=_confirmations(),
        apply=True,
    )
    assert result["status"] == BLOCKED_LEDGER_LOCKED
    assert lock_path.read_text(encoding="utf-8") == "foreign-process\n"


def test_appended_receipt_is_consumed_by_extended_campaign(tmp_path: Path) -> None:
    result = intake_receipt(
        tmp_path,
        _receipt(),
        confirmations=_confirmations(),
        apply=True,
    )
    assert result["status"] == APPENDED
    campaign = evaluate_extended_evidence_campaign(
        _ledger_path(tmp_path),
        as_of_date=__import__("datetime").date(2026, 7, 23),
    )
    assert campaign["status"] == COLLECTING_MARKET_DEMO_EVIDENCE
    assert campaign["summary"]["market_demo_trades"] == 1
    assert campaign["summary"]["fixture_or_simulation_trades"] == 0
    assert campaign["summary"]["metrics_complete"] is True


def test_serialized_result_contains_no_live_approval_or_secrets() -> None:
    result = evaluate_receipt(_receipt(), confirmations=_confirmations())
    serialized = json.dumps(result, sort_keys=True).lower()
    for phrase in (
        "approved for live",
        "safe to trade live",
        "guaranteed profit",
        "bearer ",
        "access_token",
        "account_id",
    ):
        assert phrase not in serialized
