from __future__ import annotations

from pathlib import Path


AIOS_PS1 = Path("aios.ps1")


def _operator_relief_block() -> str:
    source = AIOS_PS1.read_text(encoding="utf-8")
    start = source.index('    "operator-relief" {')
    end = source.index('\n\n    "runtime" {', start)
    return source[start:end]


def _bridge_block() -> str:
    source = AIOS_PS1.read_text(encoding="utf-8")
    start = source.index('    "bridge" {')
    end = source.index('\n\n    "runtime" {', start)
    return source[start:end]


def _runtime_bridge_block() -> str:
    source = AIOS_PS1.read_text(encoding="utf-8")
    start = source.index('    "runtime-bridge" {')
    end = source.index('\n\n    "night-mission" {', start)
    return source[start:end]


def _night_mission_block() -> str:
    source = AIOS_PS1.read_text(encoding="utf-8")
    start = source.index('    "night-mission" {')
    end = source.index('\n\n    "runtime" {', start)
    return source[start:end]


def _commit_push_dry_run_block() -> str:
    source = AIOS_PS1.read_text(encoding="utf-8")
    start = source.index('    "commit-push-dry-run" {')
    end = source.index('\n\n    "runtime" {', start)
    return source[start:end]


def test_aios_mode_includes_operator_relief() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")

    assert '"operator-relief"' in source
    assert '[string]$TaskJson = ""' in source


def test_aios_mode_includes_bridge() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")

    assert '"bridge"' in source
    assert ".\\aios.ps1 -Mode bridge -TaskJson" in source


def test_aios_mode_includes_runtime_bridge() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")

    assert '"runtime-bridge"' in source
    assert ".\\aios.ps1 -Mode runtime-bridge" in source


def test_aios_mode_includes_night_mission() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")

    assert '"night-mission"' in source
    assert '[int]$MaxCycles = 3' in source
    assert ".\\aios.ps1 -Mode night-mission -MaxCycles 3" in source


def test_aios_mode_includes_commit_push_dry_run() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")

    assert '"commit-push-dry-run"' in source
    assert ".\\aios.ps1 -Mode commit-push-dry-run -TaskJson" in source


def test_operator_relief_route_requires_task_json_path() -> None:
    block = _operator_relief_block()

    assert '[string]::IsNullOrWhiteSpace($TaskJson)' in block
    assert 'Test-Path -LiteralPath $TaskJson -PathType Leaf' in block
    assert 'BLOCKED: -TaskJson must point to a real FullAutoTask JSON file.' in block


def test_operator_relief_route_runs_only_full_auto_dry_run_module() -> None:
    block = _operator_relief_block()

    assert '$moduleName = "automation.operator_relief.run_full_auto_dry_run"' in block
    assert 'python -m $moduleName --task-json $resolvedTaskJson' in block
    assert "powershell -NoProfile" not in block
    assert "Start-Process" not in block
    assert "git " not in block


def test_operator_relief_route_prints_safety_banner() -> None:
    block = _operator_relief_block()

    assert "Mode: DRY_RUN" in block
    assert "Python module: $moduleName" in block
    assert "no commit" in block
    assert "no push" in block
    assert "no merge" in block
    assert "no OpenAI API" in block
    assert "no recursive Codex" in block
    assert "no telemetry write" in block
    assert "no approval queue write" in block
    assert "no daemon" in block


def test_bridge_route_requires_task_json_path() -> None:
    block = _bridge_block()

    assert '[string]::IsNullOrWhiteSpace($TaskJson)' in block
    assert 'Test-Path -LiteralPath $TaskJson -PathType Leaf' in block
    assert 'BLOCKED: -TaskJson must point to a real inbox FullAutoTask JSON file.' in block


def test_bridge_route_runs_only_inbox_outbox_bridge_module() -> None:
    block = _bridge_block()

    assert '$moduleName = "automation.operator_relief.inbox_outbox_bridge"' in block
    assert 'python -m $moduleName --task-json $resolvedTaskJson' in block
    assert "powershell -NoProfile" not in block
    assert "Start-Process" not in block
    assert "git " not in block


