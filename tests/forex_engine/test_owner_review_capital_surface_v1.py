from __future__ import annotations

from pathlib import Path
import sys

from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.owner_review_capital_surface_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_owner_review_capital_surface_v1,
)

MODULE_PATH = ROOT / "automation" / "forex_engine" / "owner_review_capital_surface_v1.py"
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
    return evaluate_owner_review_capital_surface_v1(payload)


def test_output_is_read_only_and_permission_flags_blocked() -> None:
    result = evaluate({})
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["trade_execution_allowed"] is False
    assert result["owner_decision_required"] is True


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": {"bucket_state": {}},
            "capital_rail_registry": {},
            "withdrawal_cadence_planner": {},
            "capital_rail_withdrawal_plan": {},
            "routing_number": "redacted-routing",
        }
    )
    assert result["surface_status"] == "BLOCKED_BY_SENSITIVE_DATA"
    assert "sensitive_financial_data_provided" in result["blockers"]
    assert "redacted-routing" not in repr(result)


def test_ready_payload_returns_ready_for_owner_review() -> None:
    result = evaluate(
        {
            "as_of_date": datetime.utcnow().date().isoformat(),
            "owner_name": "Anthony",
            "bucket_purge_controller": {
                "bucket_state": {"status": "steady"},
                "stale_bucket_flags": ["buckets_are_current"],
                "purge_actions": [{"action": "noop"}],
                "rollover_actions": [{"action": "noop"}],
                "sweep_actions": [{"action": "noop"}],
                "withdrawal_bucket_status": {"status": "REVIEW_ONLY"},
                "reserve_requirements": {
                    "operating_reserve_met": True,
                    "tax_reserve_met": True,
                },
                "margin_or_open_risk_block": False,
                "daily_loss_stop_active": False,
            },
            "capital_rail_registry": {
                "eligible_rails": [{"rail_id": "r1"}],
                "blocked_rails": [],
                "lowest_cost_rail": {"rail_id": "r1"},
                "fastest_rail": {"rail_id": "r1"},
                "preferred_withdrawal_rail": {"rail_id": "r1"},
                "same_name_proof_status": {"required": True, "satisfied": True},
                "sensitive_data_blocked": False,
                "third_party_payment_blocked": False,
            },
            "withdrawal_cadence_planner": {
                "recommended_cadence": "monthly",
                "weekly_plan": {"eligible": True},
                "monthly_plan": {"eligible": True},
                "bimonthly_plan": {"eligible": False},
                "risk_blocks": [],
                "fee_efficiency": {"monthly": "good"},
            },
            "capital_rail_withdrawal_plan": {
                "withdrawal_plan_status": "READY_FOR_OWNER_REVIEW",
                "eligible_for_owner_review": True,
                "manual_execution_only": True,
                "selected_review_rail": {"rail_id": "r1"},
                "owner_gate": {"owner_name": "Anthony", "approval_required": True},
            },
            "oanda_funding_rail_readiness": {
                "readiness_status": "blocked",
                "same_name_bank_required": False,
                "withdrawal_hierarchy_notes": ["requires_manual_review"],
            },
            "big_winner_watchtower": {"alert_level": "BIG_WINNER_REVIEW"},
        }
    )
    assert result["surface_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["owner_name"] == "Anthony"
    assert result["capital_bucket_summary"]["purge_actions_count"] == 1
    assert result["capital_bucket_summary"]["rollover_actions_count"] == 1
    assert result["capital_bucket_summary"]["sweep_actions_count"] == 1
    assert result["rail_readiness_summary"]["eligible_rail_count"] == 1
    assert result["withdrawal_cadence_summary"]["recommended_cadence"] == "monthly"
    assert result["withdrawal_plan_summary"]["withdrawal_plan_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["safety"]["read_only"] is True


def test_risk_blocker_returns_blocked_by_risk() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": {
                "bucket_state": {},
                "purge_actions": [],
                "rollover_actions": [],
                "sweep_actions": [],
                "reserve_requirements": {
                    "operating_reserve_met": True,
                    "tax_reserve_met": True,
                },
                "margin_or_open_risk_block": True,
                "daily_loss_stop_active": False,
            },
            "capital_rail_registry": {
                "eligible_rails": [{"rail_id": "r1"}],
                "same_name_proof_status": {"required": False, "satisfied": True},
            },
            "withdrawal_cadence_planner": {
                "recommended_cadence": "monthly",
                "weekly_plan": {"eligible": True},
                "monthly_plan": {"eligible": True},
                "bimonthly_plan": {"eligible": True},
                "risk_blocks": [],
            },
            "capital_rail_withdrawal_plan": {
                "withdrawal_plan_status": "READY_FOR_OWNER_REVIEW",
                "eligible_for_owner_review": True,
                "manual_execution_only": True,
                "owner_gate": {"owner_name": "Anthony", "approval_required": True},
            },
        }
    )
    assert result["surface_status"] == "BLOCKED_BY_RISK"
    assert "margin_or_open_risk_block" in result["blockers"]


