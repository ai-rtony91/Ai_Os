from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_owner_approved_runtime_handoff_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_oanda_demo_owner_approved_runtime_handoff_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "oanda_demo_owner_approved_runtime_handoff_v1.py"
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
    return evaluate_oanda_demo_owner_approved_runtime_handoff_v1(payload)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "execution_prep_package": {
            "prep_status": "OANDA_DEMO_EXECUTION_PREP_READY",
            "prep_ready": True,
            "runtime_handoff_ready": True,
            "execution_prep_score": 0.94,
            "next_best_packet": "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1",
            "prep_blockers": [],
            "sanitized_execution_prep_package": {
                "strategy_id": "edge-reversion-v1",
                "candidate_id": "demo-candidate-001",
                "credentials_included": False,
                "order_placement_allowed": False,
            },
        },
        "owner_approval": {
            "owner_name": "Anthony",
            "owner_approval_required": True,
            "owner_named_approval_required": True,
            "owner_review_required": True,
            "owner_accepts_sanitized_package": True,
            "owner_accepts_demo_only_boundary": True,
            "owner_accepts_runtime_credential_entry": True,
            "owner_accepts_one_order_only": True,
            "owner_can_cancel": True,
            "execution_allowed": False,
            "owner_approval_score": 0.97,
        },
        "runtime_credential_boundary": {
            "credentials_included": False,
            "credentials_persisted": False,
            "credentials_requested": False,
            "credential_use_allowed": False,
            "runtime_credentials_required": True,
            "runtime_only_credentials_required": True,
            "owner_runtime_credential_entry_required": True,
            "credential_redaction_required": True,
            "secret_scan_required": True,
            "credential_boundary_score": 0.96,
        },
        "oanda_account_boundary": {
            "broker_name": "OANDA",
            "broker_mode": "OANDA_DEMO",
            "account_environment": "PRACTICE",
            "demo_account_only": True,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "bank_access_allowed": False,
            "money_movement_allowed": False,
            "broker_api_allowed": False,
            "trade_execution_allowed": False,
            "demo_execution_allowed": False,
            "order_placement_allowed": False,
            "oanda_account_boundary_score": 0.96,
        },
        "order_preview": {
            "strategy_id": "edge-reversion-v1",
            "candidate_id": "demo-candidate-001",
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "PREP_ONLY",
            "units": 100,
            "max_position_units": 1000,
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_spread_pips": 2.0,
            "max_slippage_pips": 0.5,
            "order_preview_snapshot_required": True,
            "order_preview_accepted_by_owner": True,
            "order_preview_score": 0.93,
            "order_preview_blocks": [],
        },
        "risk_gates": {
            "max_loss_gate_present": True,
            "daily_loss_stop_present": True,
            "kill_switch_present": True,
            "position_size_limit_present": True,
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "risk_reward_minimum": 1.2,
            "one_order_only": True,
            "risk_gate_score": 0.94,
            "risk_gate_blocks": [],
        },
        "abort_conditions": {
            "abort_if_owner_approval_missing": True,
            "abort_if_credentials_missing": True,
            "abort_if_broker_mode_not_demo": True,
            "abort_if_spread_above_max": True,
            "abort_if_slippage_above_max": True,
            "abort_if_stop_loss_missing": True,
            "abort_if_take_profit_missing": True,
            "abort_if_daily_loss_hit": True,
            "abort_if_kill_switch_active": True,
            "abort_if_duplicate_order_detected": True,
            "abort_if_wrong_account_detected": True,
            "abort_if_live_account_detected": True,
            "abort_condition_score": 0.96,
            "abort_condition_blocks": [],
        },
        "telemetry": {
            "audit_log_required": True,
            "sanitized_ticket_required": True,
            "pre_trade_snapshot_required": True,
            "order_preview_snapshot_required": True,
            "post_trade_snapshot_required": True,
            "exception_capture_required": True,
            "owner_review_report_required": True,
            "runtime_handoff_report_required": True,
            "telemetry_score": 0.90,
            "telemetry_blocks": [],
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "pnl_review_required": True,
            "risk_review_required": True,
            "execution_quality_review_required": True,
            "next_trade_blocked_until_review": True,
            "post_trade_review_score": 0.86,
            "post_trade_review_blocks": [],
        },
        "data_quality": {
            "data_quality_score": 0.90,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_tickets": 0,
            "malformed_timestamps": 0,
        },
        "readiness_snapshot": {
            "runtime_handoff_score": 0.94,
        },
        "remaining_work_closure_index": {
            "remaining_lanes": [
                {
                    "lane_id": "OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF",
                    "title": "OANDA demo owner-approved runtime handoff",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1",
                },
                {
                    "lane_id": "OANDA_DEMO_SUPERVISED_ORDER_EXECUTION",
                    "title": "OANDA demo supervised order execution",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1",
                },
            ]
        },
    }


