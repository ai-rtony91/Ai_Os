from __future__ import annotations

from dataclasses import dataclass

from automation.operator_relief.full_auto_handoff import build_full_auto_handoff
from automation.operator_relief.full_auto_policy import (
    FULL_AUTO_ALLOWED,
    FULL_AUTO_BLOCKED,
    FULL_AUTO_REQUIRES_APPROVAL,
    FullAutoTask,
    evaluate_full_auto_policy,
)


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str = "C:\\Dev\\Ai.Os"
    branch: str = "feature/full-operator-relief-closed-loop-v1"
    dirty_state: str = "CLEAN"


def _task(**overrides) -> FullAutoTask:
    data = {
        "task_id": "task-001",
        "description": "Safe docs update",
        "allowed_paths": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "forbidden_paths": ["AGENTS.md", "README.md", "docs/governance/**"],
        "changed_paths": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "requested_actions": [],
        "validator_targets": ["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        "expected_branch": "feature/full-operator-relief-closed-loop-v1",
    }
    data.update(overrides)
    return FullAutoTask(**data)


def test_safe_doc_task_allowed() -> None:
    decision = evaluate_full_auto_policy(_task(), FakeRepoState())

    assert decision.status == FULL_AUTO_ALLOWED
    assert decision.allowed is True
    assert decision.executable is False


def test_dirty_worktree_requires_approval() -> None:
    repo_state = FakeRepoState(dirty_state="DIRTY")
    decision = evaluate_full_auto_policy(_task(), repo_state)

    assert decision.status == FULL_AUTO_REQUIRES_APPROVAL
    assert decision.notification_required is True


def test_governance_edit_requires_approval() -> None:
    task = _task(
        allowed_paths=["docs/governance/source-of-truth-map.md"],
        forbidden_paths=["AGENTS.md", "README.md"],
        changed_paths=["docs/governance/source-of-truth-map.md"],
        validator_targets=["docs/governance/source-of-truth-map.md"],
    )
    decision = evaluate_full_auto_policy(task, FakeRepoState())

    assert decision.status == FULL_AUTO_REQUIRES_APPROVAL
    assert "Protected path change requires human approval." in decision.reasons


def test_live_trading_blocked() -> None:
    decision = evaluate_full_auto_policy(_task(live_trading=True), FakeRepoState())

    assert decision.status == FULL_AUTO_BLOCKED
    assert decision.blocked is True


def test_secrets_blocked() -> None:
    decision = evaluate_full_auto_policy(_task(secrets=True), FakeRepoState())

    assert decision.status == FULL_AUTO_BLOCKED
    assert decision.notification_required is True


def test_missing_validator_blocks() -> None:
    decision = evaluate_full_auto_policy(_task(validator_targets=["unknown.bin"]), FakeRepoState())

    assert decision.status == FULL_AUTO_BLOCKED
    assert "One or more validator targets have no v1 validator." in decision.reasons


def test_forbidden_paths_with_blocked_keyword_do_not_block_safe_task() -> None:
    decision = evaluate_full_auto_policy(
        _task(forbidden_paths=["AGENTS.md", "README.md", "api/**", "broker/**", "secrets/**"]),
        FakeRepoState(),
    )

    assert decision.status == FULL_AUTO_ALLOWED
    assert decision.blocked is False


def test_allowed_paths_with_blocked_keyword_blocks() -> None:
    decision = evaluate_full_auto_policy(
        _task(
            allowed_paths=["api/safe.md"],
            changed_paths=["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
            validator_targets=["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        ),
        FakeRepoState(),
    )

    assert decision.status == FULL_AUTO_BLOCKED
    assert "Path scope includes blocked runtime, secret, broker, API, or live-trading keyword." in decision.reasons


def test_changed_paths_with_blocked_keyword_blocks() -> None:
    decision = evaluate_full_auto_policy(
        _task(
            allowed_paths=["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
            changed_paths=["api/safe.md"],
            validator_targets=["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
        ),
        FakeRepoState(),
    )

    assert decision.status == FULL_AUTO_BLOCKED


def test_validator_targets_with_blocked_keyword_blocks() -> None:
    decision = evaluate_full_auto_policy(
        _task(
            allowed_paths=["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
            changed_paths=["docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md"],
            validator_targets=["api/safe.md"],
        ),
        FakeRepoState(),
    )

    assert decision.status == FULL_AUTO_BLOCKED


def test_push_request_requires_approval() -> None:
    decision = evaluate_full_auto_policy(_task(requested_actions=["push"], push_allowed=True), FakeRepoState())

    assert decision.status == FULL_AUTO_REQUIRES_APPROVAL
    assert decision.requires_approval is True


def test_branch_mismatch_requires_approval() -> None:
    repo_state = FakeRepoState(branch="main")
    decision = evaluate_full_auto_policy(_task(), repo_state)

    assert decision.status == FULL_AUTO_REQUIRES_APPROVAL
    assert "Branch mismatch requires human approval." in decision.reasons


def test_operator_notification_required_on_failure() -> None:
    decision = evaluate_full_auto_policy(_task(live_trading=True), FakeRepoState())

    assert decision.status == FULL_AUTO_BLOCKED
    assert decision.notification_required is True


def test_handoff_packet_is_non_executing_and_bounded() -> None:
    task = _task()
    decision = evaluate_full_auto_policy(task, FakeRepoState())
    handoff = build_full_auto_handoff(task, decision, FakeRepoState())

    assert handoff.executable is False
    assert handoff.no_push_unless_approved is True
    assert handoff.no_merge_unless_approved is True
    assert "telemetry/operator_relief/evidence.jsonl" == handoff.evidence_output_path
    assert "no recursive Codex call" in handoff.draft_text
