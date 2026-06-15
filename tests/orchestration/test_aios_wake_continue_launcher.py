from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "automation" / "orchestration" / "Start-AiOsWakeContinue.ps1"


def script_source() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_launcher_script_exists():
    assert SCRIPT_PATH.exists()


def test_launcher_initializes_wake_args_for_no_arg_strict_mode():
    source = script_source()
    assert "[string[]]$WakeArgs = @()" in source
    assert "Set-StrictMode -Version Latest" in source


def test_launcher_calls_wake_continue_path():
    source = script_source()
    assert r".\automation\orchestration\aios_wake_continue.py" in source
    assert "& python $WakeScript @EffectiveArgs" in source


def test_launcher_contains_safe_default_args():
    source = script_source()
    for expected in [
        "--goal",
        "forex-paper-bot",
        "--apply",
        "--max-cycles",
        "3",
        "--max-repairs",
        "1",
        "--write-resume-state",
        "--write-control-plane-status",
        "--emit-continuation-controller",
    ]:
        assert expected in source


def test_launcher_forwards_explicit_args_as_override():
    source = script_source()
    assert "ValueFromRemainingArguments" in source
    assert "$WakeArgs.Count -gt 0" in source
    assert "$WakeArgs" in source
    assert "$DefaultArgs" in source


def test_launcher_has_no_protected_git_actions():
    source = script_source().lower()
    for forbidden in ["git add", "git commit", "git push", "git merge"]:
        assert forbidden not in source


def test_launcher_has_no_runtime_or_trading_activation_terms():
    source = script_source().lower()
    for forbidden in [
        "scheduler",
        "daemon",
        "worker",
        "broker",
        "live trading",
        "credentials",
        "real order",
        "webhook",
    ]:
        assert forbidden not in source
