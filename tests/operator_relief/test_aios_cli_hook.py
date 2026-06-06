from __future__ import annotations

from pathlib import Path


AIOS_PS1 = Path("aios.ps1")


def _operator_relief_block() -> str:
    source = AIOS_PS1.read_text(encoding="utf-8")
    start = source.index('    "operator-relief" {')
    end = source.index('\n\n    "runtime" {', start)
    return source[start:end]


def test_aios_mode_includes_operator_relief() -> None:
    source = AIOS_PS1.read_text(encoding="utf-8")

    assert '"operator-relief"' in source
    assert '[string]$TaskJson = ""' in source


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
