from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_repo_state_evidence.py"
FIXED_NOW = "2026-06-14T12:00:00Z"


def _load():
    spec = importlib.util.spec_from_file_location("aios_repo_state_evidence", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _runner(stdout_by_key: dict[tuple[str, ...], tuple[int, str, str]]):
    def run(args, **_kwargs):
        key = tuple(args[1:])
        code, stdout, stderr = stdout_by_key.get(key, (0, "", ""))
        return subprocess.CompletedProcess(args=args, returncode=code, stdout=stdout, stderr=stderr)

    return run


def _clean_runner(root: Path):
    return _runner(
        {
            ("rev-parse", "--show-toplevel"): (0, str(root), ""),
            ("branch", "--show-current"): (0, "main\n", ""),
            ("status", "--short", "--branch", "--untracked-files=all"): (
                0,
                "## main...origin/main\n",
                "",
            ),
        }
    )


def test_repo_state_collector_emits_required_fields(tmp_path: Path) -> None:
    m = _load()
    report = m.collect_repo_state(tmp_path, generated_at_utc=FIXED_NOW, runner=_clean_runner(tmp_path))

    assert {
        "schema_version",
        "system",
        "component",
        "generated_at_utc",
        "repo_root",
        "branch",
        "git_available",
        "inside_worktree",
        "is_clean",
        "status_short",
        "tracked_dirty_files",
        "untracked_files",
        "staged_files",
        "ahead_behind",
        "safe_for_apply",
        "blocked_reason",
        "evidence_quality",
    }.issubset(report)


def test_clean_simulated_repo_marks_safe_for_apply_true(tmp_path: Path) -> None:
    m = _load()
    report = m.collect_repo_state(tmp_path, generated_at_utc=FIXED_NOW, runner=_clean_runner(tmp_path))

    assert report["branch"] == "main"
    assert report["is_clean"] is True
    assert report["safe_for_apply"] is True
    assert report["blocked_reason"] is None
    assert report["evidence_quality"] == "strong"


def test_dirty_simulated_repo_marks_safe_for_apply_false(tmp_path: Path) -> None:
    m = _load()
    runner = _runner(
        {
            ("rev-parse", "--show-toplevel"): (0, str(tmp_path), ""),
            ("branch", "--show-current"): (0, "main\n", ""),
            ("status", "--short", "--branch", "--untracked-files=all"): (
                0,
                "## main...origin/main\n M tracked.py\n?? new.py\nA  staged.py\n",
                "",
            ),
        }
    )

    report = m.collect_repo_state(tmp_path, generated_at_utc=FIXED_NOW, runner=runner)

    assert report["is_clean"] is False
    assert report["safe_for_apply"] is False
    assert report["blocked_reason"] == "dirty_working_tree"
    assert report["tracked_dirty_files"] == ["tracked.py", "staged.py"]
    assert report["untracked_files"] == ["new.py"]
    assert report["staged_files"] == ["staged.py"]


def test_git_unavailable_or_failure_marks_unsafe(tmp_path: Path) -> None:
    m = _load()

    def missing_git(args, **_kwargs):
        raise FileNotFoundError("git")

    missing = m.collect_repo_state(tmp_path, generated_at_utc=FIXED_NOW, runner=missing_git)
    assert missing["git_available"] is False
    assert missing["safe_for_apply"] is False
    assert missing["evidence_quality"] == "missing"

    failing = m.collect_repo_state(
        tmp_path,
        generated_at_utc=FIXED_NOW,
        runner=_runner({("rev-parse", "--show-toplevel"): (1, "", "not a repo")}),
    )
    assert failing["git_available"] is True
    assert failing["inside_worktree"] is False
    assert failing["safe_for_apply"] is False


def test_output_json_parses_and_is_deterministic_ignoring_timestamp(tmp_path: Path) -> None:
    m = _load()
    first = m.collect_repo_state(tmp_path, generated_at_utc=FIXED_NOW, runner=_clean_runner(tmp_path))
    second = m.collect_repo_state(tmp_path, generated_at_utc=FIXED_NOW, runner=_clean_runner(tmp_path))
    output = m.write_repo_state_report(tmp_path, first)
    parsed = json.loads(output.read_text(encoding="utf-8"))

    assert parsed == first
    assert first == second
