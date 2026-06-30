from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_funding_rail_readiness_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_oanda_funding_rail_readiness_v1,
)


MODULE_PATH = (
    ROOT / "automation" / "forex_engine" / "oanda_funding_rail_readiness_v1.py"
)
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
    return evaluate_oanda_funding_rail_readiness_v1(payload)


def test_output_is_read_only_and_money_movement_is_false() -> None:
    result = evaluate({"intended_deposit_method": "debit_card"})

    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["owner_decision_required"] is True
    assert result["safety"]["no_transfer_tool"] is True


def test_unknown_or_missing_deposit_method_blocks() -> None:
    missing = evaluate({})
    unknown = evaluate({"intended_deposit_method": "crypto"})

    for result in (missing, unknown):
        assert "missing_deposit_method" in result["blocked_reasons"]
        assert "intended_deposit_method" in result["missing_information"]
        assert result["deposit_readiness"]["status"] == "BLOCKED"


def test_lump_sum_without_amount_or_date_is_planning_only() -> None:
    result = evaluate({"intended_deposit_method": "ach"})

    assert result["lump_sum_readiness"]["status"] == "PLANNING_ONLY"
    assert "intended_lump_sum_amount" in result["missing_information"]
    assert "intended_funding_date" in result["missing_information"]
    assert "owner must decide amount/date outside AIOS" in result["safe_next_action"]


def test_debit_card_amount_over_20000_flags_monthly_limit() -> None:
    result = evaluate(
        {
            "intended_deposit_method": "debit_card",
            "intended_lump_sum_amount": "20000.01",
            "intended_funding_date": "2026-07-01",
        }
    )

    assert "debit_card_monthly_limit_exceeded" in result["blocked_reasons"]
    assert (
        "debit_card_monthly_limit_exceeded"
        in result["debit_card_readiness"]["blockers"]
    )


def test_ach_amount_over_50000_flags_transaction_limit() -> None:
    result = evaluate(
        {
            "intended_deposit_method": "ach",
            "intended_lump_sum_amount": "50000.01",
            "intended_funding_date": "2026-07-01",
        }
    )

    assert "ach_transaction_limit_exceeded" in result["blocked_reasons"]
    assert "ach_transaction_limit_exceeded" in result["ach_readiness"]["blockers"]


def test_wire_route_requires_same_name_bank_proof_and_fee_review() -> None:
    result = evaluate(
        {
            "intended_deposit_method": "wire_domestic",
            "intended_lump_sum_amount": "100000",
            "intended_funding_date": "2026-07-01",
            "account_name_match": True,
        }
    )

    assert "same_name_bank_proof_required" in result["blocked_reasons"]
    assert result["wire_readiness"]["same_name_bank_proof_required"] is True
    assert result["wire_readiness"]["fee_review_required"] is True
    assert result["fee_review_required"] is True
    assert result["limits"]["wire_deposit_max_limit"] == "none stated by OANDA source"


def test_third_party_payment_blocks_readiness() -> None:
    result = evaluate(
        {
            "intended_deposit_method": "ach",
            "third_party_payment": True,
        }
    )

    assert result["third_party_payment_blocked"] is True
    assert "third_party_payment_blocked" in result["blocked_reasons"]
    assert result["ach_readiness"]["status"] == "BLOCKED"


def test_sensitive_financial_data_is_blocked_and_not_echoed() -> None:
    sensitive_value = "111000025"
    result = evaluate(
        {
            "intended_deposit_method": "ach",
            "routing_number": sensitive_value,
            "nested": {"api_key": "sk-not-real"},
        }
    )

    assert "sensitive_financial_data_provided" in result["blocked_reasons"]
    assert result["safety"]["credentials_rejected"] is True
    assert sensitive_value not in repr(result)
    assert "sk-not-real" not in repr(result)
    assert "remove sensitive financial data" in result["safe_next_action"]


def test_margin_used_triggers_margin_call_review_required() -> None:
    result = evaluate(
        {
            "intended_deposit_method": "wire_international",
            "margin_used": "1",
        }
    )

    assert result["margin_call_review_required"] is True
    assert (
        result["withdrawal_readiness"]["margin_used_review_required"]
        is True
    )
    assert "margin_used_review_required" in result["blocked_reasons"]


def test_withdrawal_hierarchy_is_present() -> None:
    result = evaluate({"intended_deposit_method": "debit_card"})

    hierarchy = result["withdrawal_hierarchy"]
    assert "debit card deposit amounts" in hierarchy["multiple_method_rule"]
    assert hierarchy["wire_same_name_bank_required"] is True
    assert "account balance minus margin used" == hierarchy["available_withdrawal_rule"]


def test_source_contains_no_blocked_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()

    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
