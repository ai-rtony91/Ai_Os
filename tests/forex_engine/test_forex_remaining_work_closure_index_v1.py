from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_remaining_work_closure_index_v1 import (  # noqa: E402
    SCHEMA,
    evaluate_forex_remaining_work_closure_index_v1,
)

MODULE_PATH = ROOT / "automation" / "forex_engine" / "forex_remaining_work_closure_index_v1.py"
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
    return evaluate_forex_remaining_work_closure_index_v1(payload)


def test_output_is_read_only_and_owner_gated() -> None:
    result = evaluate({})
    assert result["schema"] == SCHEMA
    assert result["read_only"] is True
    assert result["owner_decision_required"] is True
    assert result["safety"]["read_only"] is True
    assert result["safety"]["live_trading_allowed"] is False
    assert result["safety"]["money_movement_allowed"] is False
    assert result["safety"]["broker_api_allowed"] is False
    assert result["safety"]["bank_access_allowed"] is False
    assert result["safety"]["credential_use_allowed"] is False


def test_default_remaining_lanes_and_next_best_packet() -> None:
    result = evaluate({})
    lane_ids = [lane["lane_id"] for lane in result["remaining_lanes"]]
    assert lane_ids == [
        "OWNER_REVIEW_DASHBOARD_SURFACING",
        "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW",
        "FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY",
        "PROFIT_CANDIDATE_QUALITY_IMPROVEMENT",
        "BROKER_DEMO_OBSERVABILITY_AND_EXCEPTION_REVIEW",
        "RISK_KILL_SWITCH_DAILY_STOP_SURFACING",
        "DASHBOARD_STATE_REDUCTION_AND_SOURCE_OF_TRUTH",
        "VOICE_AI_OWNER_REVIEW_SUMMARY",
        "SECURITY_CREDENTIAL_PERSISTENCE_GATE",
        "FINAL_AUTONOMY_SUPERVISOR_READINESS_GATE",
    ]
    assert result["next_best_packet"] == "AIOS_FOREX_OWNER_REVIEW_DASHBOARD_SURFACING_V1"


def test_recommended_sequence_is_complete() -> None:
    result = evaluate({})
    assert result["recommended_sequence"] == [
        "Owner-review dashboard/surface packet",
        "Capital withdrawal owner-review workflow packet",
        "Evidence depth / walk-forward sufficiency packet",
        "Candidate quality improvement packet",
        "Broker demo observability and exception review packet",
        "Risk and kill-switch surfacing packet",
        "Dashboard state cleanup/reduction packet",
        "Voice-AI owner review summary packet",
        "Security persistence gate packet",
        "Final autonomy supervisor readiness gate packet",
    ]


def test_completion_policy_requires_allowed_statuses() -> None:
    result = evaluate({})
    allowed_statuses = result["completion_policy"]["allowed_terminal_statuses"]
    assert "LANDED" in allowed_statuses
    assert "BLOCKED_WITH_REASON" in allowed_statuses
    assert "DEFERRED_BY_OWNER" in allowed_statuses
    assert "SUPERSEDED" in allowed_statuses
    assert "NEEDS_MORE_EVIDENCE" in allowed_statuses
    assert result["completion_policy"]["one_atomic_packet_at_a_time"] is True
    assert result["completion_policy"]["clean_main_before_next_packet"] is True


def test_each_lane_has_owner_gate_and_forbidden_actions() -> None:
    result = evaluate({})
    for lane in result["remaining_lanes"]:
        assert lane["owner_gate_required"] is True
        assert isinstance(lane["forbidden_actions"], list)
        assert lane["forbidden_actions"]


def test_next_best_advances_after_lanes_landed() -> None:
    result = evaluate(
        {
            "landed_lanes": [
                "OWNER_REVIEW_DASHBOARD_SURFACING",
                "CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW",
            ]
        }
    )
    assert result["next_best_packet"] == "AIOS_FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY_V1"


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
