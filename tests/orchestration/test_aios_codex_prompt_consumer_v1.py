from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from automation.orchestration.relay.aios_codex_prompt_consumer_v1 import (
    PROTECTED_FLAGS,
    PromptValidationError,
    enqueue_prompt,
    validate_prompt,
)


def prompt_text(allowed: tuple[str, ...] = ("safe/file.py",)) -> str:
    paths = "\n".join(f"- {path}" for path in allowed)
    return f"""CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED
IDENTITY MARKER: AI_OS
SUPERVISOR IDENTITY: OWNER
WORKER IDENTITY: CODEX
PACKET ID: PACKET-1
MODE: APPLY
ZONE: LOCAL
LANE: TEST

ALLOWED PATHS
{paths}

FORBIDDEN PATHS
- AGENTS.md

APPROVAL AUTHORITY
Local edits only.

VALIDATOR CHAIN
python -m pytest

STOP POINT
Stop after validation.

MISSION
Perform bounded local work.

PREFLIGHT
git status --short

FINAL REPORT FORMAT
STATUS:
END OF PACKET
"""


@pytest.fixture
def flags() -> dict[str, bool]:
    return {name: False for name in PROTECTED_FLAGS}


def write_prompt(tmp_path: Path, text: str | None = None) -> Path:
    path = tmp_path / "next.md"
    path.write_text(text or prompt_text(), encoding="utf-8")
    return path


def test_valid_prompt_becomes_one_task_and_preserves_content(tmp_path: Path, flags: dict[str, bool]) -> None:
    prompt = write_prompt(tmp_path)
    relay = tmp_path / "relay"
    result = enqueue_prompt(prompt, relay, flags)
    task = json.loads(Path(result["target"]).read_text(encoding="utf-8"))
    assert result["status"] == "ENQUEUED"
    assert list((relay / "inbox").glob("*.task.json")) == [Path(result["target"])]
    assert task["prompt_text"] == prompt.read_text(encoding="utf-8")
    assert task["prompt_sha256"] == hashlib.sha256(prompt.read_bytes()).hexdigest()
    assert task["worker"] == task["provider"] == "codex"


def test_missing_required_field_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(PromptValidationError, match="missing required"):
        validate_prompt(write_prompt(tmp_path, prompt_text().replace("PREFLIGHT", "CHECKS")))


def test_placeholder_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(PromptValidationError, match="placeholder"):
        validate_prompt(write_prompt(tmp_path, prompt_text() + "\nTODO\n"))


def test_duplicate_digest_is_not_requeued(tmp_path: Path, flags: dict[str, bool]) -> None:
    prompt = write_prompt(tmp_path)
    relay = tmp_path / "relay"
    enqueue_prompt(prompt, relay, flags)
    duplicate = enqueue_prompt(prompt, relay, flags)
    assert duplicate["status"] == "DUPLICATE"
    assert len(list((relay / "inbox").glob("*.task.json"))) == 1


def test_negative_declarations_do_not_trigger_approval(tmp_path: Path, flags: dict[str, bool]) -> None:
    prompt = write_prompt(tmp_path, prompt_text() + "\nDo not commit, merge, contact OANDA, or trade live.\n")
    result = enqueue_prompt(prompt, tmp_path / "relay", flags)
    assert result["status"] == "ENQUEUED"


def test_positive_flag_routes_to_approvals(tmp_path: Path, flags: dict[str, bool]) -> None:
    flags["commit"] = True
    result = enqueue_prompt(write_prompt(tmp_path), tmp_path / "relay", flags)
    assert result["status"] == "APPROVAL_REQUIRED"
    assert "/approvals/" in str(result["target"])


def test_missing_or_malformed_flags_fail_closed(tmp_path: Path, flags: dict[str, bool]) -> None:
    flags.pop("commit")
    with pytest.raises(PromptValidationError, match="flags mismatch"):
        enqueue_prompt(write_prompt(tmp_path), tmp_path / "relay", flags)
    flags["commit"] = "false"  # type: ignore[assignment]
    with pytest.raises(PromptValidationError, match="boolean"):
        enqueue_prompt(write_prompt(tmp_path), tmp_path / "other", flags)


def test_dry_run_does_not_write_task(tmp_path: Path, flags: dict[str, bool]) -> None:
    result = enqueue_prompt(write_prompt(tmp_path), tmp_path / "relay", flags, dry_run=True)
    assert result["status"] == "DRY_RUN"
    assert not Path(result["target"]).exists()


def test_sha_mismatch_contract_is_present_in_worker() -> None:
    worker = Path("automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1").read_text(encoding="utf-8")
    assert "Get-FileHash -LiteralPath $promptPath -Algorithm SHA256" in worker
    assert "PROMPT_SHA256_MISMATCH" in worker


def test_allowed_path_mismatch_contract_is_present_in_worker() -> None:
    worker = Path("automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1").read_text(encoding="utf-8")
    assert "ALLOWED_PATH_MISMATCH" in worker
    assert "Task allowed paths do not match the validated prompt." in worker
