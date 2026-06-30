from __future__ import annotations

from pathlib import Path
import sys

from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_remaining_work_closure_index_v1 import (  # noqa: E402
    evaluate_forex_remaining_work_closure_index_v1,
)
from automation.forex_engine.owner_review_capital_surface_v1 import (  # noqa: E402
    evaluate_owner_review_capital_surface_v1,
)
from automation.forex_engine.owner_review_dashboard_surfacing_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_owner_review_dashboard_surfacing_v1,
)

MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "owner_review_dashboard_surfacing_v1.py"
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

REQUIRED_CARD_IDS = {
    "OWNER_REVIEW_STATUS",
    "CAPITAL_BUCKETS",
    "RAILS",
    "WITHDRAWAL_CADENCE",
    "WITHDRAWAL_PLAN",
    "OANDA_FUNDING",
    "BIG_WINNER_WATCHTOWER",
    "REMAINING_WORK",
    "NEXT_PACKET",
    "SAFETY_BOUNDARY",
}


def evaluate(payload: dict | None = None) -> dict:
    return evaluate_owner_review_dashboard_surfacing_v1(payload)


def _ready_owner_review_payload() -> dict:
    return evaluate_owner_review_capital_surface_v1(
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
                "readiness_status": "ready",
                "same_name_bank_required": False,
                "withdrawal_hierarchy_notes": ["requires_manual_review"],
            },
            "big_winner_watchtower": {
                "alert_level": "BIG_WINNER_REVIEW",
                "top_opportunity": {"pair": "EUR_USD", "direction": "buy"},
                "big_winner_candidate_count": 2,
            },
        }
    )


def _risk_owner_review_payload() -> dict:
    surface = _ready_owner_review_payload()
    surface["surface_status"] = "BLOCKED_BY_RISK"
    surface["blockers"].append("margin_or_open_risk_block")
    return surface


def _rail_owner_review_payload() -> dict:
    surface = _ready_owner_review_payload()
    surface["surface_status"] = "BLOCKED_BY_RAIL"
    surface["blockers"].append("same_name_proof_required")
    return surface


def _reserve_owner_review_payload() -> dict:
    surface = _ready_owner_review_payload()
    surface["surface_status"] = "BLOCKED_BY_RESERVE"
    surface["blockers"].append("protected_reserve_operating_not_met")
    surface["protected_reserve_summary"] = {
        "status": {
            "operating_reserve_met": False,
            "tax_reserve_met": False,
        }
    }
    return surface


def _remaining_work_payload() -> dict:
    return evaluate_forex_remaining_work_closure_index_v1(
        {
            "remaining_lanes": [
                {
                    "lane_id": "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW",
                    "title": "Owner review withdrawal workflow",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "priority": "critical",
                    "safe_packet_name": "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1",
                },
                {
                    "lane_id": "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY",
                    "title": "Evidence depth packet",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "priority": "high",
                    "safe_packet_name": "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1",
                },
                {
                    "lane_id": "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT",
                    "title": "Candidate quality packet",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "priority": "high",
                    "safe_packet_name": "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1",
                },
            ],
            "blocked_lanes": ["SOMETHING_BLOCKED"],
            "deferred_lanes": ["DEFERRED_ITEM"],
            "closure_index_status": "ACTIVE",
            "next_best_packet": "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1",
            "completion_policy": {
                "allowed_terminal_statuses": [
                    "LANDED",
                    "BLOCKED_WITH_REASON",
                    "DEFERRED_BY_OWNER",
                    "SUPERSEDED",
                    "NEEDS_MORE_EVIDENCE",
                ]
            },
        }
    )


def _payload_with_ready_inputs() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": datetime.utcnow().date().isoformat(),
        "owner_review_capital_surface": _ready_owner_review_payload(),
        "remaining_work_closure_index": _remaining_work_payload(),
    }


