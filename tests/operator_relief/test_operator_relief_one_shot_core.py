from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.operator_relief.evidence_ledger import append_evidence
from automation.operator_relief.notification_gate import notification_decision, record_notification_decision
from automation.operator_relief.packet_builder import build_packet_draft
from automation.operator_relief.run_operator_relief_loop import run_once
from automation.operator_relief.task_classifier import classify_state


@dataclass(frozen=True)
class FakeRepoState:
    repo_root: str = "C:\\Dev\\Ai.Os"
    branch: str = "main"
    git_status: str = "## main...origin/main"
    remote: str = "origin"
    dirty_state: str = "CLEAN"
    agents_md_present: bool = True
    readme_present: bool = True
    created_at: str = "2026-06-08T00:00:00+00:00"
    executable: bool = False


def test_packet_draft_is_non_executable() -> None:
    draft = build_packet_draft(FakeRepoState())

    assert draft["executable"] is False
    assert "CODEX-ONLY PROMPT" not in draft["draft_text"]
    assert "AI_OS EXECUTION TOKEN" not in draft["draft_text"]
    assert "NON-EXECUTABLE AI_OS PACKET DRAFT" in draft["draft_text"]


def test_clean_state_needs_no_wake() -> None:
    classification = classify_state(FakeRepoState())
    decision = notification_decision(classification)

    assert classification["classification"] == "routine_success"
    assert classification["needs_operator"] is False
    assert decision["wake_requested"] is False
    assert decision["live_delivery_allowed"] is False


def test_blocker_and_sos_are_separate() -> None:
    blocked = classify_state(FakeRepoState(), requested_action="auto_push")
    sos = classify_state(FakeRepoState(), sos_triggers=["loop_dead"])

    assert blocked["classification"] == "blocked_action"
    assert blocked["needs_operator"] is True
    assert blocked["sos_worthy"] is False
    assert sos["classification"] == "sos_worthy"
    assert sos["needs_operator"] is True
    assert sos["sos_worthy"] is True


def test_evidence_writes_jsonl_to_temp_path(tmp_path: Path) -> None:
    path = append_evidence({"event": "test"}, tmp_path / "evidence.jsonl")

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["event"] == "test"
    assert json.loads(lines[0])["executable"] is False


def test_clean_notification_decision_writes_no_record(tmp_path: Path) -> None:
    classification = classify_state(FakeRepoState())

    assert record_notification_decision(classification, tmp_path / "notifications.jsonl") is None


def test_blocked_notification_decision_is_local_only(tmp_path: Path) -> None:
    classification = classify_state(FakeRepoState(), requested_action="auto_commit")
    path = record_notification_decision(classification, tmp_path / "notifications.jsonl")

    assert path is not None
    record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert record["decision"]["live_delivery_allowed"] is False
    assert record["decision"]["wake_requested"] is False
    assert record["classification"]["blocked_action"] is True


def test_run_once_uses_generated_or_temp_evidence_paths(tmp_path: Path, monkeypatch) -> None:
    class Completed:
        returncode = 0
        stderr = ""

        def __init__(self, stdout: str) -> None:
            self.stdout = stdout

    def fake_run(command, cwd, capture_output, text, shell, check, timeout):
        if command[1:] == ["rev-parse", "--show-toplevel"]:
            return Completed(str(tmp_path))
        if command[1:] == ["branch", "--show-current"]:
            return Completed("main")
        if command[1:] == ["status", "--short", "--branch"]:
            return Completed("## main...origin/main")
        if command[1:] == ["remote", "-v"]:
            return Completed("origin")
        raise AssertionError(command)

    (tmp_path / "AGENTS.md").write_text("rules", encoding="utf-8")
    (tmp_path / "README.md").write_text("readme", encoding="utf-8")
    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_once(
        repo_root=tmp_path,
        evidence_path=tmp_path / "generated" / "evidence.jsonl",
        notification_log_path=tmp_path / "generated" / "notifications.jsonl",
    )

    assert result["packet_draft_executable"] is False
    assert Path(str(result["evidence_path"])).exists()
    assert result["notification_path"] is None


def test_no_forbidden_runtime_strings_in_operator_relief_package() -> None:
    root = REPO_ROOT / "automation" / "operator_relief"
    combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in root.glob("*.py"))
    forbidden_terms = [
        "register-scheduledtask",
        "schtasks",
        "telegram",
        "webhook",
        "adb.exe",
        "git add",
        "git commit",
        "git push",
        "place_live_order",
        "send_broker_order",
        "api_key =",
        "pass" + "word =",
    ]

    for term in forbidden_terms:
        assert term not in combined
