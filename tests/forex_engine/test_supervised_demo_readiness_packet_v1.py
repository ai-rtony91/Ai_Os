from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.supervised_demo_readiness_packet_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_supervised_demo_readiness_packet_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "supervised_demo_readiness_packet_v1.py"
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
    return evaluate_supervised_demo_readiness_packet_v1(payload)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "demo_candidate_review_readiness": {
            "readiness_status": "DEMO_REVIEW_READY",
            "demo_review_ready": True,
            "readiness_score": 0.86,
            "next_best_packet": "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1",
            "readiness_blockers": [],
        },
        "oanda_demo_boundary": {
            "broker_name": "OANDA",
            "broker_mode": "OANDA_DEMO",
            "demo_account_only": True,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "broker_api_allowed": False,
            "trade_execution_allowed": False,
            "demo_execution_allowed": False,
            "credential_use_allowed": False,
        },
        "owner_approval_gate": {
            "owner_approval_required": True,
            "owner_review_required": True,
            "owner_named_approval_required": True,
            "manual_execution_only": True,
            "execution_allowed": False,
            "approval_packet_required": True,
            "owner_can_cancel": True,
        },
        "runtime_credential_boundary": {
            "credentials_persisted": False,
            "credentials_requested": False,
            "runtime_only_credentials_required": True,
            "credential_redaction_required": True,
            "secret_scan_required": True,
            "credential_use_allowed": False,
        },
        "risk_controls": {
            "max_loss_gate_present": True,
            "daily_loss_stop_present": True,
            "kill_switch_present": True,
            "position_size_limit_present": True,
            "max_position_units": 1000,
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "risk_control_score": 0.91,
            "risk_blocks": [],
        },
        "order_safety": {
            "stop_loss_required": True,
            "take_profit_required": True,
            "one_order_only": True,
            "market_order_allowed": False,
            "pending_order_allowed": False,
            "order_size_capped": True,
            "pair_whitelist_present": True,
            "spread_check_required": True,
            "slippage_check_required": True,
            "order_safety_score": 0.93,
            "order_safety_blocks": [],
        },
        "telemetry": {
            "telemetry_score": 0.84,
            "audit_log_required": True,
            "sanitized_evidence_required": True,
            "pre_trade_snapshot_required": True,
            "post_trade_snapshot_required": True,
            "exception_capture_required": True,
            "owner_review_report_required": True,
            "telemetry_blocks": [],
        },
        "post_demo_review": {
            "post_demo_review_score": 0.80,
            "post_trade_review_required": True,
            "pnl_review_required": True,
            "risk_review_required": True,
            "execution_quality_review_required": True,
            "screenshot_or_snapshot_review_required": True,
            "next_trade_blocked_until_review": True,
            "post_demo_review_blocks": [],
        },
        "data_quality": {
            "data_quality_score": 0.90,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_trades": 0,
            "malformed_timestamps": 0,
        },
        "readiness_snapshot": {
            "readiness_score": 0.89,
        },
        "remaining_work_closure_index": {
            "remaining_lanes": [
                {
                    "lane_id": "SUPERVISED_DEMO_READINESS",
                    "title": "Supervised demo readiness",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1",
                },
                {
                    "lane_id": "OANDA_DEMO_SUPERVISED_EXECUTION_PREP",
                    "title": "OANDA demo supervised execution prep",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1",
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
    assert result["readiness_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert result["supervised_demo_ready"] is False
    assert result["supervised_demo_execution_authorized"] is False
    assert "sensitive_data_provided" in result["readiness_blockers"]
    assert "very-sensitive-value" not in repr(result)
    assert "Remove sensitive data" in result["safe_manual_next_action"]


def test_safety_boolean_keys_are_not_misclassified_as_sensitive() -> None:
    payload = strong_payload()
    payload["credential_use_allowed"] = False
    payload["broker_api_allowed"] = False
    payload["demo_execution_allowed"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "SUPERVISED_DEMO_READY"
    assert "sensitive_data_provided" not in result["readiness_blockers"]

    payload["demo_execution_allowed"] = True
    blocked = evaluate(payload)
    assert blocked["readiness_status"] == "BLOCKED_BY_OANDA_DEMO_BOUNDARY"
    assert "demo_execution_allowed_true" in blocked["readiness_blockers"]


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["readiness_status"] == "INCOMPLETE_INPUTS"
    for missing in [
        "demo_candidate_review_readiness",
        "oanda_demo_boundary",
        "owner_approval_gate",
        "runtime_credential_boundary",
        "risk_controls",
        "order_safety",
        "telemetry",
        "post_demo_review",
    ]:
        assert missing in result["missing_information"]


def test_weak_demo_candidate_review_returns_blocked_by_demo_candidate_review() -> None:
    payload = strong_payload()
    payload["demo_candidate_review_readiness"]["demo_review_ready"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_DEMO_CANDIDATE_REVIEW"
    assert "demo_review_ready_false" in result["readiness_blockers"]


def test_weak_oanda_demo_boundary_returns_blocked_by_oanda_demo_boundary() -> None:
    payload = strong_payload()
    payload["oanda_demo_boundary"]["broker_api_allowed"] = True
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_OANDA_DEMO_BOUNDARY"
    assert "broker_api_allowed_true" in result["readiness_blockers"]


def test_weak_owner_approval_gate_returns_blocked_by_owner_approval_gate() -> None:
    payload = strong_payload()
    payload["owner_approval_gate"]["owner_can_cancel"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_OWNER_APPROVAL_GATE"
    assert "owner_can_cancel_false" in result["readiness_blockers"]


def test_weak_runtime_credential_boundary_returns_blocked_by_runtime_credential_boundary() -> None:
    payload = strong_payload()
    payload["runtime_credential_boundary"]["credentials_persisted"] = True
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY"
    assert "credentials_persisted_true" in result["readiness_blockers"]


def test_weak_risk_controls_returns_blocked_by_risk_controls() -> None:
    payload = strong_payload()
    payload["risk_controls"]["max_risk_per_trade_pct"] = 0.02
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_RISK_CONTROLS"
    assert "max_risk_per_trade_pct_above_limit" in result["readiness_blockers"]


def test_weak_order_safety_returns_blocked_by_order_safety() -> None:
    payload = strong_payload()
    payload["order_safety"]["stop_loss_required"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_ORDER_SAFETY"
    assert "stop_loss_required_false" in result["readiness_blockers"]


def test_weak_telemetry_returns_blocked_by_telemetry() -> None:
    payload = strong_payload()
    payload["telemetry"]["audit_log_required"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_TELEMETRY"
    assert "audit_log_required_false" in result["readiness_blockers"]


def test_weak_post_demo_review_returns_blocked_by_post_demo_review() -> None:
    payload = strong_payload()
    payload["post_demo_review"]["next_trade_blocked_until_review"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_POST_DEMO_REVIEW"
    assert "next_trade_blocked_until_review_false" in result["readiness_blockers"]


def test_weak_data_quality_returns_blocked_by_data_quality() -> None:
    payload = strong_payload()
    payload["data_quality"]["data_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "data_quality_score_below_threshold" in result["readiness_blockers"]


def test_strong_readiness_evidence_returns_supervised_demo_ready() -> None:
    result = evaluate(strong_payload())
    assert result["readiness_status"] == "SUPERVISED_DEMO_READY"
    assert result["supervised_demo_ready"] is True
    assert result["readiness_score"] == 0.89


def test_strong_readiness_routes_next_best_packet_to_oanda_demo_prep() -> None:
    result = evaluate(strong_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_SUPERVISED_EXECUTION_PREP_V1"
    assert result["next_remaining_lane"]["lane_id"] == "OANDA_DEMO_SUPERVISED_EXECUTION_PREP"


def test_blocked_evidence_keeps_this_packet_as_next_best_packet() -> None:
    payload = strong_payload()
    payload["telemetry"]["exception_capture_required"] = False
    result = evaluate(payload)
    assert result["next_best_packet"] == "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1"


def test_owner_action_queue_contains_review_next_packet() -> None:
    result = evaluate(strong_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["owner_action_queue"])
    assert all(action["execution_allowed"] is False for action in result["owner_action_queue"])


def test_readiness_never_authorizes_live_or_demo_execution() -> None:
    result = evaluate(strong_payload())
    assert result["supervised_demo_ready"] is True
    assert result["supervised_demo_execution_authorized"] is False
    assert result["trade_execution_allowed"] is False
    assert result["demo_execution_allowed"] is False
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
    blocked["post_demo_review"]["pnl_review_required"] = False
    results.append(evaluate(blocked)["safe_manual_next_action"])
    for action in results:
        lowered = action.lower()
        for phrase in phrases:
            assert phrase not in lowered


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
