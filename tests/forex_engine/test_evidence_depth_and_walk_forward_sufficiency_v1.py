from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.evidence_depth_and_walk_forward_sufficiency_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_evidence_depth_and_walk_forward_sufficiency_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "evidence_depth_and_walk_forward_sufficiency_v1.py"
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
    return evaluate_evidence_depth_and_walk_forward_sufficiency_v1(payload)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "strategy_evaluation": {
            "total_trades": 150,
            "win_count": 78,
            "loss_count": 60,
            "breakeven_count": 12,
            "in_sample_trade_count": 100,
            "oos_trade_count": 50,
            "regimes": ["trend", "range", "volatile"],
        },
        "walk_forward_validation": {
            "walk_forward_windows": [
                {"status": "PASS", "pnl": 2.0},
                {"status": "PASS", "pnl": 1.3},
                {"status": "FAIL", "pnl": -0.2},
            ],
            "passed_windows": 2,
            "failed_windows": 1,
            "walk_forward_gate_cleared": True,
            "oos_pass_rate": 0.67,
            "stability_score": 0.82,
        },
        "profitability_evaluation": {
            "expectancy": 0.18,
            "profit_factor": 1.45,
            "total_pnl": 18.0,
            "gross_profit": 48.0,
            "gross_loss": -33.0,
            "candidate_status": "MORE_EVIDENCE",
            "promotion_status": "OWNER_REVIEW_REQUIRED",
        },
        "paper_session_samples": [
            {"session_id": "s1", "trade_count": 50},
            {"session_id": "s2", "trade_count": 50},
            {"session_id": "s3", "trade_count": 50},
        ],
        "candidate_quality_snapshot": {
            "max_drawdown_pct": 0.06,
            "daily_loss_stop_triggered": False,
            "risk_blocks": [],
            "data_quality_score": 0.94,
            "missing_fields": [],
            "invalid_rows": 0,
            "duplicate_trades": 0,
            "malformed_timestamps": 0,
            "spread_available": True,
            "slippage_available": True,
            "missed_valid_setups_count": 0,
            "false_positive_count": 0,
            "rejected_winner_count": 0,
            "late_entry_count": 0,
            "early_exit_count": 0,
            "opportunity_leakage_notes": ["No reviewed leakage found."],
        },
        "remaining_work_closure_index": {
            "remaining_lanes": [
                {
                    "lane_id": "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY",
                    "title": "Evidence depth / walk-forward sufficiency packet",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "safe_packet_name": "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1",
                },
                {
                    "lane_id": "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT",
                    "title": "Candidate quality improvement packet",
                    "status": "NEEDS_MORE_EVIDENCE",
                    "safe_packet_name": "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1",
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
    assert result["safety"]["fixed_return_target_promised"] is False
    assert result["safety"]["profit_claim_authorized"] is False


def test_output_is_read_only_and_execution_flags_blocked() -> None:
    assert_safety_flags(evaluate(strong_payload()))


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    payload = strong_payload()
    payload["api_key"] = "very-sensitive-value"
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert result["sufficient_for_next_profit_lane"] is False
    assert result["sufficient_for_demo_candidate_review"] is False
    assert "sensitive_data_provided" in result["blocker_summary"]["data_quality_blockers"]
    assert "very-sensitive-value" not in repr(result)
    assert result["safe_manual_next_action"] == "Remove sensitive data and rerun the read-only sufficiency evaluator."


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = evaluate({})
    assert result["evidence_status"] == "INCOMPLETE_INPUTS"
    assert result["sufficient_for_next_profit_lane"] is False
    assert result["sufficient_for_demo_candidate_review"] is False
    assert "strategy_evaluation" in result["missing_information"]
    assert "walk_forward_validation" in result["missing_information"]
    assert "profitability_evaluation" in result["missing_information"]
    assert "paper_session_samples" in result["missing_information"]


def test_insufficient_sample_returns_blocked_by_sample_size() -> None:
    payload = strong_payload()
    payload["strategy_evaluation"]["total_trades"] = 40
    payload["strategy_evaluation"]["oos_trade_count"] = 20
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_SAMPLE_SIZE"
    assert "total_trades_below_minimum" in result["blocker_summary"]["sample_blockers"]
    assert "oos_trades_below_minimum" in result["blocker_summary"]["sample_blockers"]


def test_insufficient_walk_forward_returns_blocked_by_walk_forward() -> None:
    payload = strong_payload()
    payload["walk_forward_validation"]["walk_forward_windows"] = [{"status": "PASS", "pnl": 1.0}]
    payload["walk_forward_validation"]["passed_windows"] = 1
    payload["walk_forward_validation"]["failed_windows"] = 0
    payload["walk_forward_validation"]["walk_forward_gate_cleared"] = False
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_WALK_FORWARD"
    assert "walk_forward_windows_below_minimum" in result["blocker_summary"]["walk_forward_blockers"]


def test_oos_instability_returns_blocked_by_oos_instability() -> None:
    payload = strong_payload()
    payload["walk_forward_validation"]["stability_score"] = 0.52
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_OOS_INSTABILITY"
    assert "oos_stability_score_below_minimum" in result["blocker_summary"]["oos_blockers"]


def test_insufficient_regime_coverage_returns_blocked_by_regime_coverage() -> None:
    payload = strong_payload()
    payload["strategy_evaluation"]["regimes"] = ["trend", "range"]
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_REGIME_COVERAGE"
    assert "regime_count_below_minimum" in result["blocker_summary"]["regime_blockers"]


def test_negative_expectancy_returns_blocked_by_negative_expectancy() -> None:
    payload = strong_payload()
    payload["profitability_evaluation"]["expectancy"] = -0.01
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_NEGATIVE_EXPECTANCY"
    assert "expectancy_below_minimum" in result["blocker_summary"]["profitability_blockers"]


def test_low_profit_factor_returns_blocked_by_low_profit_factor() -> None:
    payload = strong_payload()
    payload["profitability_evaluation"]["profit_factor"] = 1.05
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_LOW_PROFIT_FACTOR"
    assert "profit_factor_below_minimum" in result["blocker_summary"]["profitability_blockers"]


def test_excessive_drawdown_returns_blocked_by_drawdown() -> None:
    payload = strong_payload()
    payload["candidate_quality_snapshot"]["max_drawdown_pct"] = 0.18
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_DRAWDOWN"
    assert "max_drawdown_pct_above_limit" in result["blocker_summary"]["drawdown_blockers"]


def test_weak_data_quality_returns_blocked_by_data_quality() -> None:
    payload = strong_payload()
    payload["candidate_quality_snapshot"]["data_quality_score"] = 0.60
    result = evaluate(payload)
    assert result["evidence_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert "data_quality_score_below_minimum" in result["blocker_summary"]["data_quality_blockers"]


def test_complete_strong_evidence_returns_sufficient_for_next_profit_lane() -> None:
    result = evaluate(strong_payload())
    assert result["evidence_status"] == "SUFFICIENT_FOR_NEXT_PROFIT_LANE"
    assert result["sufficient_for_next_profit_lane"] is True
    assert result["sufficient_for_demo_candidate_review"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_PROFIT_CANDIDATE_QUALITY_IMPROVEMENT_V1"
    assert result["next_remaining_lane"]["lane_id"] == "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT"


def test_insufficient_evidence_keeps_this_packet_as_next_best_packet() -> None:
    result = evaluate({})
    assert result["next_best_packet"] == "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1"


def test_blocker_summary_separates_blocker_groups() -> None:
    payload = strong_payload()
    payload["thresholds"] = {"min_total_trades": 20}
    payload["strategy_evaluation"]["total_trades"] = 20
    payload["walk_forward_validation"]["walk_forward_gate_cleared"] = False
    payload["walk_forward_validation"]["stability_score"] = 0.5
    payload["strategy_evaluation"]["regimes"] = ["trend"]
    payload["profitability_evaluation"]["expectancy"] = -0.01
    payload["candidate_quality_snapshot"]["max_drawdown_pct"] = 0.3
    payload["candidate_quality_snapshot"]["data_quality_score"] = 0.5
    payload["candidate_quality_snapshot"]["missed_valid_setups_count"] = 2
    result = evaluate(payload)
    summary = result["blocker_summary"]
    assert summary["sample_blockers"]
    assert summary["walk_forward_blockers"]
    assert summary["oos_blockers"]
    assert summary["regime_blockers"]
    assert summary["profitability_blockers"]
    assert summary["drawdown_blockers"]
    assert summary["data_quality_blockers"]
    assert summary["leakage_blockers"]
    assert summary["threshold_blockers"] == ["threshold_override_rejected"]
    assert "threshold_override_rejected" in summary["all_blockers"]


def test_owner_action_queue_contains_review_next_profit_packet() -> None:
    result = evaluate(strong_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PROFIT_PACKET" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["owner_action_queue"])
    assert all(action["execution_allowed"] is False for action in result["owner_action_queue"])


def test_promotion_readiness_never_authorizes_live_or_demo_execution() -> None:
    result = evaluate(strong_payload())
    readiness = result["promotion_readiness"]
    assert readiness["can_promote_to_candidate_quality_improvement"] is True
    assert readiness["can_promote_to_demo_candidate_review"] is True
    assert readiness["demo_execution_authorized"] is False
    assert readiness["live_execution_authorized"] is False


def test_safe_manual_next_action_never_uses_execution_or_return_phrases() -> None:
    phrases = [
        "trade now",
        "withdraw now",
        "move money",
        "guaranteed " + "return",
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
