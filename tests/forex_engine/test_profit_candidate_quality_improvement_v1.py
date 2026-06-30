from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.profit_candidate_quality_improvement_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_profit_candidate_quality_improvement_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "profit_candidate_quality_improvement_v1.py"
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
    return evaluate_profit_candidate_quality_improvement_v1(payload)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "evidence_sufficiency": {
            "evidence_status": "SUFFICIENT_FOR_NEXT_PROFIT_LANE",
            "walk_forward_gate_cleared": True,
        },
        "profitability_evaluation": {
            "expectancy": 0.18,
            "expectancy_quality_score": 0.82,
            "profit_factor": 1.62,
            "profit_factor_quality_score": 0.81,
        },
        "candidate_quality_snapshot": {
            "candidate_quality_score": 0.82,
            "drawdown_efficiency_score": 0.83,
            "data_quality_score": 0.91,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_trades": 0,
            "malformed_timestamps": 0,
        },
        "walk_forward_validation": {
            "walk_forward_gate_cleared": True,
            "stability_score": 0.84,
        },
        "regime_results": {
            "regime_quality_score": 0.78,
            "covered_regimes": ["trend", "range", "volatile"],
            "weak_regimes": [],
        },
        "opportunity_leakage": {
            "missed_opportunity_count": 0,
            "rejected_winner_count": 0,
            "opportunity_leakage_notes": ["No reviewed leakage found."],
        },
        "entry_exit_review": {
            "entry_exit_quality_score": 0.86,
            "late_entry_count": 0,
            "early_exit_count": 0,
        },
        "false_positive_review": {
            "false_positive_count": 0,
        },
        "risk_review": {
            "risk_adjusted_quality_score": 0.80,
        },
        "remaining_work_closure_index": {
            "remaining_lanes": [
                {
                    "lane_id": "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT",
                    "title": "Candidate quality improvement packet",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1",
                },
                {
                    "lane_id": "DEMO_CANDIDATE_REVIEW_READINESS",
                    "title": "Demo-candidate review readiness",
                    "status": "OWNER_REVIEW_REQUIRED",
                    "safe_packet_name": "AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1",
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
    assert result["credential_use_allowed"] is False
    assert result["scheduler_created"] is False
    assert result["daemon_created"] is False
    assert result["webhook_created"] is False
    assert result["dashboard_runtime_created"] is False
    assert result["owner_decision_required"] is True
    assert result["safety"]["money_movement_allowed"] is False
    assert result["safety"]["bank_access_allowed"] is False
    assert result["safety"]["broker_api_allowed"] is False
    assert result["safety"]["trade_execution_allowed"] is False
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
    assert result["quality_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "sensitive_data_provided" in result["blocker_summary"]["data_quality_blockers"]
    assert "very-sensitive-value" not in repr(result)
    assert "Remove sensitive data" in result["safe_manual_next_action"]
    assert result["next_best_packet"] == "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1"


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["quality_status"] == "INCOMPLETE_INPUTS"
    assert "profitability_evaluation" in result["missing_information"]
    assert "candidate_quality_snapshot" in result["missing_information"]
    assert "opportunity_leakage" in result["missing_information"]
    assert "entry_exit_review" in result["missing_information"]


def test_weak_expectancy_returns_blocked_by_expectancy() -> None:
    payload = strong_payload()
    payload["profitability_evaluation"]["expectancy_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_EXPECTANCY"
    assert "expectancy_quality_score_below_threshold" in result["blocker_summary"]["expectancy_blockers"]


def test_weak_profit_factor_returns_blocked_by_profit_factor() -> None:
    payload = strong_payload()
    payload["profitability_evaluation"]["profit_factor_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_PROFIT_FACTOR"
    assert "profit_factor_quality_score_below_threshold" in result["blocker_summary"]["profit_factor_blockers"]


def test_weak_drawdown_efficiency_returns_blocked_by_drawdown_efficiency() -> None:
    payload = strong_payload()
    payload["candidate_quality_snapshot"]["drawdown_efficiency_score"] = 0.50
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_DRAWDOWN_EFFICIENCY"
    assert "drawdown_efficiency_score_below_threshold" in result["blocker_summary"]["drawdown_blockers"]


def test_weak_regime_quality_returns_blocked_by_regime_weakness() -> None:
    payload = strong_payload()
    payload["regime_results"]["regime_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_REGIME_WEAKNESS"
    assert "regime_quality_score_below_threshold" in result["blocker_summary"]["regime_blockers"]


def test_missed_opportunity_leakage_returns_blocked_by_missed_opportunity_leakage() -> None:
    payload = strong_payload()
    payload["opportunity_leakage"]["missed_opportunity_count"] = 1
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_MISSED_OPPORTUNITY_LEAKAGE"
    assert "missed_opportunity_count_above_threshold" in result["blocker_summary"]["missed_opportunity_blockers"]


def test_false_positives_return_blocked_by_false_positives() -> None:
    payload = strong_payload()
    payload["false_positive_review"]["false_positive_count"] = 1
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_FALSE_POSITIVES"
    assert "false_positive_count_above_threshold" in result["blocker_summary"]["false_positive_blockers"]


def test_late_entry_or_early_exit_returns_blocked_by_entry_exit_quality() -> None:
    payload = strong_payload()
    payload["entry_exit_review"]["late_entry_count"] = 1
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_ENTRY_EXIT_QUALITY"
    assert "late_entry_count_above_threshold" in result["blocker_summary"]["entry_exit_blockers"]

    payload = strong_payload()
    payload["entry_exit_review"]["early_exit_count"] = 1
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_ENTRY_EXIT_QUALITY"
    assert "early_exit_count_above_threshold" in result["blocker_summary"]["entry_exit_blockers"]


def test_weak_data_quality_returns_blocked_by_data_quality() -> None:
    payload = strong_payload()
    payload["candidate_quality_snapshot"]["data_quality_score"] = 0.60
    result = evaluate(payload)
    assert result["quality_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "data_quality_score_below_threshold" in result["blocker_summary"]["data_quality_blockers"]


def test_strong_quality_evidence_returns_quality_improvement_ready() -> None:
    result = evaluate(strong_payload())
    assert result["quality_status"] == "QUALITY_IMPROVEMENT_READY"
    assert result["candidate_quality_score"] == 0.82


def test_strong_quality_evidence_routes_to_demo_candidate_review_readiness() -> None:
    result = evaluate(strong_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_DEMO_CANDIDATE_REVIEW_READINESS_V1"
    assert result["next_remaining_lane"]["lane_id"] == "DEMO_CANDIDATE_REVIEW_READINESS"


def test_blocked_evidence_keeps_quality_improvement_packet_as_next_best_packet() -> None:
    payload = strong_payload()
    payload["profitability_evaluation"]["expectancy_quality_score"] = 0.50
    result = evaluate(payload)
    assert result["next_best_packet"] == "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1"


def test_improvement_actions_contains_review_next_packet() -> None:
    result = evaluate(strong_payload())
    action_ids = {action["action_id"] for action in result["improvement_actions"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["improvement_actions"])
    assert all(action["execution_allowed"] is False for action in result["improvement_actions"])


def test_promotion_readiness_never_authorizes_live_or_demo_execution() -> None:
    result = evaluate(strong_payload())
    readiness = result["promotion_readiness"]
    assert readiness["can_queue_demo_candidate_review_readiness"] is True
    assert readiness["demo_execution_authorized"] is False
    assert readiness["live_execution_authorized"] is False
    assert readiness["broker_execution_authorized"] is False
    assert result["trade_execution_allowed"] is False
    assert result["broker_api_allowed"] is False


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
    blocked["candidate_quality_snapshot"]["data_quality_score"] = 0.1
    results.append(evaluate(blocked)["safe_manual_next_action"])
    for action in results:
        lowered = action.lower()
        for phrase in phrases:
            assert phrase not in lowered


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
