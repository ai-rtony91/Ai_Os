from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.evidence_milestone_selector_v1 import (  # noqa: E402
    EVIDENCE_MILESTONE_BLOCKED,
    EVIDENCE_MILESTONE_COMPLETE,
    EVIDENCE_MILESTONE_CONTINUE,
    build_sample_evidence_results,
    result_to_jsonable_dict,
    result_to_operator_text,
    select_evidence_milestone,
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


def test_safe_complete_path_marks_all_milestones_complete() -> None:
    result = select_evidence_milestone(build_sample_evidence_results())

    assert result["status"] == EVIDENCE_MILESTONE_COMPLETE
    assert result["remaining_evidence_milestones"] == []
    assert_permissions_false(result)


def test_missing_input_selects_replay_as_next_incomplete() -> None:
    result = select_evidence_milestone(None)

    assert result["status"] == EVIDENCE_MILESTONE_CONTINUE
    assert result["next_evidence_milestone"] == "replay_proof_evidence"
    assert result["incomplete_evidence_milestones"]
    assert_permissions_false(result)


def test_stale_blocked_evidence_blocks_selector() -> None:
    evidence = build_sample_evidence_results()
    evidence["replay_proof_evidence"]["status"] = "REPLAY_PROOF_BLOCKED"
    evidence["replay_proof_evidence"]["blockers"] = ["replay evidence is stale"]

    result = select_evidence_milestone(evidence)

    assert result["status"] == EVIDENCE_MILESTONE_BLOCKED
    assert "replay_proof_evidence" in result["blocked_evidence_milestones"]
    assert any("stale" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_true_permission_blocks_selector() -> None:
    evidence = build_sample_evidence_results()
    evidence["walk_forward_oos_evidence"]["order_submission_allowed"] = True

    result = select_evidence_milestone(evidence)

    assert result["status"] == EVIDENCE_MILESTONE_BLOCKED
    assert any("unsafe true" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_secret_like_or_account_like_field_blocks_selector() -> None:
    evidence = build_sample_evidence_results()
    evidence["persistent_profitability_evidence"]["raw_transaction_id"] = "blocked"

    result = select_evidence_milestone(evidence)

    assert result["status"] == EVIDENCE_MILESTONE_BLOCKED
    assert any("secret-like or account-like" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_unsanitized_input_blocks_selector() -> None:
    evidence = build_sample_evidence_results()
    evidence["supervised_observation_22h6d_evidence"]["sanitized"] = False

    result = select_evidence_milestone(evidence)

    assert result["status"] == EVIDENCE_MILESTONE_BLOCKED
    assert "supervised_observation_22h6d_evidence" in result["blocked_evidence_milestones"]
    assert_permissions_false(result)


def test_incomplete_milestone_selects_next_packet() -> None:
    evidence = build_sample_evidence_results()
    evidence.pop("walk_forward_oos_evidence")

    result = select_evidence_milestone(evidence)

    assert result["status"] == EVIDENCE_MILESTONE_CONTINUE
    assert result["next_evidence_milestone"] == "walk_forward_oos_evidence"
    assert result["next_safe_packet"] == "AIOS-FOREX-WALK-FORWARD-OOS-EVIDENCE-V1"
    assert_permissions_false(result)


def test_operator_text_and_json_conversion() -> None:
    result = select_evidence_milestone(build_sample_evidence_results())

    assert result_to_jsonable_dict(result)["status"] == EVIDENCE_MILESTONE_COMPLETE
    assert "No trading approval" in result_to_operator_text(result)
