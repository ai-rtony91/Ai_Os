"""Bounded local task discovery for Operator Relief autonomy spine v1."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .full_auto_policy import BLOCKED_PATH_KEYWORDS, FullAutoTask


DEFAULT_TASK_INPUT_DIR = Path("automation/operator_relief/task_input")
SUPPORTED_TASK_SUFFIX = ".json"
PLACEHOLDER_MARKERS = (
    "@filename",
    "path/to/file",
    "[REAL-FILENAME]",
    "{feature}",
    "TODO",
    "TBD",
)
FORBIDDEN_PATH_PATTERNS = (
    "AGENTS.md",
    "README.md",
    "docs/governance/",
    "docs/security/",
    "services/",
    "apps/",
    "telemetry/",
    "approval/operator_relief/pending/",
)
REQUIRED_TASK_FIELDS = (
    "task_id",
    "description",
    "allowed_paths",
    "forbidden_paths",
    "changed_paths",
    "requested_actions",
    "validator_targets",
)


@dataclass(frozen=True)
class DiscoveredTask:
    source_path: str
    task: FullAutoTask
    status: str = "DISCOVERED"
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["task"] = self.task.to_dict()
        return data


@dataclass(frozen=True)
class TaskDiscoveryResult:
    status: str
    tasks: list[DiscoveredTask]
    rejected: list[dict[str, Any]]
    input_paths: list[str]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "tasks": [task.to_dict() for task in self.tasks],
            "rejected": self.rejected,
            "input_paths": self.input_paths,
            "executable": False,
        }


def _normalize(path_text: str) -> str:
    return Path(path_text).as_posix()


def _contains_placeholder(value: Any) -> bool:
    if isinstance(value, str):
        return any(marker in value for marker in PLACEHOLDER_MARKERS)
    if isinstance(value, list):
        return any(_contains_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_placeholder(item) for item in value.values())
    return False


def _contains_forbidden_path(paths: list[str]) -> bool:
    normalized = [_normalize(path).lower() for path in paths]
    patterns = tuple(pattern.lower() for pattern in FORBIDDEN_PATH_PATTERNS)
    blocked_keywords = tuple(keyword.lower() for keyword in BLOCKED_PATH_KEYWORDS)
    return any(
        path == pattern.rstrip("/") or path.startswith(pattern)
        for path in normalized
        for pattern in patterns
    ) or any(keyword in path for path in normalized for keyword in blocked_keywords)


def _load_task(path: Path) -> FullAutoTask:
    if path.suffix.lower() != SUPPORTED_TASK_SUFFIX:
        raise ValueError("Unsupported task file extension.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed task JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Task payload must be a JSON object.")
    missing = [field for field in REQUIRED_TASK_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing required task fields: {', '.join(missing)}")
    if _contains_placeholder(payload):
        raise ValueError("Task payload contains unresolved placeholder text.")
    task = FullAutoTask(**payload)
    scoped_paths = task.allowed_paths + task.changed_paths + task.validator_targets
    if _contains_forbidden_path(scoped_paths):
        raise ValueError("Task payload references a forbidden, secret, broker/API, live-trading, or protected path.")
    return task


def discover_tasks(task_file: Path | None = None, input_dir: Path | None = None) -> TaskDiscoveryResult:
    root = input_dir or DEFAULT_TASK_INPUT_DIR
    candidates = [task_file] if task_file else sorted(root.glob("*.json")) if root.exists() else []
    tasks: list[DiscoveredTask] = []
    rejected: list[dict[str, Any]] = []

    for candidate in candidates:
        path = Path(candidate)
        try:
            tasks.append(DiscoveredTask(source_path=str(path), task=_load_task(path)))
        except (OSError, TypeError, ValueError) as exc:
            rejected.append({"source_path": str(path), "reason": str(exc), "executable": False})

    status = "DISCOVERED" if tasks and not rejected else "PARTIAL" if tasks else "BLOCKED"
    return TaskDiscoveryResult(status=status, tasks=tasks, rejected=rejected, input_paths=[str(path) for path in candidates])
