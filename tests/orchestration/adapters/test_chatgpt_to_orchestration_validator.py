from pathlib import Path

from automation.orchestration.adapters.chatgpt_to_orchestration.models import (
    BranchWorktreeValidation,
    RepoState,
)
from automation.orchestration.adapters.chatgpt_to_orchestration.parser import parse_packet
from automation.orchestration.adapters.chatgpt_to_orchestration.validator import validate_packet

FIXTURE_ROOT = Path("tests/fixtures/chatgpt_to_orchestration")
REPO_STATE = RepoState(
    branch="feature/full-operator-relief-closed-loop-v1",
    git_status_short_branch="## feature/full-operator-relief-closed-loop-v1",
    dirty_state_class="REPORT_ONLY_UNTRACKED",
)


def _packet(name: str):
    return parse_packet((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def test_valid_packet_has_no_missing_required_fields():
    result = validate_packet(_packet("pass_report_only_packet.txt"), REPO_STATE)

    assert result.missing_fields == []
    assert result.blocked_reasons == []
    assert result.branch_worktree_validation == BranchWorktreeValidation.PASS


def test_missing_execution_token_is_blocked():
    result = validate_packet(_packet("fail_missing_token_packet.txt"), REPO_STATE)

    assert "MISSING_EXECUTION_TOKEN" in result.blocked_reasons


def test_branch_mismatch_is_detected():
    result = validate_packet(_packet("fail_branch_mismatch_packet.txt"), REPO_STATE)

    assert result.branch_worktree_validation == BranchWorktreeValidation.FAIL
    assert "STATE_MISMATCH" in result.blocked_reasons
