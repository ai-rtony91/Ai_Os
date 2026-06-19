from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.forex_delivery.auto_exit_live_readiness import (  # noqa: E402
    build_auto_exit_live_readiness_model,
    build_sanitized_report,
    cli_summary,
)


def policy_evidence() -> dict[str, object]:
    return {
        "stop_loss_policy": "REQUIRED_BEFORE_OR_WITH_ENTRY",
        "take_profit_policy": "PRESENT",
        "trailing_stop_policy": "OPTIONAL",
        "max_time_policy": "PRESENT",
        "manual_close_fallback": "MANUAL_BROKER_UI_FALLBACK_REQUIRED",
    }


def test_auto_exit_live_readiness_stays_false_even_with_policy_evidence():
    result = build_auto_exit_live_readiness_model(
        policy_evidence=policy_evidence(),
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["AUTO_EXIT_LIVE_READY"] is False
    assert result["live_execution_allowed"] is False
    assert result["stop_loss_required"] is True
    assert result["stop_loss_ready"] is True
    assert result["manual_broker_ui_fallback_required"] is True
    assert result["broker_write_calls_allowed"] is False
    assert result["close_trade_allowed"] is False
    assert "auto_exit_readiness_not_implemented_for_live_execution" in result["blocked_reasons"]


def test_auto_exit_missing_policy_evidence_adds_policy_blockers():
    result = build_auto_exit_live_readiness_model(
        policy_evidence={},
        generated_at_utc="2026-06-19T00:00:00Z",
    )

    assert result["AUTO_EXIT_LIVE_READY"] is False
    assert "stop_loss_policy_missing_for_live_exit" in result["blocked_reasons"]
    assert "take_profit_policy_missing_for_live_exit" in result["blocked_reasons"]
    assert result["live_execution_allowed"] is False


def test_auto_exit_report_and_summary_are_sanitized():
    result = build_auto_exit_live_readiness_model(
        policy_evidence=policy_evidence(),
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
