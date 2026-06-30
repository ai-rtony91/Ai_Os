from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.capital_rail_withdrawal_plan_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_capital_rail_withdrawal_plan_v1,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "capital_rail_withdrawal_plan_v1.py"
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
    return evaluate_capital_rail_withdrawal_plan_v1(payload)


def _common_bucket_payload() -> dict:
    return {
        "reserve_requirements": {
            "operating_reserve_current": 2000,
            "tax_reserve_current": 1000,
            "operating_reserve_met": True,
            "tax_reserve_met": True,
            "operating_reserve_percent": 10,
            "tax_reserve_percent": 10,
        },
        "withdrawal_bucket_status": {
            "status": "REVIEW_ONLY",
            "eligible_amount": 1200,
        },
        "bucket_state": {
            "pending_withdrawal_bucket": 0,
            "withdrawal_bucket": 1200,
        },
        "blocked_reasons": [],
        "stale_bucket_flags": ["buckets_are_current"],
    }


def _common_rail_payload() -> dict:
    return {
        "rail_registry": [
            {
                "rail_id": "r1",
                "fee_estimate_usd": 8,
                "processing_time_estimate": "same day",
                "active": True,
                "withdrawal_supported": True,
                "same_name_verified": True,
                "same_name_proof_required": True,
            }
        ],
        "eligible_rails": ["r1"],
        "lowest_cost_rail": {"rail_id": "r1"},
        "fastest_rail": {"rail_id": "r1"},
        "same_name_proof_required": True,
        "same_name_proof_status": {"satisfied": True, "missing_rail_proofs": []},
        "blocked_rails": [],
    }


def _common_cadence_payload() -> dict:
    return {
        "recommended_cadence": "monthly",
        "withdrawal_eligibility": {"eligible_for_owner_review": True},
        "risk_blocks": [],
        "blocked_reasons": [],
        "monthly_plan": {"eligible": True, "next_review_date": "2026-07-15"},
        "weekly_plan": {"eligible": True, "next_review_date": "2026-07-08"},
        "bimonthly_plan": {"eligible": True, "next_review_date": "2026-07-22"},
    }


def test_readies_only_when_all_gates_pass() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": _common_bucket_payload(),
            "rail_registry": _common_rail_payload(),
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["withdrawal_plan_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["eligible_for_owner_review"] is True
    assert result["recommended_cadence"] == "monthly"
    assert result["manual_execution_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["bank_access_allowed"] is False


def test_blocked_by_risk_when_margin_or_risk_flags_present() -> None:
    bucket = _common_bucket_payload()
    bucket["margin_or_open_risk_block"] = True
    result = evaluate(
        {
            "bucket_purge_controller": bucket,
            "rail_registry": _common_rail_payload(),
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    assert result["withdrawal_plan_status"] == "BLOCKED_BY_RISK"
    assert "margin_or_open_risk_block" in result["blocked_reasons"]
    assert result["eligible_for_owner_review"] is False


def test_blocked_by_rail_when_rail_proof_missing() -> None:
    rail = _common_rail_payload()
    rail["same_name_proof_status"]["satisfied"] = False
    result = evaluate(
        {
            "bucket_purge_controller": _common_bucket_payload(),
            "rail_registry": rail,
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    assert result["withdrawal_plan_status"] == "BLOCKED_BY_RAIL"
    assert result["rail_proof_required"] is True


def test_blocked_by_reserve_when_underfunded() -> None:
    bucket = _common_bucket_payload()
    bucket["reserve_requirements"]["operating_reserve_met"] = False
    bucket["reserve_requirements"]["tax_reserve_met"] = False
    result = evaluate(
        {
            "bucket_purge_controller": bucket,
            "rail_registry": _common_rail_payload(),
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    assert result["withdrawal_plan_status"] == "BLOCKED_BY_RESERVE"
    assert any("underfund" in reason for reason in result["blocked_reasons"])

    assert result["reserve_summary"]["bucket_eligibility"] is False


def test_blocked_by_sensitive_data() -> None:
    result = evaluate({"routing_number": "111000025", "bucket_purge_controller": _common_bucket_payload()})
    assert result["withdrawal_plan_status"] == "BLOCKED_BY_SENSITIVE_DATA"
    assert result["eligible_for_owner_review"] is False
    assert "sensitive_financial_data_provided" in result["blocked_reasons"]


def test_includes_owner_gate_and_manual_execution_only() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": _common_bucket_payload(),
            "rail_registry": _common_rail_payload(),
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    owner_gate = result["owner_gate"]
    assert owner_gate["owner_name"] == "Anthony"
    assert owner_gate["approval_required"] is True
    assert owner_gate["approval_scope"] == "manual external withdrawal review only"
    assert owner_gate["execution_allowed"] is False
    assert result["manual_execution_only"] is True


def test_selected_review_rail_is_only_eligible_redacted_rail() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": _common_bucket_payload(),
            "rail_registry": {
                **_common_rail_payload(),
                "selected_review_rail": {"rail_id": "r1"},
            },
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    assert result["selected_review_rail"] is not None
    assert result["selected_review_rail"]["rail_id"] == "r1"


def test_outputs_weekly_monthly_bimonthly_sections() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": _common_bucket_payload(),
            "rail_registry": _common_rail_payload(),
            "withdrawal_cadence_planner": _common_cadence_payload(),
        }
    )
    assert result["withdrawal_plan_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["fee_summary"]["lowest_fee_rail"]["rail_id"] == "r1"
    assert isinstance(result["timing_summary"], dict)
    assert "next_review_day" in result["timing_summary"]


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source

