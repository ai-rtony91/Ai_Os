from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "relay"
    / "Get-AiOsRelayWorkerEvidenceDrain.DRY_RUN.ps1"
)


def adapter_text() -> str:
    return ADAPTER.read_text(encoding="utf-8")


def test_adapter_file_exists() -> None:
    assert ADAPTER.is_file()


def test_adapter_contains_no_forbidden_mutation_commands() -> None:
    text = adapter_text()
    forbidden = (
        "Set-Content",
        "Add-Content",
        "Move-Item",
        "Remove-Item",
        "New-Item",
        "Copy-Item",
        "Start-Process",
        "Start-Job",
        "Register-ScheduledTask",
        "schtasks",
        "New-Service",
        "sc.exe",
        "git add",
        "git commit",
        "git push",
        "git merge",
        "git reset",
        "git clean",
    )
    for command in forbidden:
        assert command not in text


def test_adapter_does_not_execute_relay_worker_or_runner() -> None:
    text = adapter_text()

    assert "Invoke-AiOsRelayWorker.ps1" not in text
    assert "Invoke-AiOsRelayRunner.ps1" not in text
    assert "Invoke-AiOsProviderWorker" not in text
    assert "Invoke-AiOsCliWithTimeout.ps1" not in text
    assert "& $" not in text


def test_adapter_does_not_reference_provider_commands() -> None:
    text = adapter_text()

    forbidden = (
        "provider_command",
        "provider_args",
        "codex exec",
        "claude ",
        "openai ",
        "custom provider",
    )
    for term in forbidden:
        assert term not in text


def test_adapter_exposes_false_execution_and_mutation_flags() -> None:
    text = adapter_text()

    assert "mutation_performed = $false" in text
    assert "worker_invoked = $false" in text
    assert "provider_cli_invoked = $false" in text
    assert "relay_state_mutated = $false" in text


def test_adapter_reads_relay_evidence_folders() -> None:
    text = adapter_text()

    for folder in ("inbox", "running", "done", "error", "outbox", "approvals"):
        assert f'{folder} = Join-Path $relayRoot "{folder}"' in text
    assert "Get-ChildItem -LiteralPath $Path -File" in text
    assert "counts = $counts" in text
    assert "latest_done" in text
    assert "latest_error" in text
    assert "latest_outbox_report" in text
    assert "approval_wait_count" in text
    assert "has_pending_inbox" in text
    assert "has_running_packets" in text


def test_adapter_has_no_watch_mode() -> None:
    text = adapter_text()

    assert "[switch]$Watch" not in text
    assert "$Watch" not in text
    assert "-Watch" not in text
