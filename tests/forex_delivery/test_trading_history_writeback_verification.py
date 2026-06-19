from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.trading_history_writeback_verification import (  # noqa: E402
    build_sanitized_report,
    build_trading_history_writeback_verification_model,
    cli_summary,
)


def read_only_fixture() -> dict[str, object]:
    return {
        "source_type": "fixture",
        "source_label": "FIXTURE_NOT_LIVE",
        "freshness_utc": "2026-06-19T00:00:00Z",
        "stale_status": "BLOCKED",
        "trading_history": {
            "trading_history_available": True,
            "history_rows": [{"pair": "EUR_USD", "realized_pl": "0.10"}],
        },
    }


def read_only_broker_history() -> dict[str, object]:
    return {
        "source_type": "broker-live-read-only",
        "source_label": "OANDA_READ_ONLY_SANITIZED",
        "freshness_utc": "2026-06-19T00:00:00Z",
        "stale_status": "VALID",
        "trading_history": {
            "trading_history_available": True,
            "history_rows": [{"pair": "EUR_USD", "realized_pl": "0.10"}],
            "evidence_path": "Reports/forex_delivery/sanitized_history.md",
        },
    }


def paper_history() -> dict[str, object]:
    return {
        "trading_history_row_written": True,
        "evidence_path": "Reports/forex_delivery/paper_history.md",
        "live_execution_allowed": False,
    }


def test_fixture_only_data_cannot_verify_real_history_writeback():
    result = build_trading_history_writeback_verification_model(
        read_only_model=read_only_fixture(),
        paper_model=paper_history(),
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["paper_history_writeback_verified"] is True
    assert result["real_broker_history_writeback_verified"] is False
    assert result["trading_history_writeback_verified"] is False
    assert "fixture_history_cannot_verify_real_broker_writeback" in result["blocked_reasons"]
    assert result["live_execution_allowed"] is False


def test_broker_read_only_history_rows_verify_real_history_writeback():
    result = build_trading_history_writeback_verification_model(
        read_only_model=read_only_broker_history(),
        paper_model=paper_history(),
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["paper_history_writeback_verified"] is True
    assert result["real_broker_history_writeback_verified"] is True
    assert result["trading_history_writeback_verified"] is True
    assert result["sanitized_history_rows_count"] == 1
    assert result["live_execution_allowed"] is False


def test_history_report_and_summary_are_sanitized():
    result = build_trading_history_writeback_verification_model(
        read_only_model=read_only_broker_history(),
        paper_model=paper_history(),
        generated_at_utc="2026-06-19T00:00:00Z",
    )
    serialized = build_sanitized_report(result) + json.dumps(cli_summary(result))

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
