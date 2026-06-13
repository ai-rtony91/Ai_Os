import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "backup" / "Start-AiOsT9SnapshotBackup.ps1"


def _powershell_exe():
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if exe is None:
        raise AssertionError("PowerShell is required for T9 backup non-interference tests.")
    return exe


def _run_powershell(command: str) -> str:
    completed = subprocess.run(
        [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def _load_script_functions_command(extra: str) -> str:
    return f"""
$script = Get-Content -Raw -LiteralPath '{SCRIPT_PATH}'
$marker = '$expectedSource ='
$functionBlock = $script.Substring(0, $script.IndexOf($marker))
Invoke-Expression $functionBlock
{extra}
"""


def test_backup_report_root_prefers_t9_backup_reports_outside_active_repo():
    command = _load_script_functions_command(
        r"""
Resolve-AiOsBackupReportRoot `
    -PreferredRoot 'D:\T9_FOB\backup_reports' `
    -FallbackRoot 'C:\Temp\AIOS_T9_BACKUP' `
    -SourceRoot 'C:\Dev\Ai.Os'
"""
    )

    result = _run_powershell(command)

    assert result == r"D:\T9_FOB\backup_reports"


def test_backup_report_root_falls_back_when_preferred_root_is_inside_repo():
    command = _load_script_functions_command(
        r"""
Resolve-AiOsBackupReportRoot `
    -PreferredRoot 'C:\Dev\Ai.Os\telemetry\backup_reports' `
    -FallbackRoot 'C:\Temp\AIOS_T9_BACKUP' `
    -SourceRoot 'C:\Dev\Ai.Os'
"""
    )

    result = _run_powershell(command)

    assert result == r"C:\Temp\AIOS_T9_BACKUP"


def test_self_validation_dirty_allowlist_only_accepts_exact_backup_files():
    command = _load_script_functions_command(
        r"""
$allowedStatus = [pscustomobject]@{
    lines = @(
        '## feature/governed-self-development-closure-v1',
        ' M scripts/backup/Start-AiOsT9SnapshotBackup.ps1',
        '?? tests/backup/test_t9_snapshot_backup_noninterference.py'
    )
}
$blockedStatus = [pscustomobject]@{
    lines = @(
        '## feature/governed-self-development-closure-v1',
        ' M scripts/backup/Start-AiOsT9SnapshotBackup.ps1',
        '?? telemetry/backup_reports/AIOS_BACKUP_IN_PROGRESS.lock'
    )
}
$allowed = Test-AiOsBackupSelfValidationDirtyState -GitStatus $allowedStatus
$blocked = Test-AiOsBackupSelfValidationDirtyState -GitStatus $blockedStatus
"$allowed|$blocked"
"""
    )

    result = _run_powershell(command)

    assert result == "True|False"


def test_backup_script_no_longer_assigns_lock_under_active_repo_telemetry():
    text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert 'Join-Path $normalizedSource "telemetry\\backup_reports"' not in text
    assert "$backupReportRoot = Resolve-AiOsBackupReportRoot" in text
    assert 'Join-Path $normalizedBackupRoot "backup_reports"' in text
    assert '"AIOS_BACKUP_IN_PROGRESS.lock"' in text


def test_robocopy_excludes_do_not_use_invalid_full_backup_wildcard_paths():
    text = SCRIPT_PATH.read_text(encoding="utf-8")

    assert 'Join-Path $normalizedBackupRoot "AIOS_BACKUP*"' not in text
    assert '"/MIR"' not in text
    assert '"tests/backup/test_t9_snapshot_backup_noninterference.py"' in text


def test_console_output_reports_no_active_repo_mutation_and_lock_path():
    text = SCRIPT_PATH.read_text(encoding="utf-8")

    for expected in [
        "Source size:",
        "Snapshot path:",
        "Robocopy exit code:",
        "File count copied:",
        "Byte count copied:",
        "Final snapshot size:",
        "Manifest path:",
        "Lock path:",
        "active_repo_mutation = NO",
    ]:
        assert expected in text