def test_output_is_read_only_and_permission_flags_blocked() -> None:
    result = evaluate({})
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["dashboard_runtime_created"] is False
    assert result["scheduler_created"] is False
    assert result["daemon_created"] is False
    assert result["webhook_created"] is False
    assert result["money_movement_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["trade_execution_allowed"] is False
    assert result["credential_use_allowed"] is False
    assert result["owner_decision_required"] is True
    assert result["safety"]["read_only"] is True
    assert result["safety"]["display_only"] is True
    assert result["safety"]["manual_execution_only"] is True
    assert result["safety"]["scheduler_allowed"] is False
    assert result["safety"]["daemon_allowed"] is False
    assert result["safety"]["webhook_allowed"] is False
    assert result["display_contract"]["display_only"] is True
    assert result["display_contract"]["mutates_repo"] is False


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    result = evaluate(
        {
            "owner_review_capital_surface": _ready_owner_review_payload(),
            "remaining_work_closure_index": _remaining_work_payload(),
            "routing_number": "redacted-routing",
        }
    )
    assert result["dashboard_status"] == "BLOCKED_BY_SENSITIVE_DATA"
    assert "sensitive_financial_data_provided" in result["blocker_summary"]["all_blockers"]
    assert "redacted-routing" not in repr(result)


def test_ready_inputs_return_ready_for_owner_review() -> None:
    result = evaluate(_payload_with_ready_inputs())
    assert result["dashboard_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["safe_manual_next_action"] == (
        "Owner may review dashboard cards manually. AIOS does not move money, access banks, "
        "access brokers, execute trades, or start dashboard runtimes."
    )
    assert result["owner_name"] == "Anthony"
    assert result["dashboard_summary"]["headline_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["dashboard_summary"]["next_best_packet"] == "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1"
    assert isinstance(result["dashboard_summary"]["watchlist_card_count"], int)


def test_risk_blocker_returns_blocked_by_risk() -> None:
    payload = {
        "owner_review_capital_surface": _risk_owner_review_payload(),
        "remaining_work_closure_index": _remaining_work_payload(),
    }
    result = evaluate(payload)
    assert result["dashboard_status"] == "BLOCKED_BY_RISK"
    assert result["blocker_summary"]["risk_blockers"]
    assert "margin_or_open_risk_block" in result["blocker_summary"]["risk_blockers"]


def test_rail_blocker_returns_blocked_by_rail() -> None:
    payload = {
        "owner_review_capital_surface": _rail_owner_review_payload(),
        "remaining_work_closure_index": _remaining_work_payload(),
    }
    result = evaluate(payload)
    assert result["dashboard_status"] == "BLOCKED_BY_RAIL"
    assert "same_name_proof_required" in result["blocker_summary"]["rail_blockers"]
    assert result["dashboard_summary"]["blocked_card_count"] >= 1


def test_reserve_blocker_returns_blocked_by_reserve() -> None:
    payload = {
        "owner_review_capital_surface": _reserve_owner_review_payload(),
        "remaining_work_closure_index": _remaining_work_payload(),
    }
    result = evaluate(payload)
    assert result["dashboard_status"] == "BLOCKED_BY_RESERVE"
    assert "protected_reserve_operating_not_met" in result["blocker_summary"]["reserve_blockers"]


def test_incomplete_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["dashboard_status"] == "INCOMPLETE_INPUTS"
    assert "owner_review_capital_surface" in result["missing_information"]
    assert "remaining_work_closure_index" in result["missing_information"]


def test_owner_review_dashboard_cards_include_all_required_ids() -> None:
    result = evaluate(_payload_with_ready_inputs())
    card_ids = {card["card_id"] for card in result["dashboard_cards"]}
    assert REQUIRED_CARD_IDS.issubset(card_ids)
    for card in result["dashboard_cards"]:
        if card["card_id"] in REQUIRED_CARD_IDS:
            assert card["owner_decision_required"] is True
            assert card["execution_allowed"] is False
            assert isinstance(card["sort_order"], int)


def test_dashboard_summary_includes_counts_and_next_best_packet() -> None:
    result = evaluate(_payload_with_ready_inputs())
    summary = result["dashboard_summary"]
    assert summary["owner_name"] == "Anthony"
    assert summary["next_best_packet"] == "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1"
    assert summary["ready_card_count"] >= 1
    assert summary["blocked_card_count"] >= 0
    assert isinstance(summary["top_blockers"], list)
    assert isinstance(summary["incomplete_card_count"], int)


def test_owner_action_queue_contains_next_remaining_work_action() -> None:
    result = evaluate(_payload_with_ready_inputs())
    action_ids = [action["action_id"] for action in result["owner_action_queue"]]
    assert "REVIEW_REMAINING_WORK_NEXT_PACKET" in action_ids


def test_blocker_summary_partitions_risk_rail_reserve_sensitive_and_incomplete() -> None:
    payload = _payload_with_ready_inputs()
    payload["owner_review_capital_surface"]["blockers"] = [
        "margin_or_open_risk_block",
        "same_name_proof_required",
        "protected_reserve_operating_not_met",
        "sensitive_financial_data_provided",
    ]
    result = evaluate(payload)
    assert result["blocker_summary"]["risk_blockers"]
    assert result["blocker_summary"]["rail_blockers"]
    assert result["blocker_summary"]["reserve_blockers"]
    assert result["blocker_summary"]["sensitive_data_blockers"] == []
    assert "all_blockers" in result["blocker_summary"]
    assert set(
        [
            "risk_blockers",
            "rail_blockers",
            "reserve_blockers",
            "sensitive_data_blockers",
            "incomplete_input_blockers",
            "remaining_work_blockers",
            "all_blockers",
        ]
    ) == set(result["blocker_summary"].keys())


def test_remaining_work_summary_has_lane_counts_and_top_lanes() -> None:
    result = evaluate(_payload_with_ready_inputs())
    remaining = result["remaining_work_summary"]
    assert remaining["remaining_lane_count"] == 3
    assert remaining["top_remaining_lanes"] == [
        "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW",
        "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY",
        "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT",
    ]
    assert remaining["next_best_packet"] == "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1"
    assert remaining["closure_index_status"] == "ACTIVE"
    assert remaining["completion_policy_statuses"]


def test_display_contract_is_display_only_and_mutation_free() -> None:
    result = evaluate(_payload_with_ready_inputs())
    display_contract = result["display_contract"]
    assert display_contract["display_only"] is True
    assert display_contract["mutates_repo"] is False
    assert display_contract["creates_dashboard_runtime"] is False
    assert display_contract["cards_are_projection_only"] is True
    assert display_contract["owner_action_required_for_real_world_steps"] is True


def test_safe_manual_next_action_never_authorizes_execution() -> None:
    ready = evaluate(_payload_with_ready_inputs())
    incomplete = evaluate({})
    blocked = evaluate(
            {
                "owner_review_capital_surface": _rail_owner_review_payload(),
                "remaining_work_closure_index": _remaining_work_payload(),
            }
        )
    for action in (
        ready["safe_manual_next_action"],
        incomplete["safe_manual_next_action"],
        blocked["safe_manual_next_action"],
    ):
        lower_action = action.lower()
        assert (
            "owner may review" in lower_action
            or "provide sanitized" in lower_action
            or "resolve dashboard blockers" in lower_action
        )
        if "provide sanitized" not in lower_action:
            assert "does not" in lower_action or "outside" in lower_action


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
