from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.demo_candidate_review_readiness_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_demo_candidate_review_readiness_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "demo_candidate_review_readiness_v1.py"
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
    return evaluate_demo_candidate_review_readiness_v1(payload)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "evidence_sufficiency": {
            "evidence_status": "SUFFICIENT_FOR_DEMO_CANDIDATE_REVIEW",
            "sufficient_for_next_profit_lane": True,
            "sufficient_for_demo_candidate_review": True,
            "evidence_sufficiency_score": 0.86,
            "sample_sufficient": True,
            "walk_forward_gate_cleared": True,
            "oos_stable": True,
            "regime_coverage_sufficient": True,
        },
        "profit_candidate_quality": {
            "quality_status": "QUALITY_IMPROVEMENT_READY",
            "candidate_quality_score": 0.84,
            "demo_review_ready": True,
            "can_queue_demo_candidate_review_readiness": True,
            "improvement_blockers": [],
            "blocker_summary": {},
        },
        "risk_controls": {
            "risk_control_score": 0.87,
            "max_drawdown_pct": 4.2,
            "daily_loss_stop_configured": True,
            "kill_switch_present": True,
            "max_loss_gate_present": True,
            "position_size_limit_present": True,
            "risk_blocks": [],
        },
        "observability": {
            "observability_score": 0.82,
            "audit_log_present": True,
            "sanitized_evidence_present": True,
            "owner_review_packet_present": True,
            "monitoring_plan_present": True,
            "dashboard_projection_safe": True,
            "observability_blocks": [],
        },
        "owner_gate": {
            "owner_gate_required": True,
            "owner_approval_required": True,
            "owner_review_ready": True,
            "execution_allowed": False,
            "manual_execution_only": True,
        },
        "broker_boundary": {
            "broker_api_allowed": False,
            "trade_execution_allowed": False,
            "credential_use_allowed": False,
            "demo_execution_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
        },
        "data_quality": {
            "data_quality_score": 0.91,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_trades": 0,
            "malformed_timestamps": 0,
        },
        "readiness_snapshot": {
            "readiness_score": 0.86,
        },
        "remaining_work_closure_index": {
            "remaining_lanes": [
                {
                    "lane_id": "DEMO_CANDIDATE_REVIEW_READINESS",
                    "title": "Demo candidate review readiness",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1",
                },
                {
                    "lane_id": "SUPERVISED_DEMO_READINESS",
                    "title": "Supervised demo readiness",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1",
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
    assert result["safety"]["money_movement_allowed"] is False
    assert result["safety"]["bank_access_allowed"] is False
    assert result["safety"]["broker_api_allowed"] is False
    assert result["safety"]["trade_execution_allowed"] is False
    assert result["safety"]["demo_execution_allowed"] is False
    assert result["safety"]["credential_use_allowed"] is False
    assert result["safety"]["scheduler_allowed"] is False
    assert result["safety"]["daemon_allowed"] is False
    assert result["safety"]["webhook_allowed"] is False
    assert result["safety"]["dashboard_runtime_allowed"] is False
    assert result["safety"]["fixed_return_target_promised"] is False
    assert result["safety"]["profit_claim_authorized"] is False


def test_output_is_read_only_and_execution_flags_blocked() -> None:
    assert_safety_flags(evaluate(strong_payload()))


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    payload = strong_payload()
    payload["api_key"] = "very-sensitive-value"
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert result["demo_review_ready"] is False
    assert result["supervised_demo_execution_authorized"] is False
    assert "sensitive_data_provided" in result["readiness_blockers"]
    assert "very-sensitive-value" not in repr(result)
    assert "Remove sensitive data" in result["safe_manual_next_action"]


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["readiness_status"] == "INCOMPLETE_INPUTS"
    for missing in [
        "evidence_sufficiency",
        "profit_candidate_quality",
        "risk_controls",
        "observability",
        "owner_gate",
        "broker_boundary",
    ]:
        assert missing in result["missing_information"]


def test_weak_evidence_sufficiency_returns_blocked_by_evidence_sufficiency() -> None:
    payload = strong_payload()
    payload["evidence_sufficiency"]["evidence_sufficiency_score"] = 0.50
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_EVIDENCE_SUFFICIENCY"
    assert "evidence_sufficiency_score_below_threshold" in result["readiness_blockers"]


def test_weak_candidate_quality_returns_blocked_by_candidate_quality() -> None:
    payload = strong_payload()
    payload["profit_candidate_quality"]["candidate_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_CANDIDATE_QUALITY"
    assert "candidate_quality_score_below_threshold" in result["readiness_blockers"]


def test_weak_risk_controls_returns_blocked_by_risk_controls() -> None:
    payload = strong_payload()
    payload["risk_controls"]["kill_switch_present"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_RISK_CONTROLS"
    assert "kill_switch_present_false" in result["readiness_blockers"]


def test_weak_observability_returns_blocked_by_observability() -> None:
    payload = strong_payload()
    payload["observability"]["audit_log_present"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_OBSERVABILITY"
    assert "audit_log_present_false" in result["readiness_blockers"]


def test_owner_gate_weakness_returns_blocked_by_owner_gate() -> None:
    payload = strong_payload()
    payload["owner_gate"]["owner_review_ready"] = False
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_OWNER_GATE"
    assert "owner_review_ready_false" in result["readiness_blockers"]


def test_broker_boundary_violation_returns_blocked_by_broker_boundary() -> None:
    payload = strong_payload()
    payload["broker_boundary"]["broker_api_allowed"] = True
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_BROKER_BOUNDARY"
    assert result["broker_api_allowed"] is False
    assert result["supervised_demo_execution_authorized"] is False
    assert "broker_api_allowed_true" in result["readiness_blockers"]


def test_weak_data_quality_returns_blocked_by_data_quality() -> None:
    payload = strong_payload()
    payload["data_quality"]["data_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["readiness_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "data_quality_score_below_threshold" in result["readiness_blockers"]


def test_strong_readiness_evidence_returns_demo_review_ready() -> None:
    result = evaluate(strong_payload())
    assert result["readiness_status"] == "DEMO_REVIEW_READY"
    assert result["demo_review_ready"] is True
    assert result["readiness_score"] == 0.86


def test_strong_readiness_routes_next_best_packet_to_supervised_demo_readiness() -> None:
    result = evaluate(strong_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_SUPERVISED_DEMO_READINESS_PACKET_V1"
    assert result["next_remaining_lane"]["lane_id"] == "SUPERVISED_DEMO_READINESS"


def test_blocked_evidence_keeps_this_packet_as_next_best_packet() -> None:
    payload = strong_payload()
    payload["evidence_sufficiency"]["walk_forward_gate_cleared"] = False
    result = evaluate(payload)
    assert result["next_best_packet"] == "AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1"


def test_owner_action_queue_contains_review_next_packet() -> None:
    result = evaluate(strong_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["owner_action_queue"])
    assert all(action["execution_allowed"] is False for action in result["owner_action_queue"])


def test_promotion_readiness_never_authorizes_live_or_demo_execution() -> None:
    result = evaluate(strong_payload())
    assert result["demo_review_ready"] is True
    assert result["supervised_demo_execution_authorized"] is False
    assert result["trade_execution_allowed"] is False
    assert result["demo_execution_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["safety"]["profit_claim_authorized"] is False


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
    blocked["data_quality"]["data_quality_score"] = 0.1
    results.append(evaluate(blocked)["safe_manual_next_action"])
    for action in results:
        lowered = action.lower()
        for phrase in phrases:
            assert phrase not in lowered


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
