from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.capital_withdrawal_owner_review_workflow_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_capital_withdrawal_owner_review_workflow_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "capital_withdrawal_owner_review_workflow_v1.py"
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

REQUIRED_CHECKLIST_IDS = {
    "CONFIRM_OWNER_IDENTITY",
    "REVIEW_WITHDRAWAL_CADENCE",
    "REVIEW_PROTECTED_RESERVES",
    "REVIEW_RISK_BLOCKERS",
    "REVIEW_RAIL_PROOF",
    "REVIEW_SELECTED_RAIL",
    "REVIEW_BUCKET_PURGE_STATE",
    "REVIEW_FEE_AND_TIMING",
    "REVIEW_OANDA_HIERARCHY",
    "CONFIRM_MANUAL_EXECUTION_ONLY",
    "CONFIRM_NO_AI_EXECUTION",
}


def evaluate(payload: dict | None = None) -> dict:
    return evaluate_capital_withdrawal_owner_review_workflow_v1(payload)


def _ready_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "owner_review_dashboard_surfacing": {
            "dashboard_status": "READY_FOR_OWNER_REVIEW",
            "dashboard_cards": [],
            "dashboard_summary": {
                "next_best_packet": "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1",
                "recommended_cadence": "monthly",
            },
            "owner_action_queue": [],
            "blocker_summary": {"all_blockers": []},
            "missing_information": [],
            "remaining_work_summary": {},
            "safe_manual_next_action": "Owner may review manually.",
            "display_contract": {"display_only": True},
            "safety": {"manual_execution_only": True},
        },
        "owner_review_capital_surface": {
            "surface_status": "READY_FOR_OWNER_REVIEW",
            "capital_bucket_summary": {
                "margin_or_open_risk_block": False,
                "daily_loss_stop_active": False,
            },
            "rail_readiness_summary": {},
            "withdrawal_cadence_summary": {"recommended_cadence": "monthly"},
            "withdrawal_plan_summary": {
                "withdrawal_plan_status": "READY_FOR_OWNER_REVIEW",
                "eligible_for_owner_review": True,
                "selected_review_rail": {"rail_id": "r1"},
                "manual_execution_only": True,
            },
            "protected_reserve_summary": {
                "status": {"operating_reserve_met": True, "tax_reserve_met": True},
            },
            "blockers": [],
            "missing_information": [],
            "safe_manual_next_action": "Owner may review manually.",
            "safety": {"manual_execution_only": True},
        },
        "capital_rail_withdrawal_plan": {
            "withdrawal_plan_status": "READY_FOR_OWNER_REVIEW",
            "eligible_for_owner_review": True,
            "recommended_cadence": "monthly",
            "withdrawal_bucket": {"status": "REVIEW_ONLY"},
            "protected_buckets": ["tax_reserve_bucket", "operating_reserve_bucket"],
            "reserve_summary": {"operating_reserve_met": True, "tax_reserve_met": True},
            "rail_summary": {"eligible_rail_ids": ["r1"]},
            "selected_review_rail": {"rail_id": "r1"},
            "fee_summary": {"lowest_fee_rail": {"rail_id": "r1"}},
            "timing_summary": {"next_review_date": "2026-07-31"},
            "withdrawal_hierarchy_review": {"manual_review": True},
            "margin_call_review_required": False,
            "bucket_purge_required": False,
            "rail_proof_required": False,
            "owner_gate": {"approval_required": True},
            "manual_execution_only": True,
            "blocked_reasons": [],
            "missing_information": [],
            "safe_next_action": "Owner may review manually.",
            "audit_record": {"status": "READY_FOR_OWNER_REVIEW"},
            "safety": {"manual_execution_only": True},
        },
        "withdrawal_cadence_planner": {
            "recommended_cadence": "monthly",
            "weekly_plan": {"eligible": True},
            "monthly_plan": {"eligible": True},
            "bimonthly_plan": {"eligible": False},
            "no_withdrawal_plan": {"blocked_reasons": []},
            "withdrawal_eligibility": {
                "eligible_for_owner_review": True,
                "margin_or_open_risk_block": False,
                "daily_loss_stop_active": False,
            },
            "reserve_requirements": {"operating_reserve_met": True, "tax_reserve_met": True},
            "risk_blocks": [],
            "fee_efficiency": {"lowest_fee_rail": {"rail_id": "r1"}},
            "rail_readiness": {"eligible_count": 1},
            "blocked_reasons": [],
            "missing_information": [],
            "safe_next_action": "Owner may review manually.",
        },
        "capital_rail_registry": {
            "eligible_rails": ["r1"],
            "blocked_rails": [],
            "lowest_cost_rail": {"rail_id": "r1"},
            "fastest_rail": {"rail_id": "r1"},
            "preferred_withdrawal_rail": {"rail_id": "r1"},
            "same_name_proof_required": True,
            "same_name_proof_status": {"required": True, "satisfied": True},
            "third_party_payment_blocked": False,
            "sensitive_data_blocked": False,
            "missing_information": [],
            "blocked_reasons": [],
        },
        "capital_bucket_purge_controller": {
            "bucket_state": {"withdrawal_bucket": 1200},
            "stale_bucket_flags": ["buckets_are_current"],
            "purge_actions": [],
            "rollover_actions": [],
            "sweep_actions": [],
            "reserve_requirements": {"operating_reserve_met": True, "tax_reserve_met": True},
            "withdrawal_bucket_status": {
                "status": "REVIEW_ONLY",
                "margin_or_open_risk_block": False,
                "daily_loss_stop_active": False,
            },
            "blocked_reasons": [],
            "missing_information": [],
            "safe_next_action": "No immediate action.",
        },
        "remaining_work_closure_index": {
            "closure_index_status": "ACTIVE",
            "remaining_lanes": [
                {
                    "lane_id": "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW",
                    "title": "Capital withdrawal owner-review workflow",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "priority": "critical",
                    "safe_packet_name": "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1",
                },
                {
                    "lane_id": "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY",
                    "title": "Evidence depth / walk-forward sufficiency packet",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "priority": "high",
                    "safe_packet_name": "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1",
                },
            ],
            "recommended_sequence": [],
            "next_best_packet": "AIOS_FOREX_CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW_V1",
            "blocked_lanes": [],
            "deferred_lanes": [],
            "completion_policy": {"allowed_terminal_statuses": ["LANDED", "NEEDS_MORE_EVIDENCE"]},
        },
    }