def test_bridge_route_prints_safety_banner() -> None:
    block = _bridge_block()

    assert "Mode: DRY_RUN" in block
    assert "Python module: $moduleName" in block
    assert "no commit" in block
    assert "no push" in block
    assert "no merge" in block
    assert "no OpenAI API" in block
    assert "no recursive Codex" in block
    assert "no daemon" in block
    assert "no watcher" in block
    assert "no service" in block
    assert "no shell passthrough" in block
    assert "no source mutation" in block


def test_runtime_bridge_route_runs_only_runtime_bridge_module() -> None:
    block = _runtime_bridge_block()

    assert '$moduleName = "automation.operator_relief.runtime_bridge"' in block
    assert 'python -m $moduleName' in block
    assert "--task-json" not in block
    assert "Start-Process" not in block
    assert "git " not in block


def test_runtime_bridge_route_prints_safety_banner() -> None:
    block = _runtime_bridge_block()

    assert "Mode: DRY_RUN" in block
    assert "Python module: $moduleName" in block
    assert "no commit" in block
    assert "no push" in block
    assert "no merge" in block
    assert "no rebase" in block
    assert "no force-push" in block
    assert "no OpenAI API" in block
    assert "no recursive Codex" in block
    assert "no daemon" in block
    assert "no watcher" in block
    assert "no service" in block
    assert "no shell passthrough" in block


def test_night_mission_route_runs_only_unattended_mission_module() -> None:
    block = _night_mission_block()

    assert '$moduleName = "automation.operator_relief.unattended_mission_runner"' in block
    assert 'python -m $moduleName --max-cycles $MaxCycles' in block
    assert "Start-Process" not in block
    assert "git " not in block
    assert "powershell -NoProfile" not in block


def test_night_mission_route_prints_safe_usage() -> None:
    block = _night_mission_block()

    assert "Mode: DRY_RUN" in block
    assert "one-shot only" in block
    assert "no daemon" in block
    assert "no watcher" in block
    assert "no service" in block
    assert "no commit" in block
    assert "no push" in block
    assert "no merge" in block
    assert "-MaxCycles must be greater than zero" in block


def test_commit_push_dry_run_route_requires_task_json_path() -> None:
    block = _commit_push_dry_run_block()

    assert '[string]::IsNullOrWhiteSpace($TaskJson)' in block
    assert 'Test-Path -LiteralPath $TaskJson -PathType Leaf' in block
    assert 'BLOCKED: -TaskJson must point to a real FullAutoTask JSON file.' in block


def test_commit_push_dry_run_route_runs_only_dry_run_executor_module() -> None:
    block = _commit_push_dry_run_block()

    assert '$moduleName = "automation.operator_relief.auto_commit_push_executor"' in block
    assert 'python -m $moduleName --task-json $resolvedTaskJson --validators-passed' in block
    assert "--mode" not in block
    assert "Start-Process" not in block
    assert "git " not in block


def test_commit_push_dry_run_route_prints_safety_banner() -> None:
    block = _commit_push_dry_run_block()

    assert "Mode: DRY_RUN" in block
    assert "dry-run only" in block
    assert "no commit" in block
    assert "no push" in block
    assert "no merge" in block
    assert "no rebase" in block
    assert "no force-push" in block
    assert "no OpenAI API" in block
    assert "no recursive Codex" in block
    assert "no daemon" in block
    assert "no watcher" in block
    assert "no service" in block
    assert "no shell passthrough" in block


def test_aios_operator_relief_safe_cli_source_has_no_apply_or_unsafe_execution_exposure() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")
    forbidden_markers = [
        "APPLY_COMMIT_PUSH",
        "git commit",
        "git push",
        "git merge",
        "git rebase",
        "--force",
        "OpenAI(",
        "openai.",
        "call_codex",
        "Start-Process",
        "New-Service",
        "Register-ScheduledTask",
    ]
    for marker in forbidden_markers:
        assert marker not in source
