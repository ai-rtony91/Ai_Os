from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.walk_forward_oos_evidence_v1 import (  # noqa: E402
    WALK_FORWARD_OOS_BLOCKED,
    WALK_FORWARD_OOS_INCOMPLETE,
    WALK_FORWARD_OOS_READY,
    build_sample_walk_forward_oos_summary,
    evaluate_walk_forward_oos_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
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


def test_safe_ready_path_accepts_walk_forward_oos_summary() -> None:
    result = evaluate_walk_forward_oos_evidence(build_sample_walk_forward_oos_summary())

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_READY
    assert result["blockers"] == []
    assert result["metrics"]["walk_forward_pass_rate"] >= 0.75
    assert_permissions_false(result)


def test_missing_input_is_incomplete() -> None:
    result = evaluate_walk_forward_oos_evidence(None)

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_INCOMPLETE
    assert result["missing_fields"]
    assert_permissions_false(result)


def test_stale_evidence_blocks() -> None:
    summary = build_sample_walk_forward_oos_summary()
    summary["evidence_age_days"] = 99

    result = evaluate_walk_forward_oos_evidence(summary)

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_BLOCKED
    assert any("stale" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_true_permission_blocks() -> None:
    summary = build_sample_walk_forward_oos_summary()
    summary["order_submission_allowed"] = True

    result = evaluate_walk_forward_oos_evidence(summary)

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_BLOCKED
    assert any("unsafe true" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_secret_like_or_account_like_field_blocks() -> None:
    summary = build_sample_walk_forward_oos_summary()
    summary["raw_payload"] = {"anything": "blocked"}

    result = evaluate_walk_forward_oos_evidence(summary)

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_BLOCKED
    assert any("secret-like or account-like" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsanitized_input_blocks() -> None:
    summary = build_sample_walk_forward_oos_summary()
    summary["sanitized"] = False

    result = evaluate_walk_forward_oos_evidence(summary)

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_BLOCKED
    assert any("sanitized" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_conflicting_threshold_blocks() -> None:
    summary = build_sample_walk_forward_oos_summary()
    summary["min_pass_rate"] = 1.5

    result = evaluate_walk_forward_oos_evidence(summary)

    assert result["walk_forward_oos_status"] == WALK_FORWARD_OOS_BLOCKED
    assert any("min_pass_rate" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_operator_text_and_json_conversion() -> None:
    result = evaluate_walk_forward_oos_evidence(build_sample_walk_forward_oos_summary())

    assert result_to_jsonable_dict(result)["walk_forward_oos_status"] == WALK_FORWARD_OOS_READY
    assert "No trading approval" in result_to_operator_text(result)