def test_output_is_read_only_and_execution_flags_blocked() -> None:
    result = evaluate(_ready_payload())
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["trade_execution_allowed"] is False
    assert result["credential_use_allowed"] is False
    assert result["scheduler_created"] is False
    assert result["daemon_created"] is False
    assert result["webhook_created"] is False
    assert result["dashboard_runtime_created"] is False
    assert result["owner_decision_required"] is True
    assert result["safety"]["manual_execution_only"] is True


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    payload = _ready_payload()
    payload["routing_number"] = "secret-routing-value"
    result = evaluate(payload)
    assert result["workflow_status"] == "BLOCKED_BY_SENSITIVE_DATA"
    assert result["eligible_for_owner_review"] is False
    assert "sensitive_financial_data_provided" in result["blocker_summary"]["all_blockers"]
    assert "secret-routing-value" not in repr(result)


def test_complete_ready_inputs_return_ready_for_owner_review() -> None:
    result = evaluate(_ready_payload())
    assert result["workflow_status"] == "READY_FOR_OWNER_REVIEW"
    assert result["eligible_for_owner_review"] is True
    assert result["recommended_cadence"] == "monthly"
    assert result["withdrawal_review_packet"]["eligible_for_owner_review"] is True


def test_no_withdrawal_cadence_returns_no_withdrawal_recommended() -> None:
    payload = _ready_payload()
    payload["withdrawal_cadence_planner"]["recommended_cadence"] = "no_withdrawal"
    payload["capital_rail_withdrawal_plan"]["eligible_for_owner_review"] = False
    result = evaluate(payload)
    assert result["workflow_status"] == "NO_WITHDRAWAL_RECOMMENDED"
    assert result["eligible_for_owner_review"] is False


def test_risk_blocker_returns_blocked_by_risk() -> None:
    payload = _ready_payload()
    payload["capital_bucket_purge_controller"]["withdrawal_bucket_status"]["margin_or_open_risk_block"] = True
    result = evaluate(payload)
    assert result["workflow_status"] == "BLOCKED_BY_RISK"
    assert "margin_or_open_risk_block" in result["risk_gate_checklist"]["risk_blockers"]