def test_rail_blocker_returns_blocked_by_rail() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": {
                "bucket_state": {},
                "purge_actions": [],
                "rollover_actions": [],
                "sweep_actions": [],
                "reserve_requirements": {
                    "operating_reserve_met": True,
                    "tax_reserve_met": True,
                },
            },
            "capital_rail_registry": {
                "eligible_rails": [],
                "blocked_rails": [{"rail_id": "r1"}],
                "same_name_proof_status": {"required": True, "satisfied": False},
                "sensitive_data_blocked": False,
                "third_party_payment_blocked": False,
            },
            "withdrawal_cadence_planner": {
                "recommended_cadence": "monthly",
                "weekly_plan": {"eligible": True},
                "monthly_plan": {"eligible": True},
                "bimonthly_plan": {"eligible": True},
                "risk_blocks": [],
            },
            "capital_rail_withdrawal_plan": {
                "withdrawal_plan_status": "BLOCKED_BY_RAIL",
                "eligible_for_owner_review": False,
                "manual_execution_only": True,
                "owner_gate": {"owner_name": "Anthony", "approval_required": True},
            },
        }
    )
    assert result["surface_status"] == "BLOCKED_BY_RAIL"
    assert result["rail_readiness_summary"]["same_name_proof_status"]["satisfied"] is False


def test_reserve_blocker_returns_blocked_by_reserve() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": {
                "bucket_state": {},
                "reserve_requirements": {
                    "operating_reserve_met": False,
                    "tax_reserve_met": False,
                },
                "purge_actions": [],
                "rollover_actions": [],
                "sweep_actions": [],
                "margin_or_open_risk_block": False,
                "daily_loss_stop_active": False,
            },
            "capital_rail_registry": {
                "eligible_rails": [{"rail_id": "r1"}],
                "same_name_proof_status": {"required": False, "satisfied": True},
            },
            "withdrawal_cadence_planner": {
                "recommended_cadence": "monthly",
                "weekly_plan": {"eligible": True},
                "monthly_plan": {"eligible": True},
                "bimonthly_plan": {"eligible": True},
                "risk_blocks": [],
            },
            "capital_rail_withdrawal_plan": {
                "withdrawal_plan_status": "READY_FOR_OWNER_REVIEW",
                "eligible_for_owner_review": True,
                "manual_execution_only": True,
                "owner_gate": {"owner_name": "Anthony", "approval_required": True},
            },
        }
    )
    assert result["surface_status"] == "BLOCKED_BY_RESERVE"


def test_incomplete_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["surface_status"] == "INCOMPLETE_INPUTS"
    assert "bucket_purge_controller" in result["missing_information"]
    assert "capital_rail_registry" in result["missing_information"]


def test_owner_review_cards_include_all_required_card_ids() -> None:
    result = evaluate(
        {
            "bucket_purge_controller": {
                "bucket_state": {},
                "reserve_requirements": {
                    "operating_reserve_met": True,
                    "tax_reserve_met": True,
                },
                "purge_actions": [],
                "rollover_actions": [],
                "sweep_actions": [],
            },
            "capital_rail_registry": {"eligible_rails": [{"rail_id": "r1"}]},
            "withdrawal_cadence_planner": {"recommended_cadence": "monthly"},
            "capital_rail_withdrawal_plan": {"withdrawal_plan_status": "READY_FOR_OWNER_REVIEW"},
        }
    )
    required_cards = {
        "CAPITAL_BUCKETS",
        "RAILS",
        "WITHDRAWAL_CADENCE",
        "WITHDRAWAL_PLAN",
        "OANDA_FUNDING",
        "BIG_WINNER_WATCHTOWER",
        "REMAINING_WORK",
    }
    assert required_cards == {card["card_id"] for card in result["owner_review_cards"]}
    for card in result["owner_review_cards"]:
        assert card["owner_decision_required"] is True
        assert card["execution_allowed"] is False


def test_safe_manual_next_action_does_not_request_money_movement() -> None:
    ready = evaluate(
        {
            "bucket_purge_controller": {
                "bucket_state": {},
                "reserve_requirements": {
                    "operating_reserve_met": True,
                    "tax_reserve_met": True,
                },
                "purge_actions": [],
                "rollover_actions": [],
                "sweep_actions": [],
            },
            "capital_rail_registry": {"eligible_rails": [{"rail_id": "r1"}]},
            "withdrawal_cadence_planner": {"recommended_cadence": "monthly"},
            "capital_rail_withdrawal_plan": {"withdrawal_plan_status": "READY_FOR_OWNER_REVIEW"},
        }
    )
    assert ready["safe_manual_next_action"] == (
        "Owner may review the capital withdrawal packet manually. AIOS does not move money, "
        "access banks, access brokers, or execute trades."
    )
    assert "money movement" not in ready["safe_manual_next_action"].lower()
    assert "execute money movement" not in ready["safe_manual_next_action"].lower()

    incomplete = evaluate({})
    assert incomplete["safe_manual_next_action"] == "Provide sanitized upstream read-only outputs, then rerun owner-review surface."
    assert "money movement" not in incomplete["safe_manual_next_action"].lower()


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
