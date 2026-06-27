from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.supervised_observation_22h6d_evidence_v1 import (  # noqa: E402
    SUPERVISED_OBSERVATION_BLOCKED,
    SUPERVISED_OBSERVATION_INCOMPLETE,
    SUPERVISED_OBSERVATION_READY,
    build_sample_observation_summary,
    evaluate_supervised_observation_22h6d_evidence,
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


def test_safe_ready_path_accepts_22h6d_observation_summary() -> None:
    result = evaluate_supervised_observation_22h6d_evidence(
        build_sample_observation_summary()
    )

    assert result["observation_status"] == SUPERVISED_OBSERVATION_READY
    assert result["blockers"] == []
    assert result["metrics"]["observed_hours"] >= 22
    assert_permissions_false(result)


def test_missing_input_is_incomplete() -> None:
    result = evaluate_supervised_observation_22h6d_evidence(None)

    assert result["observation_status"] == SUPERVISED_OBSERVATION_INCOMPLETE
    assert result["missing_fields"]
    assert_permissions_false(result)


def test_stale_observation_evidence_blocks() -> None:
    summary = build_sample_observation_summary()
    summary["evidence_age_days"] = 99

    result = evaluate_supervised_observation_22h6d_evidence(summary)

    assert result["observation_status"] == SUPERVISED_OBSERVATION_BLOCKED
    assert any("stale" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_true_permission_blocks() -> None:
    summary = build_sample_observation_summary()
    summary["dashboard_execution_authority"] = True

    result = evaluate_supervised_observation_22h6d_evidence(summary)

    assert result["observation_status"] == SUPERVISED_OBSERVATION_BLOCKED
    assert any("unsafe true" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_secret_like_or_account_like_field_blocks() -> None:
    summary = build_sample_observation_summary()
    summary["order_payload"] = {"side": "blocked"}

    result = evaluate_supervised_observation_22h6d_evidence(summary)

    assert result["observation_status"] == SUPERVISED_OBSERVATION_BLOCKED
    assert any("secret-like or account-like" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsanitized_input_blocks() -> None:
    summary = build_sample_observation_summary()
    summary["sanitized"] = False

    result = evaluate_supervised_observation_22h6d_evidence(summary)

    assert result["observation_status"] == SUPERVISED_OBSERVATION_BLOCKED
    assert any("sanitized" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_conflicting_threshold_blocks() -> None:
    summary = build_sample_observation_summary()
    summary["required_hours"] = 21

    result = evaluate_supervised_observation_22h6d_evidence(summary)

    assert result["observation_status"] == SUPERVISED_OBSERVATION_BLOCKED
    assert any("at least 22" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_operator_text_and_json_conversion() -> None:
    result = evaluate_supervised_observation_22h6d_evidence(
        build_sample_observation_summary()
    )

    assert result_to_jsonable_dict(result)["observation_status"] == SUPERVISED_OBSERVATION_READY
    assert "No trading approval" in result_to_operator_text(result)
