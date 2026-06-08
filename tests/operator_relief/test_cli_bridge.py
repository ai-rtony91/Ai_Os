from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief.cli_bridge import (
    CLI_HANDOFF_BLOCKED,
    CLI_HANDOFF_READY,
    CliAvailability,
    build_cli_handoff,
)


def test_cli_bridge_creates_non_executable_handoff(tmp_path: Path) -> None:
    cli = CliAvailability(codex_path="C:/bin/codex.exe", openai_path=None, status="CLI_AVAILABLE")

    report = build_cli_handoff(
        task_id="task-001",
        prompt_text="PACKET CANDIDATE [ANTHONY_APPROVAL_REQUIRED]",
        repo_root=tmp_path,
        cli=cli,
    ).to_dict()

    assert report["status"] == CLI_HANDOFF_READY
    assert report["executable"] is False
    assert report["codex_invoked"] is False
    assert report["openai_api_invoked"] is False
    assert Path(report["handoff_path"]).is_file()
    payload = json.loads(Path(report["handoff_path"]).read_text(encoding="utf-8"))
    assert payload["executable"] is False


def test_cli_bridge_does_not_call_codex_by_default(tmp_path: Path) -> None:
    cli = CliAvailability(codex_path="C:/bin/codex.exe", openai_path=None, status="CLI_AVAILABLE")

    report = build_cli_handoff(
        task_id="task-002",
        prompt_text="bounded prompt [ANTHONY_APPROVAL_REQUIRED]",
        repo_root=tmp_path,
        cli=cli,
        write_evidence=False,
    ).to_dict()

    assert report["status"] == CLI_HANDOFF_READY
    assert report["cli_command"] == ["codex", "exec", "--prompt-file", "<handoff-prompt-path>"]
    assert report["codex_invoked"] is False


def test_cli_bridge_blocks_live_execution_token(tmp_path: Path) -> None:
    cli = CliAvailability(codex_path="C:/bin/codex.exe", openai_path=None, status="CLI_AVAILABLE")

    report = build_cli_handoff(
        task_id="task-003",
        prompt_text="CODEX-ONLY PROMPT\nAI_OS EXECUTION TOKEN: LIVE",
        repo_root=tmp_path,
        cli=cli,
    ).to_dict()

    assert report["status"] == CLI_HANDOFF_BLOCKED
    assert "Live AI_OS execution token" in report["reasons"][0]
    assert report["executable"] is False
