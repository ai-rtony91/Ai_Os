"""Collect local AI_OS repository state without mutating the repo."""

from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class RepoState:
    repo_root: str
    branch: str
    git_status: str
    remote: str
    dirty_state: str
    agents_md_present: bool
    readme_present: bool
    created_at: str
    executable: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
        timeout=20,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def collect_repo_state(repo_root: Path | None = None) -> RepoState:
    root = Path(repo_root or Path.cwd()).resolve()
    git_root = Path(_run_git(root, ["rev-parse", "--show-toplevel"])).resolve()
    branch = _run_git(git_root, ["branch", "--show-current"]) or "DETACHED"
    status = _run_git(git_root, ["status", "--short", "--branch"])
    remote = _run_git(git_root, ["remote", "-v"])
    dirty_lines = [
        line
        for line in status.splitlines()
        if line.strip() and not line.startswith("##")
    ]
    return RepoState(
        repo_root=str(git_root),
        branch=branch,
        git_status=status,
        remote=remote,
        dirty_state="DIRTY" if dirty_lines else "CLEAN",
        agents_md_present=(git_root / "AGENTS.md").exists(),
        readme_present=(git_root / "README.md").exists(),
        created_at=datetime.now(timezone.utc).isoformat(),
        executable=False,
    )

