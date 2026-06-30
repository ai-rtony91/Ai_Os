from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_supervised_execution_prep_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_oanda_demo_supervised_execution_prep_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "oanda_demo_supervised_execution_prep_v1.py"
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
    return evaluate_oanda_demo_supervised_execution_prep_v1(payload)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "supervised_demo_readiness_packet": {
            "readiness_status": "SUPERVISED_DEMO_READY",
            "supervised_demo_ready": True,
            "readiness_score": 0.91,
            "next_best_packet": "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1",
            "readiness_blockers": [],
        },
        "owner_approval_gate": {
            "owner_approval_required": True,
            "owner_named_approval_required": True,
            "owner_review_required": True,
            "approval_packet_required": True,
            "final_execution_approval_collected": False,
            "execution_allowed": False,
            "owner_can_cancel": True,
            "manual_execution_only": True,
            "owner_approval_gate_score": 0.95,
        },
        "oanda_runtime_boundary": {
            "broker_name": "OANDA",
            "broker_mode": "OANDA_DEMO",
            "account_environment": "PRACTICE",
            "demo_account_only": True,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "broker_api_allowed": False,
            "trade_execution_allowed": False,
            "demo_execution_allowed": False,
            "order_placement_allowed": False,
            "credential_use_allowed": False,
            "credentials_persisted": False,
            "credentials_requested": False,
            "runtime_only_credentials_required": True,
            "owner_runtime_credential_entry_required": True,
            "credential_redaction_required": True,
            "secret_scan_required": True,
            "oanda_runtime_boundary_score": 0.96,
        },
        "candidate_ticket": {
            "strategy_id": "edge-reversion-v1",
            "candidate_id": "demo-candidate-001",
            "instrument": "EUR_USD",
            "side": "BUY",
            "timeframe": "M15",
            "setup_timestamp": "2026-06-30T13:00:00Z",
            "confidence_score": 0.72,
            "candidate_quality_score": 0.82,
            "evidence_reference": "sanitized-candidate-evidence",
            "ticket_score": 0.94,
            "ticket_blocks": [],
        },
        "order_intent": {
            "order_type": "PREP_ONLY",
            "units": 100,
            "max_position_units": 1000,
            "stop_loss_required": True,
            "stop_loss_pips": 10,
            "take_profit_required": True,
            "take_profit_pips": 15,
            "max_spread_pips": 2.0,
            "max_slippage_pips": 0.5,
            "one_order_only": True,
            "order_intent_score": 0.95,
            "order_intent_blocks": [],
        },
        "risk_gates": {
            "max_loss_gate_present": True,
            "daily_loss_stop_present": True,
            "kill_switch_present": True,
            "position_size_limit_present": True,
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "risk_reward_minimum": 1.2,
            "account_risk_mode": "demo_micro",
            "risk_gate_score": 0.94,
            "risk_gate_blocks": [],
        },
        "order_safety": {
            "pair_whitelist_present": True,
            "spread_check_required": True,
            "slippage_check_required": True,
            "stop_loss_validation_required": True,
            "take_profit_validation_required": True,
            "duplicate_order_check_required": True,
            "market_open_check_required": True,
            "order_preview_required": True,
            "order_safety_score": 0.95,
            "order_safety_blocks": [],
        },
        "telemetry_plan": {
            "audit_log_required": True,
            "sanitized_ticket_required": True,
            "pre_trade_snapshot_required": True,
            "order_preview_snapshot_required": True,
            "post_trade_snapshot_required": True,
            "exception_capture_required": True,
            "owner_review_report_required": True,
            "telemetry_plan_score": 0.91,
            "telemetry_blocks": [],
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
            "abort_condition_score": 0.95,
            "abort_condition_blocks": [],
        },
        "data_quality": {
            "data_quality_score": 0.90,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_tickets": 0,
            "malformed_timestamps": 0,
        },
        "readiness_snapshot": {
            "execution_prep_score": 0.93,
        },
        "remaining_work_closure_index": {
            "remaining_lanes": [
                {
                    "lane_id": "OANDA_DEMO_SUPERVISED_EXECUTION_PREP",
                    "title": "OANDA demo supervised execution prep",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1",
                },
                {
                    "lane_id": "OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF",
                    "title": "OANDA demo owner-approved runtime handoff",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1",
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
    assert result["prep_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert result["prep_ready"] is False
    assert result["runtime_handoff_ready"] is False
    assert result["supervised_demo_execution_authorized"] is False
    assert "sensitive_data_provided" in result["prep_blockers"]
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
    assert result["prep_status"] == "OANDA_DEMO_EXECUTION_PREP_READY"
    assert "sensitive_data_provided" not in result["prep_blockers"]

    payload["broker_api_allowed"] = True
    blocked = evaluate(payload)
    assert blocked["prep_status"] == "BLOCKED_BY_OANDA_RUNTIME_BOUNDARY"
    assert "broker_api_allowed_true" in blocked["prep_blockers"]


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["prep_status"] == "INCOMPLETE_INPUTS"
    for missing in [
        "supervised_demo_readiness_packet",
        "owner_approval_gate",
        "oanda_runtime_boundary",
        "candidate_ticket",
        "order_intent",
        "risk_gates",
        "order_safety",
        "telemetry_plan",
        "abort_conditions",
    ]:
        assert missing in result["missing_information"]


def test_weak_supervised_demo_readiness_returns_blocked_by_supervised_demo_readiness() -> None:
    payload = strong_payload()
    payload["supervised_demo_readiness_packet"]["supervised_demo_ready"] = False
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_SUPERVISED_DEMO_READINESS"
    assert "supervised_demo_ready_false" in result["prep_blockers"]


def test_weak_owner_approval_gate_returns_blocked_by_owner_approval_gate() -> None:
    payload = strong_payload()
    payload["owner_approval_gate"]["execution_allowed"] = True
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_OWNER_APPROVAL_GATE"
    assert "execution_allowed_true" in result["prep_blockers"]


def test_weak_oanda_runtime_boundary_returns_blocked_by_oanda_runtime_boundary() -> None:
    payload = strong_payload()
    payload["oanda_runtime_boundary"]["demo_execution_allowed"] = True
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_OANDA_RUNTIME_BOUNDARY"
    assert "demo_execution_allowed_true" in result["prep_blockers"]


def test_weak_candidate_ticket_returns_blocked_by_candidate_ticket() -> None:
    payload = strong_payload()
    payload["candidate_ticket"]["side"] = "WAIT"
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_CANDIDATE_TICKET"
    assert "side_not_supported" in result["prep_blockers"]


def test_weak_order_intent_returns_blocked_by_order_intent() -> None:
    payload = strong_payload()
    payload["order_intent"]["units"] = 1200
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_ORDER_INTENT"
    assert "units_above_max_position_units" in result["prep_blockers"]


def test_weak_risk_gates_returns_blocked_by_risk_gates() -> None:
    payload = strong_payload()
    payload["risk_gates"]["max_risk_per_trade_pct"] = 0.02
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_RISK_GATES"
    assert "max_risk_per_trade_pct_above_limit" in result["prep_blockers"]


def test_weak_order_safety_returns_blocked_by_order_safety() -> None:
    payload = strong_payload()
    payload["order_safety"]["duplicate_order_check_required"] = False
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_ORDER_SAFETY"
    assert "duplicate_order_check_required_false" in result["prep_blockers"]


def test_weak_telemetry_plan_returns_blocked_by_telemetry_plan() -> None:
    payload = strong_payload()
    payload["telemetry_plan"]["audit_log_required"] = False
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_TELEMETRY_PLAN"
    assert "audit_log_required_false" in result["prep_blockers"]


def test_weak_abort_conditions_returns_blocked_by_abort_conditions() -> None:
    payload = strong_payload()
    payload["abort_conditions"]["abort_if_kill_switch_active"] = False
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_ABORT_CONDITIONS"
    assert "abort_if_kill_switch_active_false" in result["prep_blockers"]


def test_weak_data_quality_returns_blocked_by_data_quality() -> None:
    payload = strong_payload()
    payload["data_quality"]["data_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["prep_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "data_quality_score_below_threshold" in result["prep_blockers"]


def test_strong_prep_evidence_returns_oanda_demo_execution_prep_ready() -> None:
    result = evaluate(strong_payload())
    assert result["prep_status"] == "OANDA_DEMO_EXECUTION_PREP_READY"
    assert result["prep_ready"] is True
    assert result["runtime_handoff_ready"] is True
    assert result["execution_prep_score"] == 0.93


def test_strong_prep_routes_next_best_packet_to_owner_runtime_handoff() -> None:
    result = evaluate(strong_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF_V1"
    assert result["next_remaining_lane"]["lane_id"] == "OANDA_DEMO_OWNER_APPROVED_RUNTIME_HANDOFF"


def test_blocked_evidence_keeps_this_packet_as_next_best_packet() -> None:
    payload = strong_payload()
    payload["telemetry_plan"]["exception_capture_required"] = False
    result = evaluate(payload)
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1"


def test_sanitized_execution_prep_package_contains_no_sensitive_values() -> None:
    result = evaluate(strong_payload())
    package = result["sanitized_execution_prep_package"]
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
    assert "REVIEW_SANITIZED_EXECUTION_PREP_PACKAGE" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["owner_action_queue"])
    assert all(action["execution_allowed"] is False for action in result["owner_action_queue"])


def test_readiness_never_authorizes_live_demo_or_order_execution() -> None:
    result = evaluate(strong_payload())
    assert result["prep_ready"] is True
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
    blocked["order_safety"]["market_open_check_required"] = False
    results.append(evaluate(blocked)["safe_manual_next_action"])
    for action in results:
        lowered = action.lower()
        for phrase in phrases:
            assert phrase not in lowered


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
