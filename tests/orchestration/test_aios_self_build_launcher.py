from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "automation" / "orchestration" / "Start-AiOsSelfBuild.DRY_RUN.ps1"


def script_text() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def test_launcher_exists_and_calls_controller():
    source = script_text()
    assert SCRIPT_PATH.exists()
    assert "C:\\Dev\\Ai.Os" in source
    assert "aios_overnight_build_controller.py" in source
    assert "DRY_RUN" in source
    assert "@EffectiveArgs" in source


def test_launcher_forwards_explicit_args():
    source = script_text()
    assert "ValueFromRemainingArguments" in source
    assert "$SelfBuildArgs" in source


def test_launcher_does_not_contain_protected_or_runtime_actions():
    source = script_text().lower()
    for forbidden in [
        "git add",
        "git commit",
        "git push",
        "git merge",
        "register-scheduledtask",
        "start-scheduledtask",
        "new-service",
        "start-service",
        "start-process",
        "broker",
        "credential",
        "real_order",
        "webhook",
    ]:
        assert forbidden not in source
