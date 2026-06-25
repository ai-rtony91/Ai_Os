from __future__ import annotations

import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.dev.aios_operator_fast_preflight_validator_v1 import (  # noqa: E402
    CommandResult,
    command_plan,
    evaluate_operator_fast_preflight,
    main,
)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    return repo


def fake_runner(
    *,
    branch: str = "main",
    status: str = "## main...origin/main\n",
    remote: str = "origin  https://github.com/ai-rtony91/Ai_Os.git (fetch)\n",
    validator_returncode: int = 0,
):
    def runner(command, cwd, timeout):  # noqa: ANN001
        command_tuple = tuple(command)
        if command_tuple == ("git", "status", "--short", "--branch"):
            return CommandResult(command_tuple, 0, status, "")
        if command_tuple == ("git", "branch", "--show-current"):
            return CommandResult(command_tuple, 0, f"{branch}\n", "")
        if command_tuple == ("git", "remote", "-v"):
            return CommandResult(command_tuple, 0, remote, "")
        if command_tuple[0:3] == ("python", "-m", "pytest"):
            return CommandResult(command_tuple, validator_returncode, "tests ran", "")
        if command_tuple[0:3] == ("python", "-m", "py_compile"):
            return CommandResult(command_tuple, validator_returncode, "", "")
        return CommandResult(command_tuple, 99, "", "unexpected command")

    return runner


def test_missing_repo_root_blocks(tmp_path: Path) -> None:
    result = evaluate_operator_fast_preflight(
        repo_root=tmp_path / "missing",
        command_runner=fake_runner(),
    )

    assert result["safe_to_continue"] is False
    assert result["branch_ok"] is False
    assert "repo root is missing" in result["next_safe_action"]


def test_missing_git_blocks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()

    result = evaluate_operator_fast_preflight(repo_root=repo, command_runner=fake_runner())

    assert result["safe_to_continue"] is False
    assert "not a git repo" in result["next_safe_action"]


def test_branch_mismatch_blocks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = evaluate_operator_fast_preflight(
        repo_root=repo,
        expected_branch="main",
        command_runner=fake_runner(branch="feature/work"),
    )

    assert result["safe_to_continue"] is False
    assert result["branch_ok"] is False
    assert "expected branch" in result["next_safe_action"]


def test_clean_correct_branch_with_passing_mocked_commands_allows_continue(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)

    result = evaluate_operator_fast_preflight(
        repo_root=repo,
        expected_branch="main",
        run_forex_loss_gate_tests=True,
        command_runner=fake_runner(),
    )

    assert result["safe_to_continue"] is True
    assert result["branch_ok"] is True
    assert result["validators_passed"] is True
    assert len(result["validators_run"]) == 2


def test_dirty_files_block_safe_to_continue(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    status = "## main...origin/main\n M README.md\n"

    result = evaluate_operator_fast_preflight(
        repo_root=repo,
        command_runner=fake_runner(status=status),
    )

    assert result["safe_to_continue"] is False
    assert result["dirty_files"] == ["README.md"]
    assert "unrelated dirty files" in result["next_safe_action"]


def test_packet_allowed_dirty_files_do_not_block_during_creation(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    status = (
        "## main...origin/main\n"
        "?? scripts/dev/aios_operator_fast_preflight_validator_v1.py\n"
        "?? tests/dev/test_aios_operator_fast_preflight_validator_v1.py\n"
        "?? Reports/dev/AIOS_OPERATOR_FAST_PREFLIGHT_VALIDATOR_V1_REPORT.md\n"
    )

    result = evaluate_operator_fast_preflight(
        repo_root=repo,
        run_forex_loss_gate_tests=True,
        command_runner=fake_runner(status=status),
    )

    assert result["safe_to_continue"] is True
    assert result["dirty_count"] == 3


def test_failed_validator_blocks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = evaluate_operator_fast_preflight(
        repo_root=repo,
        run_forex_loss_gate_tests=True,
        command_runner=fake_runner(validator_returncode=1),
    )

    assert result["safe_to_continue"] is False
    assert result["validators_passed"] is False
    assert len(result["validators_failed"]) == 2


def test_json_output_is_valid_when_json_flag_is_used(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    output = io.StringIO()

    exit_code = main(
        ["--repo-root", str(repo), "--branch", "main", "--json"],
        command_runner=fake_runner(),
        stdout=output,
    )
    parsed = json.loads(output.getvalue())

    assert exit_code == 0
    assert parsed["packet_id"]
    assert parsed["safe_to_continue"] is True


def test_operator_benefit_text_is_present_for_anthony(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = evaluate_operator_fast_preflight(repo_root=repo, command_runner=fake_runner())
    benefit = result["operator_benefit"].lower()

    assert "anthony" in benefit
    assert "repeated command copying" in benefit
    assert "babysitting validator steps" in benefit


def test_safety_flags_remain_conservative(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    result = evaluate_operator_fast_preflight(repo_root=repo, command_runner=fake_runner())
    safety = result["safety"]

    assert safety["local_only"] is True
    assert safety["network_used"] is False
    assert safety["credentials_used"] is False
    assert safety["repo_mutation_performed"] is False
    assert safety["broker_calls_allowed"] is False
    assert safety["order_placement_allowed"] is False
    assert safety["commit_allowed"] is False
    assert safety["push_allowed"] is False


def test_no_mutation_commands_are_included_in_allowlisted_command_plan() -> None:
    forbidden = {
        "add",
        "commit",
        "push",
        "merge",
        "reset",
        "stash",
        "checkout",
        "switch",
        "rebase",
        "clean",
    }

    for command in command_plan(run_forex_loss_gate_tests=True):
        assert not any(part in forbidden for part in command)
