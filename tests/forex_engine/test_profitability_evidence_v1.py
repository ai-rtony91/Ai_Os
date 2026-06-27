from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.profitability_evidence_v1 import (  # noqa: E402
    PROFITABILITY_EVIDENCE_BLOCKED,
    PROFITABILITY_EVIDENCE_INCOMPLETE,
    PROFITABILITY_EVIDENCE_REVIEW_READY,
    build_sample_closed_trades,
    build_sample_replay_summaries,
    build_sample_thresholds,
    build_sample_walk_forward_summaries,
    evaluate_profitability_evidence,
)


PROTECTED_FLAGS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
)


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def sample_result() -> dict:
    return evaluate_profitability_evidence(
        build_sample_closed_trades(),
        build_sample_replay_summaries(),
        build_sample_walk_forward_summaries(),
        build_sample_thresholds(),
    )


def test_safe_review_path_scores_profitability_evidence() -> None:
    result = sample_result()

    assert result["status"] == PROFITABILITY_EVIDENCE_REVIEW_READY
    assert result["expectancy"] > 0
    assert result["profit_factor"] > 1
    assert result["blockers"] == []
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    result = evaluate_profitability_evidence(None, [], [], build_sample_thresholds())

    assert result["status"] == PROFITABILITY_EVIDENCE_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_thresholds_block() -> None:
    thresholds = build_sample_thresholds()
    thresholds["min_profit_factor"] = 0.5

    result = evaluate_profitability_evidence(
        build_sample_closed_trades(),
        build_sample_replay_summaries(),
        build_sample_walk_forward_summaries(),
        thresholds,
    )

    assert result["status"] == PROFITABILITY_EVIDENCE_BLOCKED
    assert any("conflicts" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_evidence_blocks_profitability() -> None:
    trades = build_sample_closed_trades()
    trades[0]["age_days"] = 99

    result = evaluate_profitability_evidence(
        trades,
        build_sample_replay_summaries(),
        build_sample_walk_forward_summaries(),
        build_sample_thresholds(),
    )

    assert result["status"] == PROFITABILITY_EVIDENCE_BLOCKED
    assert any("stale" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_flag_blocks_profitability() -> None:
    trades = build_sample_closed_trades()
    trades[0]["live_trading_allowed"] = True

    result = evaluate_profitability_evidence(
        trades,
        build_sample_replay_summaries(),
        build_sample_walk_forward_summaries(),
        build_sample_thresholds(),
    )

    assert result["status"] == PROFITABILITY_EVIDENCE_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)
