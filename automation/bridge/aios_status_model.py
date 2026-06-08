from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


PACKET_ID = "AIOS-PHASE-0-TO-4-INFRASTRUCTURE-BRIDGE-ONE-SHOT-APPLY-001"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_git(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        ["git", *args],
        cwd=str(repo_root),
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def list_git_files(repo_root: Path, *pathspecs: str) -> list[str]:
    code, stdout, _stderr = run_git(repo_root, ["ls-files", *pathspecs])
    if code != 0 or not stdout:
        return []
    return [line.strip().replace("\\", "/") for line in stdout.splitlines() if line.strip()]


def first_existing(repo_root: Path, candidates: Iterable[str]) -> list[str]:
    found: list[str] = []
    for candidate in candidates:
        path = repo_root / candidate
        if path.exists():
            found.append(candidate.replace("\\", "/"))
    return found


def matching_files(files: Iterable[str], terms: Iterable[str], limit: int = 200) -> list[str]:
    lowered_terms = [term.lower() for term in terms]
    matches: list[str] = []
    for file_name in files:
        lower = file_name.lower()
        if "todo" in lower:
            continue
        if any(term in lower for term in lowered_terms):
            matches.append(file_name)
            if len(matches) >= limit:
                break
    return matches


@dataclass
class RepoSnapshot:
    packet_id: str
    timestamp_utc: str
    repo_root: str
    branch: str
    remote_origin: str
    git_status_short: str
    dirty_files: list[str] = field(default_factory=list)


def capture_repo_snapshot(repo_root: Path) -> RepoSnapshot:
    _code_root, root_stdout, _root_stderr = run_git(repo_root, ["rev-parse", "--show-toplevel"])
    _code_branch, branch_stdout, _branch_stderr = run_git(repo_root, ["branch", "--show-current"])
    _code_status, status_stdout, _status_stderr = run_git(repo_root, ["status", "--short", "--branch"])
    _code_remote, remote_stdout, _remote_stderr = run_git(repo_root, ["remote", "-v"])
    dirty_files = [
        line[3:].strip()
        for line in status_stdout.splitlines()
        if line and not line.startswith("## ")
    ]
    return RepoSnapshot(
        packet_id=PACKET_ID,
        timestamp_utc=utc_now(),
        repo_root=(root_stdout or str(repo_root)).replace("\\", "/"),
        branch=branch_stdout,
        remote_origin=remote_stdout,
        git_status_short=status_stdout,
        dirty_files=dirty_files,
    )


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(payload, "__dataclass_fields__"):
        data = asdict(payload)
    else:
        data = payload
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json_if_exists(path: Path) -> object | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"path": str(path), "status": "INVALID_JSON"}


def write_markdown(path: Path, title: str, sections: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", "", "Status: evidence, not authority.", ""]
    for heading, value in sections.items():
        lines.extend([f"## {heading}", ""])
        if isinstance(value, list):
            if value:
                lines.extend(f"- `{item}`" if isinstance(item, str) else f"- {item}" for item in value)
            else:
                lines.append("- None")
        elif isinstance(value, dict):
            lines.append("```json")
            lines.append(json.dumps(value, indent=2, sort_keys=True))
            lines.append("```")
        else:
            lines.append(str(value))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