def test_rail_blocker_returns_blocked_by_rail() -> None:
    payload = _ready_payload()
    payload["capital_rail_registry"]["same_name_proof_status"]["satisfied"] = False
    result = evaluate(payload)
    assert result["workflow_status"] == "BLOCKED_BY_RAIL"
    assert "same_name_proof_required" in result["rail_proof_checklist"]["rail_blockers"]


def test_reserve_blocker_returns_blocked_by_reserve() -> None:
    payload = _ready_payload()
    payload["capital_bucket_purge_controller"]["reserve_requirements"]["tax_reserve_met"] = False
    result = evaluate(payload)
    assert result["workflow_status"] == "BLOCKED_BY_RESERVE"
    assert "tax_reserve_underfunded" in result["reserve_gate_checklist"]["reserve_blockers"]


def test_incomplete_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["workflow_status"] == "INCOMPLETE_INPUTS"
    assert "owner_review_dashboard_surfacing" in result["missing_information"]


def test_owner_approval_checklist_includes_all_required_ids() -> None:
    result = evaluate(_ready_payload())
    checklist_ids = {item["checklist_id"] for item in result["owner_approval_checklist"]}
    assert REQUIRED_CHECKLIST_IDS.issubset(checklist_ids)
    assert all(item["execution_allowed"] is False for item in result["owner_approval_checklist"])


def test_manual_execution_packet_blocks_ai_and_money_movement() -> None:
    packet = evaluate(_ready_payload())["manual_execution_packet"]
    assert packet["manual_execution_only"] is True
    assert packet["ai_execution_allowed"] is False
    assert packet["money_movement_allowed"] is False
    assert packet["bank_access_allowed"] is False
    assert packet["broker_api_allowed"] is False
    assert packet["trade_execution_allowed"] is False
    assert packet["credential_use_allowed"] is False


def test_rail_proof_and_selected_rail_reviews_are_present() -> None:
    result = evaluate(_ready_payload())
    proof = result["rail_proof_checklist"]
    selected = result["selected_review_rail_review"]
    assert proof["same_name_proof_required"] is True
    assert proof["same_name_proof_satisfied"] is True
    assert proof["selected_review_rail"]["rail_id"] == "r1"
    assert selected["selected_rail_present"] is True
    assert selected["selected_rail_is_redacted"] is True
    assert selected["selected_rail_execution_allowed"] is False


def test_reserve_risk_and_bucket_reviews_include_required_fields() -> None:
    result = evaluate(_ready_payload())
    assert result["reserve_gate_checklist"]["tax_reserve_met"] is True
    assert result["reserve_gate_checklist"]["operating_reserve_met"] is True
    assert result["risk_gate_checklist"]["margin_or_open_risk_block"] is False
    assert result["risk_gate_checklist"]["daily_loss_stop_active"] is False
    assert result["bucket_purge_review"]["stale_bucket_flags"] == ["buckets_are_current"]
    assert result["bucket_purge_review"]["purge_actions_count"] == 0
    assert result["bucket_purge_review"]["rollover_actions_count"] == 0
    assert result["bucket_purge_review"]["sweep_actions_count"] == 0


def test_owner_action_queue_and_next_packet_advance_remaining_work() -> None:
    result = evaluate(_ready_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_REMAINING_WORK_PACKET" in action_ids
    assert result["next_best_packet"] == "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1"
    assert result["next_remaining_lane"]["lane_id"] == "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY"


def test_safe_manual_next_action_never_authorizes_execution() -> None:
    actions = [
        evaluate(_ready_payload())["safe_manual_next_action"],
        evaluate({})["safe_manual_next_action"],
    ]
    blocked_payload = _ready_payload()
    blocked_payload["capital_bucket_purge_controller"]["withdrawal_bucket_status"]["daily_loss_stop_active"] = True
    actions.append(evaluate(blocked_payload)["safe_manual_next_action"])
    for action in actions:
        lowered = action.lower()
        assert "withdraw now" not in lowered
        assert "move money" not in lowered or "does not move money" in lowered


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
