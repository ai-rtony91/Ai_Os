import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COURTESY_HELPER = REPO_ROOT / "automation" / "orchestration" / "backups" / "New-AiOsBackupCourtesySos.ps1"


def _powershell_exe():
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if exe is None:
        raise AssertionError("PowerShell is required for T9 backup courtesy SOS tests.")
    return exe


def _run_powershell(command: str) -> dict:
    completed = subprocess.run(
        [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_courtesy_sos_success_message_is_report_only():
    command = f"""
. '{COURTESY_HELPER}'
$copied = [pscustomobject]@{{ copied_mb = 0.20; copied_files_count = 28 }}
$dev = [pscustomobject]@{{ patch_delta_kb = 204.41; changed_files_count = 28; insertions = 3319; deletions = 41 }}
$daily = [pscustomobject]@{{ patch_delta_today_kb = 204.41; commits_today_count = 3 }}
New-AiOsBackupCourtesySos `
    -Status 'SUCCESS' `
    -TimeslotLabel '3 PM' `
    -CopiedMetrics $copied `
    -DevWorkDeltaMetrics $dev `
    -DailyWorkMetrics $daily `
    -BaseCommit 'abc123' `
    -CurrentCommit 'def456' `
    -Destination 'D:\\T9_FOB\\AIOS_BACKUP_example' `
    -RobocopyExit 1 | ConvertTo-Json -Depth 5
"""
    result = _run_powershell(command)

    assert result["required"] is True
    assert result["mode"] == "REPORT_ONLY"
    assert result["notify_on_success"] is True
    assert result["notify_on_failure"] is True
    assert result["scheduler_active"] is False
    assert "AIOS T9 backup complete." in result["message"]
    assert "Time slot: 3 PM" in result["message"]
    assert "Backup copied: 0.2 MB / 28 files" in result["message"]
    assert "New dev work: 204.41 KB patch / 28 files / 3319 insertions / 41 deletions" in result["message"]
    assert "Safety: secrets excluded, no delete/mirror behavior." in result["message"]


def test_courtesy_sos_failure_message_is_report_only():
    command = f"""
. '{COURTESY_HELPER}'
New-AiOsBackupCourtesySos `
    -Status 'FAILED' `
    -TimeslotLabel '10 PM' `
    -CopiedMetrics $null `
    -DevWorkDeltaMetrics $null `
    -DailyWorkMetrics $null `
    -BaseCommit 'abc123' `
    -CurrentCommit 'def456' `
    -Destination 'D:\\T9_FOB\\AIOS_BACKUP_example' `
    -RobocopyExit 9 `
    -FailedFilesCount 2 `
    -FailedDirsCount 1 `
    -LogPath 'D:\\T9_FOB\\AIOS_BACKUP_example\\AIOS_BACKUP_ROBOCOPY.log' `
    -Failure | ConvertTo-Json -Depth 5
"""
    result = _run_powershell(command)

    assert result["required"] is True
    assert result["mode"] == "REPORT_ONLY"
    assert result["scheduler_active"] is False
    assert "AIOS T9 backup failed." in result["message"]
    assert "Time slot: 10 PM" in result["message"]
    assert "Robocopy exit: 9" in result["message"]
    assert "Failed files: 2" in result["message"]
    assert "Failed dirs: 1" in result["message"]
    assert "Safety: no delete/mirror behavior performed." in result["message"]
