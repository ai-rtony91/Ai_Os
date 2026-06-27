from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.replay_proof_evidence_v1 import (  # noqa: E402
    REPLAY_PROOF_BLOCKED,
    REPLAY_PROOF_INCOMPLETE,
    REPLAY_PROOF_READY,
    build_sample_replay_summary,
    evaluate_replay_proof_evidence,
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


def test_safe_ready_path_accepts_deterministic_replay_summary() -> None:
    result = evaluate_replay_proof_evidence(build_sample_replay_summary())

    assert result["replay_proof_status"] == REPLAY_PROOF_READY
    assert result["blockers"] == []
    assert result["metrics"]["mismatch_count"] == 0
    assert_permissions_false(result)


def test_missing_input_is_incomplete() -> None:
    result = evaluate_replay_proof_evidence(None)

    assert result["replay_proof_status"] == REPLAY_PROOF_INCOMPLETE
    assert result["missing_fields"]
    assert_permissions_false(result)


def test_stale_replay_evidence_blocks() -> None:
    summary = build_sample_replay_summary()
    summary["evidence_age_days"] = 99

    result = evaluate_replay_proof_evidence(summary)

    assert result["replay_proof_status"] == REPLAY_PROOF_BLOCKED
    assert any("stale" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_true_permission_blocks_but_safe_false_does_not() -> None:
    summary = build_sample_replay_summary()
    summary["live_trading_allowed"] = True
    summary["credential_access_allowed"] = False

    result = evaluate_replay_proof_evidence(summary)

    assert result["replay_proof_status"] == REPLAY_PROOF_BLOCKED
    assert any("unsafe true" in blocker for blocker in result["blockers"])
    assert not any("credential_access_allowed contains" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_secret_like_or_account_like_field_blocks() -> None:
    summary = build_sample_replay_summary()
    summary["broker_order_id"] = "not-allowed"

    result = evaluate_replay_proof_evidence(summary)

    assert result["replay_proof_status"] == REPLAY_PROOF_BLOCKED
    assert any("secret-like or account-like" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsanitized_input_blocks() -> None:
    summary = build_sample_replay_summary()
    summary["sanitized"] = False

    result = evaluate_replay_proof_evidence(summary)

    assert result["replay_proof_status"] == REPLAY_PROOF_BLOCKED
    assert any("sanitized" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_conflicting_threshold_blocks() -> None:
    summary = build_sample_replay_summary()
    summary["max_evidence_age_days"] = -1

    result = evaluate_replay_proof_evidence(summary)

    assert result["replay_proof_status"] == REPLAY_PROOF_BLOCKED
    assert any("cannot be negative" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_operator_text_and_json_conversion() -> None:
    result = evaluate_replay_proof_evidence(build_sample_replay_summary())

    assert result_to_jsonable_dict(result)["replay_proof_status"] == REPLAY_PROOF_READY
    assert "No trading approval" in result_to_operator_text(result)