def assert_safety_flags(result: dict) -> None:
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["money_movement_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["trade_execution_allowed"] is False
    assert result["demo_execution_allowed"] is False
    assert result["order_placement_allowed"] is False
    assert result["credential_use_allowed"] is False
    assert result["scheduler_created"] is False
    assert result["daemon_created"] is False
    assert result["webhook_created"] is False
    assert result["dashboard_runtime_created"] is False
    assert result["owner_decision_required"] is True
    assert result["owner_named_approval_required"] is True
    assert result["supervised_demo_execution_authorized"] is False
    assert result["safety"]["fixed_return_target_promised"] is False
    assert result["safety"]["profit_claim_authorized"] is False
    for key in [
        "money_movement_allowed",
        "bank_access_allowed",
        "broker_api_allowed",
        "trade_execution_allowed",
        "demo_execution_allowed",
        "order_placement_allowed",
        "credential_use_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
        "dashboard_runtime_allowed",
    ]:
        assert result["safety"][key] is False


def test_output_is_read_only_and_execution_flags_blocked() -> None:
    assert_safety_flags(evaluate(strong_payload()))


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    payload = strong_payload()
    payload["api_key"] = "very-sensitive-value"
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert result["runtime_handoff_ready"] is False
    assert result["supervised_demo_execution_authorized"] is False
    assert "sensitive_data_provided" in result["handoff_blockers"]
    assert "very-sensitive-value" not in repr(result)
    assert "Remove sensitive data" in result["safe_manual_next_action"]


def test_safety_boolean_keys_are_not_misclassified_as_sensitive() -> None:
    payload = strong_payload()
    payload["credential_use_allowed"] = False
    payload["broker_api_allowed"] = False
    payload["demo_execution_allowed"] = False
    payload["trade_execution_allowed"] = False
    payload["order_placement_allowed"] = False
    result = evaluate(payload)
    assert result["handoff_status"] == "OANDA_DEMO_RUNTIME_HANDOFF_READY"
    assert "sensitive_data_provided" not in result["handoff_blockers"]

    blocked_payload = strong_payload()
    blocked_payload["broker_api_allowed"] = True
    blocked = evaluate(blocked_payload)
    assert blocked["handoff_status"] == "BLOCKED_BY_OANDA_ACCOUNT_BOUNDARY"
    assert "broker_api_allowed_true" in blocked["handoff_blockers"]


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["handoff_status"] == "INCOMPLETE_INPUTS"
    for missing in [
        "execution_prep_package",
        "owner_approval",
        "runtime_credential_boundary",
        "oanda_account_boundary",
        "order_preview",
        "risk_gates",
        "abort_conditions",
        "telemetry",
        "post_trade_review",
    ]:
        assert missing in result["missing_information"]


def test_weak_execution_prep_returns_blocked_by_execution_prep() -> None:
    payload = strong_payload()
    payload["execution_prep_package"]["prep_ready"] = False
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_EXECUTION_PREP"
    assert "prep_ready_false" in result["handoff_blockers"]


def test_weak_owner_approval_returns_blocked_by_owner_approval() -> None:
    payload = strong_payload()
    payload["owner_approval"]["execution_allowed"] = True
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_OWNER_APPROVAL"
    assert "execution_allowed_true" in result["handoff_blockers"]


def test_weak_runtime_credential_boundary_returns_blocked_by_runtime_credential_boundary() -> None:
    payload = strong_payload()
    payload["runtime_credential_boundary"]["credentials_requested"] = True
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY"
    assert "credentials_requested_true" in result["handoff_blockers"]


def test_weak_oanda_account_boundary_returns_blocked_by_oanda_account_boundary() -> None:
    payload = strong_payload()
    payload["oanda_account_boundary"]["demo_execution_allowed"] = True
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_OANDA_ACCOUNT_BOUNDARY"
    assert "demo_execution_allowed_true" in result["handoff_blockers"]


def test_weak_order_preview_returns_blocked_by_order_preview() -> None:
    payload = strong_payload()
    payload["order_preview"]["side"] = "WAIT"
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_ORDER_PREVIEW"
    assert "side_not_supported" in result["handoff_blockers"]


def test_weak_risk_gates_returns_blocked_by_risk_gates() -> None:
    payload = strong_payload()
    payload["risk_gates"]["max_risk_per_trade_pct"] = 0.02
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_RISK_GATES"
    assert "max_risk_per_trade_pct_above_limit" in result["handoff_blockers"]


def test_weak_abort_conditions_returns_blocked_by_abort_conditions() -> None:
    payload = strong_payload()
    payload["abort_conditions"]["abort_if_live_account_detected"] = False
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_ABORT_CONDITIONS"
    assert "abort_if_live_account_detected_false" in result["handoff_blockers"]


def test_weak_telemetry_returns_blocked_by_telemetry() -> None:
    payload = strong_payload()
    payload["telemetry"]["audit_log_required"] = False
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_TELEMETRY"
    assert "audit_log_required_false" in result["handoff_blockers"]


def test_weak_post_trade_review_returns_blocked_by_post_trade_review() -> None:
    payload = strong_payload()
    payload["post_trade_review"]["next_trade_blocked_until_review"] = False
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_POST_TRADE_REVIEW"
    assert "next_trade_blocked_until_review_false" in result["handoff_blockers"]


def test_weak_data_quality_returns_blocked_by_data_quality() -> None:
    payload = strong_payload()
    payload["data_quality"]["data_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["handoff_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "data_quality_score_below_threshold" in result["handoff_blockers"]


def test_strong_handoff_evidence_returns_oanda_demo_runtime_handoff_ready() -> None:
    result = evaluate(strong_payload())
    assert result["handoff_status"] == "OANDA_DEMO_RUNTIME_HANDOFF_READY"
    assert result["runtime_handoff_ready"] is True
    assert result["runtime_handoff_score"] == 0.94


def test_strong_handoff_routes_next_best_packet_to_supervised_order_execution() -> None:
    result = evaluate(strong_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1"
    assert result["next_remaining_lane"]["lane_id"] == "OANDA_DEMO_SUPERVISED_ORDER_EXECUTION"


def test_blocked_evidence_keeps_this_packet_as_next_best_packet() -> None:
    payload = strong_payload()
    payload["telemetry"]["exception_capture_required"] = False
    result = evaluate(payload)
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1"


def test_sanitized_runtime_handoff_package_contains_no_sensitive_values() -> None:
    payload = strong_payload()
    payload["order_preview"]["notes"] = "very-sensitive-value"
    result = evaluate(payload)
    package = result["sanitized_runtime_handoff_package"]
    assert package["credentials_included"] is False
    assert package["execution_authorized"] is False
    assert package["order_placement_allowed"] is False
    assert package["strategy_id"] == "edge-reversion-v1"
    assert package["candidate_id"] == "demo-candidate-001"
    assert package["risk_limits"]["max_risk_per_trade_pct"] == 0.01
    assert "very-sensitive-value" not in repr(package)


def test_owner_action_queue_contains_review_next_packet() -> None:
    result = evaluate(strong_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert "REVIEW_SANITIZED_RUNTIME_HANDOFF_PACKAGE" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["owner_action_queue"])
    assert all(action["execution_allowed"] is False for action in result["owner_action_queue"])


def test_readiness_never_authorizes_live_demo_or_order_execution() -> None:
    result = evaluate(strong_payload())
    assert result["runtime_handoff_ready"] is True
    assert result["supervised_demo_execution_authorized"] is False
    assert result["trade_execution_allowed"] is False
    assert result["demo_execution_allowed"] is False
    assert result["order_placement_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["credential_use_allowed"] is False


def test_safe_manual_next_action_never_uses_execution_or_return_phrases() -> None:
    phrases = [
        "trade " + "now",
        "withdraw " + "now",
        "move " + "money",
        "guaranteed " + "return",
        "guaranteed " + "profit",
    ]
    results = [
        evaluate(strong_payload())["safe_manual_next_action"],
        evaluate({})["safe_manual_next_action"],
    ]
    blocked = strong_payload()
    blocked["order_preview"]["stop_loss_present"] = False
    results.append(evaluate(blocked)["safe_manual_next_action"])
    for action in results:
        lowered = action.lower()
        for phrase in phrases:
            assert phrase not in lowered


def test_threshold_overrides_cannot_weaken_guardrails() -> None:
    payload = strong_payload()
    payload["thresholds"] = {"min_runtime_handoff_score": 0.50}
    result = evaluate(payload)
    assert result["handoff_status"] == "NEEDS_MORE_EVIDENCE"
    assert "threshold_override_rejected" in result["handoff_blockers"]
    assert result["threshold_policy"]["active_thresholds"]["min_runtime_handoff_score"] == 0.92


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
