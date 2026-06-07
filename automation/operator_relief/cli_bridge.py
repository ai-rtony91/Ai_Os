"""Non-executing CLI bridge records for Operator Relief.

The bridge discovers local CLI availability and prepares handoff evidence only.
It does not call Codex, OpenAI, validators, workers, shells, or APIs.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CLI_AVAILABLE = "CLI_AVAILABLE"
CLI_MISSING = "CLI_MISSING"
CLI_HANDOFF_READY = "CLI_HANDOFF_READY"
CLI_HANDOFF_BLOCKED = "CLI_HANDOFF_BLOCKED"
DEFAULT_HANDOFF_DIR = Path("telemetry/operator_relief/cli_bridge")


@dataclass(frozen=True)
class CliAvailability:
    codex_path: str | None
    openai_path: str | None
    status: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CliHandoffRecord:
    status: str
    task_id: str
    cli_command: list[str]
    codex_path: str | None
    openai_path: str | None
    handoff_path: str | None
    reasons: list[str]
    prompt_text: str
    codex_invoked: bool = False
    openai_api_invoked: bool = False
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def discover_cli() -> CliAvailability:
    codex_path = shutil.which("codex")
    openai_path = shutil.which("openai")
    status = CLI_AVAILABLE if codex_path or openai_path else CLI_MISSING
    return CliAvailability(codex_path=codex_path, openai_path=openai_path, status=status, executable=False)


def _contains_live_execution_token(text: str) -> bool:
    return "AI_OS EXECUTION TOKEN" in text and "[ANTHONY_APPROVAL_REQUIRED]" not in text


def build_cli_handoff(
    task_id: str,
    prompt_text: str,
    repo_root: Path,
    handoff_dir: Path | str = DEFAULT_HANDOFF_DIR,
    cli: CliAvailability | None = None,
    write_evidence: bool = True,
) -> CliHandoffRecord:
    availability = cli or discover_cli()
    reasons: list[str] = []
    normalized_task_id = task_id.strip()
    if not normalized_task_id:
        reasons.append("task_id is required.")
    if not prompt_text.strip():
        reasons.append("prompt_text is required.")
    if _contains_live_execution_token(prompt_text):
        reasons.append("Live AI_OS execution token is not allowed in CLI handoff v1.")
    if availability.status == CLI_MISSING:
        reasons.append("No local Codex/OpenAI CLI command was discovered.")

    command = ["codex", "exec", "--prompt-file", "<handoff-prompt-path>"]
    if reasons:
        return CliHandoffRecord(
            status=CLI_HANDOFF_BLOCKED,
            task_id=normalized_task_id,
            cli_command=command,
            codex_path=availability.codex_path,
            openai_path=availability.openai_path,
            handoff_path=None,
            reasons=reasons,
            prompt_text=prompt_text,
            executable=False,
        )

    root = repo_root.resolve()
    output_dir = (root / Path(handoff_dir)).resolve()
    handoff_path = output_dir / f"{normalized_task_id}.handoff.json"
    record = CliHandoffRecord(
        status=CLI_HANDOFF_READY,
        task_id=normalized_task_id,
        cli_command=command,
        codex_path=availability.codex_path,
        openai_path=availability.openai_path,
        handoff_path=str(handoff_path),
        reasons=[],
        prompt_text=prompt_text,
        executable=False,
    )
    if write_evidence:
        output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "record": record.to_dict(),
            "executable": False,
        }
        handoff_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record
