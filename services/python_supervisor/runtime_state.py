"""Runtime state preview helpers for the AI_OS Python supervisor skeleton."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RuntimeState:
    mode: str
    repo_root: str
    execution_enabled: bool
    queue_mutation_enabled: bool
    approval_mutation_enabled: bool
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_runtime_state(repo_root: Path) -> RuntimeState:
    return RuntimeState(
        mode="DRY_RUN",
        repo_root=str(repo_root),
        execution_enabled=False,
        queue_mutation_enabled=False,
        approval_mutation_enabled=False,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
