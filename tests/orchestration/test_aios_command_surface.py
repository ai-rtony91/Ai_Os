from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = REPO_ROOT / "aios.ps1"


def test_aios_launcher_exposes_autonomy_command_surface() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    for mode in (
        "autonomy-status",
        "autonomy-next",
        "approval-status",
        "self-build-status",
    ):
        assert mode in text


def test_aios_launcher_references_existing_read_only_targets() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")

    for target in (
        "New-AiOsAutonomyStatusReport.DRY_RUN.ps1",
        "Get-AiOsNextCommand.ps1",
        "Get-AiOsApprovalInboxSummary.DRY_RUN.ps1",
        "aios_self_build_decision_consumer.py",
        "latest_self_build_cycle.evidence.json",
    ):
        assert target in text


def test_new_autonomy_modes_do_not_add_protected_execution() -> None:
    text = LAUNCHER.read_text(encoding="utf-8")
    start = text.index('    "autonomy-status" {')
    end = text.index('    "runtime" {')
    new_mode_block = text[start:end]

    forbidden_terms = (
        "git push",
        "git commit",
        "git merge",
        "gh pr merge",
        "Register-ScheduledTask",
        "New-Service",
        "Move-AiOsPacketState",
    )
    for term in forbidden_terms:
        assert term not in new_mode_block
