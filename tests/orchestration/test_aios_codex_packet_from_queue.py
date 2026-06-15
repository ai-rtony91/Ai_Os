from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_codex_packet_from_queue.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_codex_packet_from_queue", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def item(**overrides: object) -> dict[str, object]:
    payload = {
        "action_id": "build_platform_status_reader",
        "allowed_paths": ["automation/orchestration/platform_status_reader.py"],
        "validators": ["python -m pytest tests/orchestration/test_platform_status_reader.py"],
        "protected_action_flags": {"git_commit": False},
    }
    payload.update(overrides)
    return payload


def test_imports_and_schema():
    module = load_module()
    assert module.SCHEMA == "AIOS_CODEX_PACKET_FROM_QUEUE.v1"


def test_builds_codex_only_packet_text():
    module = load_module()
    result = module.build_codex_packet_from_queue_item(item())
    prompt = result["codex_prompt_text"]
    assert result["packet_ready"] is True
    assert prompt.startswith("CODEX-ONLY PROMPT")
    assert "AI_OS EXECUTION TOKEN" in prompt
    assert "AI_OS BOOTSTRAP REQUIRED" in prompt
    assert "WORKTREE: C:\\Dev\\Ai.Os" in prompt
    assert "BRANCH: main" in prompt
    assert "WRITE ONLY:" in prompt
    assert "STOP:" in prompt


def test_rejects_missing_allowed_paths_and_protected_actions():
    module = load_module()
    assert module.build_codex_packet_from_queue_item(item(allowed_paths=[]))["reason_code"] == "allowed_paths_missing"
    protected = item(protected_action_flags={"git_commit": True})
    assert module.build_codex_packet_from_queue_item(protected)["reason_code"] == "protected_action_required"


def test_no_codex_launch_or_api_calls():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "openai", "anthropic", "start-process"]:
        assert forbidden not in source
