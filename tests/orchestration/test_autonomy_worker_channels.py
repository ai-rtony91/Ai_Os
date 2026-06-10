"""Tests for autonomy worker-channel map."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/autonomy_worker_channels/Get-AiOsWorkerChannelMap.DRY_RUN.ps1"


def run_worker_map(*, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-OutputPath",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_worker_channel_map_includes_all_required_channels(tmp_path: Path) -> None:
    out = tmp_path / "channels.json"
    result = run_worker_map(output=out)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip())
    names = {c["name"] for c in payload["channels"]}

    assert "Codex CLI local" in names
    assert "Codex App worktree" in names
    assert "Codex Web/cloud" in names
    assert "ChatGPT desktop/mobile supervisor" in names
    assert "OpenAI CLI optional" in names
    assert "GitHub PR checks" in names
    assert "AI_OS internal router" in names
    assert out.exists()

    safe = {c["name"]: c["command"] for c in payload["channels"]}
    for _, command in safe.items():
        assert "merge" not in command.lower()
        assert "force-push" not in command.lower()
        assert "delete branch" not in command.lower()
        assert "apply" not in command.lower()
        assert "broker" not in command.lower()


def test_worker_channel_map_payload_is_stored(tmp_path: Path) -> None:
    out = tmp_path / "channels.json"
    result = run_worker_map(output=out)
    assert result.returncode == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "AIOS-AUTONOMY-WORKER-CHANNEL-MAP-V1"
    assert payload["channels"][0]["role"] in {"execution", "execution", "connector", "supervisor", "optional_tool", "verification", "coordinator"}
