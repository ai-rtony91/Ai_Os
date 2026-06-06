from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from automation.operator_relief.approval_queue import build_approval_item, write_approval_item
from automation.operator_relief.evidence_ledger import append_evidence
from automation.operator_relief.notification_gate import emit_notification, should_notify
from automation.operator_relief.packet_builder import build_packet_draft
from automation.operator_relief.repo_state import RepoState
from automation.operator_relief.task_classifier import classify_state
from automation.operator_relief.validator_router import select_validator


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str = "C:\\Dev\\Ai.Os"
    branch: str = "feature/test-branch"
    git_status: str = "## feature/test-branch"
    remote: str = "origin"
    dirty_state: str = "CLEAN"
    agents_md_present: bool = True
    readme_present: bool = True
    created_at: str = "2026-06-06T00:00:00+00:00"
    executable: bool = False


def test_repo_state_model_marks_executable_false() -> None:
    state = RepoState(
        repo_root="C:\\Dev\\Ai.Os",
        branch="main",
        git_status="## main",
        remote="origin",
        dirty_state="CLEAN",
        agents_md_present=True,
        readme_present=True,
        created_at="2026-06-06T00:00:00+00:00",
    )

    assert state.executable is False
    assert state.to_dict()["executable"] is False


def test_approval_item_requires_human(tmp_path: Path) -> None:
    item = build_approval_item("dirty worktree", "medium", "Review changes.", {"event": "test"})
    path = write_approval_item(item, tmp_path)
    parsed = json.loads(path.read_text(encoding="utf-8"))

    assert parsed["human_required"] is True
    assert parsed["executable"] is False


def test_notification_gate_suppresses_clean_success(tmp_path: Path) -> None:
    event = {"classification": "routine_success", "approval_needed": False, "safe_next_action": "none"}

    assert should_notify(event) is False
    assert emit_notification(event, tmp_path / "notifications.jsonl", print_to_console=False) is None


def test_notification_gate_emits_approval_needed(tmp_path: Path) -> None:
    event = {"classification": "approval_needed", "approval_needed": True, "safe_next_action": "review"}
    path = emit_notification(event, tmp_path / "notifications.jsonl", print_to_console=False)

    assert path is not None
    assert "approval_needed" in path.read_text(encoding="utf-8")


def test_packet_builder_uses_resolved_branch_not_hardcoded_main() -> None:
    draft = build_packet_draft(FakeRepoState())

    assert draft["branch"] == "feature/test-branch"
    assert "BRANCH: feature/test-branch" in draft["draft_text"]
    assert "BRANCH: main" not in draft["draft_text"]


def test_validator_router_does_not_invent_missing_validators() -> None:
    assert select_validator("example.txt") == "unsupported_extension"


def test_evidence_ledger_writes_jsonl(tmp_path: Path) -> None:
    path = append_evidence({"event": "test"}, tmp_path / "evidence.jsonl")

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["event"] == "test"


def test_forbidden_actions_are_blocked() -> None:
    classification = classify_state(FakeRepoState(), requested_action="auto_push")

    assert classification["blocked_action"] is True
    assert classification["approval_needed"] is True
    assert classification["classification"] == "blocked_action"


def test_packet_drafts_are_non_executable() -> None:
    draft = build_packet_draft(FakeRepoState())

    assert draft["executable"] is False
    assert "PLACEHOLDER_REQUIRES_ANTHONY_APPROVAL" in draft["draft_text"]


def test_no_live_trading_broker_secret_strings_are_implemented() -> None:
    root = Path("automation/operator_relief")
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in root.glob("*.py"))
    blocked_runtime_terms = [
        "place_live_order",
        "send_broker_order",
        "broker_sdk",
        "api_key =",
        "password =",
        "import openai",
        "from openai",
        "openai.chat",
    ]

    for term in blocked_runtime_terms:
        assert term not in combined
