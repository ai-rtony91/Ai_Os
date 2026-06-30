from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.capital_bucket_purge_controller_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_capital_bucket_purge_controller_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "capital_bucket_purge_controller_v1.py"
FORBIDDEN_SOURCE_MARKERS = (
    "requests",
    "socket",
    "urllib",
    "subprocess",
    "os.environ",
    "broker_sdk",
    "schedule.every",
    "start-process",
)


def evaluate(payload: dict | None = None) -> dict:
    return evaluate_capital_bucket_purge_controller_v1(payload)


def test_output_is_read_only_and_money_movement_blocked() -> None:
    result = evaluate({})
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["owner_decision_required"] is True


def test_stale_bucket_flags_detected_and_purge_suggested() -> None:
    result = evaluate(
        {
            "as_of_date": "2026-06-30",
            "balance_bucket": "10000",
            "bucket_last_purged_at": "2026-06-01",
            "bucket_last_rolled_at": "2026-06-01",
            "purge_frequency_days": 7,
            "rollover_frequency_days": 14,
        }
    )

    assert "balance_bucket_stale_for_purge" in result["stale_bucket_flags"]
    assert any(action["action"] == "balance_bucket_stale_for_purge" for action in result["purge_actions"])
    assert result["audit_record"]["audit_history_deleted"] is False


def test_rollover_and_sweep_are_read_only_proposals() -> None:
    result = evaluate(
        {
            "as_of_date": "2026-06-30",
            "balance_bucket": "10000",
            "bucket_last_purged_at": "2026-06-20",
            "bucket_last_rolled_at": "2026-06-01",
            "purge_frequency_days": 90,
            "rollover_frequency_days": 7,
            "profit_bucket": "3000",
            "realized_profit_period": "1200",
            "owner_approved_rollover": True,
            "owner_approved_purge": True,
            "owner_approved_sweep": True,
        }
    )
    assert result["rollover_actions"]
    assert result["sweep_actions"]
    assert result["sweep_actions"][0]["action_type"] == "read_only_sweep"
    assert result["rollover_actions"][0]["action_type"] == "read_only_rollover"
    allocation = result["sweep_actions"][0]["proposed_bucket_allocation"]
    assert "tax_reserve_bucket_delta" in allocation
    assert "operating_reserve_bucket_delta" in allocation
    assert "withdrawal_bucket_delta" in allocation


def test_margin_or_open_risk_blocks_withdrawal_release() -> None:
    with_margin = evaluate({"balance_bucket": "10000", "margin_used": "1"})
    with_risk = evaluate({"balance_bucket": "10000", "open_risk": "0.5"})
    for result in (with_margin, with_risk):
        assert result["withdrawal_bucket_status"]["margin_or_open_risk_block"] is True
        assert result["withdrawal_bucket_status"]["pending_review_release"] is True
        assert "margin_or_open_risk_block" in result["blocked_reasons"] or any(
            "margin" in item for item in result["blocked_reasons"]
        )


def test_realized_loss_reduces_withdrawal_eligibility_and_sets_priority_blockers() -> None:
    no_loss = evaluate({"balance_bucket": "10000", "profit_bucket": "1000"})
    with_loss = evaluate({"balance_bucket": "10000", "profit_bucket": "1000", "realized_loss_period": "600"})
    assert no_loss["withdrawal_bucket_status"]["eligible_amount"] >= with_loss["withdrawal_bucket_status"]["eligible_amount"]
    assert "realized_loss_requires_reserve_rebuild" in with_loss["blocked_reasons"]


def test_daily_loss_stop_blocks_plan_generation() -> None:
    result = evaluate(
        {
            "balance_bucket": "10000",
            "daily_loss_used": "100",
            "max_daily_loss": "100",
            "profit_bucket": "5000",
        }
    )
    assert "daily_loss_stop_active" in result["blocked_reasons"]
    assert result["withdrawal_bucket_status"]["daily_loss_stop_active"] is True


def test_reserve_buckets_are_protected() -> None:
    result = evaluate(
        {
            "balance_bucket": "10000",
            "operating_reserve_bucket": "1000",
            "tax_reserve_bucket": "1000",
            "min_operating_reserve_percent": "20",
            "min_tax_reserve_percent": "20",
            "withdrawal_bucket": "1000",
        }
    )
    assert result["operating_reserve_status"]["protected"] is True
    assert result["tax_reserve_status"]["protected"] is True
    assert result["compounding_status"]["no_capital_reduction"] is True


def test_sensitive_financial_data_is_blocked_and_not_echoed() -> None:
    redacted_numeric_value = "REDACTED_ROUTING_NUMBER"
    result = evaluate(
        {
            "balance_bucket": "1000",
            "routing_number": redacted_numeric_value,
        }
    )
    assert result["blocked_reasons"] == ["sensitive_financial_data_provided"]
    assert "routing_number" not in repr(result)
    assert redacted_numeric_value not in repr(result)


def test_owner_approval_requirements_are_reflected_in_actions() -> None:
    result = evaluate(
        {
            "as_of_date": "2026-06-30",
            "balance_bucket": "10000",
            "profit_bucket": "2000",
            "bucket_last_purged_at": "2026-06-20",
            "bucket_last_rolled_at": "2026-06-20",
            "purge_frequency_days": 7,
            "rollover_frequency_days": 14,
        }
    )
    assert result["purge_actions"] and all(
        action["owner_review_state"] == "PENDING_REVIEW_APPROVAL"
        for action in result["purge_actions"]
    )


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source

