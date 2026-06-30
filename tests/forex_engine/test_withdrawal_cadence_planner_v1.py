from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.withdrawal_cadence_planner_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_withdrawal_cadence_planner_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "withdrawal_cadence_planner_v1.py"
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
    return evaluate_withdrawal_cadence_planner_v1(payload)


def test_output_is_read_only_and_no_money_movement() -> None:
    result = evaluate({"balance_bucket": "10000", "profit_bucket": "2000", "withdrawal_eligible_amount": "500"})
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert "weekly" in result["cadence_candidates"]
    assert result["owner_decision_required"] is True


def test_weekly_cadence_requires_strong_profit_low_fee_and_no_risk() -> None:
    result = evaluate(
        {
            "balance_bucket": "10000",
            "operating_reserve_bucket": "2000",
            "tax_reserve_bucket": "1500",
            "withdrawal_eligible_amount": "1200",
            "withdrawal_bucket_status": {"eligible_amount": "1200"},
            "min_withdrawal_threshold": "500",
            "min_operating_reserve_percent": "10",
            "min_tax_reserve_percent": "10",
            "max_withdrawal_fee_tolerance": "15",
            "profit_consistency_score": "0.9",
            "max_drawdown_percent": "1",
            "rail_registry": {
                "eligible_rails": ["r1"],
                "rail_registry": [
                    {
                        "rail_id": "r1",
                        "fee_estimate_usd": "4",
                        "processing_time_estimate": "instant",
                        "active": True,
                        "withdrawal_supported": True,
                        "same_name_verified": True,
                    }
                ],
                "same_name_proof_status": {"satisfied": True, "missing_rail_proofs": []},
                "same_name_proof_required": True,
                "lowest_cost_rail": {"rail_id": "r1"},
                "fastest_rail": {"rail_id": "r1"},
            },
        }
    )
    assert result["recommended_cadence"] in {"weekly", "monthly"}
    assert result["weekly_plan"]["eligible"] is True
    assert result["weekly_plan"]["selection_gate"] == "eligible_for_owner_review"


def test_monthly_is_conservative_default() -> None:
    result = evaluate(
        {
            "balance_bucket": "10000",
            "operating_reserve_bucket": "2000",
            "tax_reserve_bucket": "2000",
            "withdrawal_eligible_amount": "800",
            "min_withdrawal_threshold": "500",
            "max_withdrawal_fee_tolerance": "1",
            "profit_consistency_score": "0.3",
            "rail_registry": {
                "eligible_rails": ["r2"],
                "rail_registry": [
                    {
                        "rail_id": "r2",
                        "fee_estimate_usd": "30",
                        "processing_time_estimate": "2 business days",
                        "active": True,
                        "withdrawal_supported": True,
                        "same_name_verified": True,
                    }
                ],
                "same_name_proof_status": {"satisfied": True, "missing_rail_proofs": []},
                "same_name_proof_required": True,
                "lowest_cost_rail": {"rail_id": "r2"},
                "fastest_rail": {"rail_id": "r2"},
            },
        }
    )
    assert result["monthly_plan"]["selection_gate"] in {"eligible_for_owner_review", "not_eligible"}
    assert result["monthly_plan"]["cadence"] == "monthly"


def test_bimonthly_preferred_for_high_fees_or_thinner_profit() -> None:
    result = evaluate(
        {
            "balance_bucket": "10000",
            "operating_reserve_bucket": "2000",
            "tax_reserve_bucket": "2000",
            "withdrawal_eligible_amount": "2000",
            "min_withdrawal_threshold": "200",
            "max_withdrawal_fee_tolerance": "10",
            "profit_consistency_score": "0.35",
            "min_withdrawal_consistency_score": "0.80",
            "rail_registry": {
                "eligible_rails": ["r3"],
                "rail_registry": [
                    {
                        "rail_id": "r3",
                        "fee_estimate_usd": "40",
                        "processing_time_estimate": "3 business days",
                        "active": True,
                        "withdrawal_supported": True,
                        "same_name_verified": True,
                    }
                ],
                "same_name_proof_status": {"satisfied": True, "missing_rail_proofs": []},
                "same_name_proof_required": True,
                "lowest_cost_rail": {"rail_id": "r3"},
                "fastest_rail": {"rail_id": "r3"},
            },
        }
    )
    assert result["bimonthly_plan"]["eligible"] is True
    assert result["recommended_cadence"] in {"bimonthly", "monthly", "weekly"}


def test_no_withdrawal_when_no_profit() -> None:
    result = evaluate(
        {
            "withdrawal_eligible_amount": "0",
            "rail_registry": {"same_name_proof_required": True, "same_name_proof_status": {}},
        }
    )
    assert result["recommended_cadence"] == "no_withdrawal"
    assert result["withdrawal_eligibility"]["eligible_for_owner_review"] is False


def test_no_withdrawal_when_drawdown_or_risk_block() -> None:
    result = evaluate(
        {
            "withdrawal_eligible_amount": "1000",
            "margin_used": "1",
            "max_withdrawal_fee_tolerance": "50",
            "max_drawdown_percent": "30",
            "max_drawdown_limit": "20",
            "rail_registry": {
                "eligible_rails": ["r4"],
                "rail_registry": [
                    {
                        "rail_id": "r4",
                        "fee_estimate_usd": "5",
                        "processing_time_estimate": "instant",
                        "active": True,
                        "withdrawal_supported": True,
                        "same_name_verified": True,
                    }
                ],
                "same_name_proof_status": {"satisfied": True, "missing_rail_proofs": []},
                "same_name_proof_required": True,
                "lowest_cost_rail": {"rail_id": "r4"},
                "fastest_rail": {"rail_id": "r4"},
            },
        }
    )
    assert result["recommended_cadence"] == "no_withdrawal"
    assert "margin_or_open_risk_block" in result["risk_blocks"]
    assert "drawdown_exceeded_limit" in result["risk_blocks"]


def test_no_withdrawal_when_reserve_underfunded_or_proof_missing() -> None:
    result = evaluate(
        {
            "balance_bucket": "10000",
            "operating_reserve_bucket": "100",
            "tax_reserve_bucket": "0",
            "withdrawal_eligible_amount": "1000",
            "min_withdrawal_threshold": "100",
            "operating_reserve_percent": "20",
            "tax_reserve_percent": "20",
            "rail_registry": {
                "same_name_proof_required": True,
                "same_name_proof_status": {"satisfied": False, "missing_rail_proofs": ["r5"]},
                "eligible_rails": [],
                "rail_registry": [],
            },
        }
    )
    assert result["recommended_cadence"] == "no_withdrawal"
    assert "rail_proof_missing" in result["risk_blocks"] or "no_eligible_rails" in result["risk_blocks"]


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source

