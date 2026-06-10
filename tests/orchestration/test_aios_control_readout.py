from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = REPO_ROOT / "aios.ps1"


def _control_block(text: str) -> str:
    start = text.index('    "control" {')
    end = text.index('    "autonomy-status" {')
    return text[start:end]


def test_control_mode_is_exposed_and_described() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    assert '"control"' in text
    assert ".\\aios.ps1 -Mode control # one-command operator control readout" in text


def test_control_mode_references_compact_safe_sources() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    control_block = _control_block(text)

    for term in (
        "Get-AiOsNextCommand.ps1",
        "-QuietJson",
        "git status --short --branch",
    ):
        assert term in text

    for flag in (
        "approvals_performed",
        "approval_inbox_mutated",
        "apply_gate_mutated",
        "protected_action_allowed",
        "commit_performed",
        "push_performed",
        "merge_performed",
        "dispatch_performed",
    ):
        assert flag in text


def test_control_block_stays_read_only_and_does_not_run_reports_or_cycle() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    control_block = _control_block(text)

    for term in (
        "git push",
        "git commit",
        "git merge",
        "gh pr merge",
        "gh pr create",
        "Register-ScheduledTask",
        "New-Service",
        "Start-Job",
        "Move-AiOsPacketState",
        "approved_by_human = true",
        "approval_status = completed",
        "OANDA",
        "live_trading",
        "broker",
        "webhook",
        "automation/self_build/aios_self_build_cycle.py",
        "New-AiOsAutonomyStatusReport.DRY_RUN.ps1",
    ):
        assert term not in control_block
