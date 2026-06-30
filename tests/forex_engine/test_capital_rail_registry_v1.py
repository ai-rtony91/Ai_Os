from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.capital_rail_registry_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_capital_rail_registry_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "capital_rail_registry_v1.py"
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
    return evaluate_capital_rail_registry_v1(payload)


def test_output_is_read_only_and_money_movement_is_false() -> None:
    result = evaluate({})
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["owner_decision_required"] is True
    assert result["same_name_proof_required"] is False or result["same_name_proof_required"] is True


def test_redacted_rails_keep_last4_identity_only() -> None:
    result = evaluate(
        {
            "rails": [
                {
                    "rail_id": "r1",
                    "rail_type": "personal_bank_ach",
                    "nickname": "Business ACH",
                    "institution_name_redacted": "Bank X",
                    "last4_only": "1234",
                    "currency": "USD",
                    "same_name_verified": True,
                    "owner_verified": True,
                    "withdrawal_supported": True,
                    "active": True,
                    "fee_estimate_usd": 8.5,
                    "processing_time_estimate": "2 business days",
                }
            ]
        }
    )
    rail = result["rail_registry"][0]
    assert rail["last4_only"] == "1234"
    assert "account" not in str(rail).lower()
    assert result["eligible_rails"] == ["r1"]


def test_sensitive_rail_fields_are_rejected() -> None:
    result = evaluate(
        {
            "rails": [
                {
                    "rail_id": "r2",
                    "rail_type": "personal_bank_wire",
                    "routing_number": "111000025",
                    "account_number": "123456789",
                    "last4_only": "0000",
                    "active": True,
                }
            ]
        }
    )
    assert result["sensitive_data_blocked"] is True
    assert "sensitive_financial_data_provided" in result["blocked_reasons"]
    assert result["eligible_rails"] == []
    assert "111000025" not in repr(result)


def test_third_party_rails_are_blocked() -> None:
    result = evaluate(
        {
            "third_party_payment": True,
            "rails": [
                {
                    "rail_id": "r3",
                    "rail_type": "personal_bank_wire",
                    "active": True,
                    "withdrawal_supported": True,
                }
            ],
        }
    )
    assert result["third_party_payment_blocked"] is True
    assert "third_party_payment_blocked" in result["blocked_reasons"]


def test_same_name_verification_required() -> None:
    result = evaluate(
        {
            "rails": [
                {
                    "rail_id": "r4",
                    "rail_type": "oanda_ach",
                    "active": True,
                    "withdrawal_supported": True,
                    "same_name_verified": False,
                }
            ]
        }
    )
    assert result["same_name_proof_required"] is True
    status = result["same_name_proof_status"]
    assert status["satisfied"] is False
    assert "r4" in status["missing_rail_proofs"]


def test_selects_lowest_cost_and_fastest_rail_with_tie_break() -> None:
    result = evaluate(
        {
            "rails": [
                {
                    "rail_id": "r5",
                    "rail_type": "personal_bank_wire",
                    "active": True,
                    "withdrawal_supported": True,
                    "same_name_verified": True,
                    "owner_preferred": True,
                    "fee_estimate_usd": 40,
                    "processing_time_estimate": "3 business days",
                },
                {
                    "rail_id": "r6",
                    "rail_type": "oanda_domestic_wire",
                    "active": True,
                    "withdrawal_supported": True,
                    "same_name_verified": True,
                    "fee_estimate_usd": 40,
                    "processing_time_estimate": "same day",
                    "owner_preferred": False,
                },
                {
                    "rail_id": "r7",
                    "rail_type": "oanda_domestic_wire",
                    "active": False,
                    "withdrawal_supported": True,
                    "same_name_verified": True,
                    "fee_estimate_usd": 10,
                    "processing_time_estimate": "1 business day",
                },
            ]
        }
    )
    assert result["lowest_cost_rail"]["rail_id"] in {"r5", "r6"}
    assert result["fastest_rail"]["rail_id"] == "r6"
    assert any(item["rail_id"] == "r7" for item in result["blocked_rails"])


def test_no_sensitive_values_exposed() -> None:
    secret = "secret-token-000"
    result = evaluate(
        {
            "rails": [
                {
                    "rail_id": "r8",
                    "rail_type": "oanda_ach",
                    "active": True,
                    "withdrawal_supported": True,
                    "same_name_verified": True,
                    "token": secret,
                }
            ]
        }
    )
    assert secret not in repr(result)


def test_safety_prevents_money_or_bank_or_broker_execution() -> None:
    result = evaluate(
        {
            "rails": [
                {
                    "rail_id": "r9",
                    "rail_type": "personal_bank_wire",
                    "active": True,
                    "withdrawal_supported": True,
                    "same_name_verified": True,
                    "owner_preferred": True,
                }
            ]
        }
    )
    assert result["safety"]["no_transfer_tool"] is True
    assert result["safety"]["no_bank_connection"] is True
    assert result["safety"]["no_broker_connection"] is True
    assert result["safety"]["manual_execution_only"] is True


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source

