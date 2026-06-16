import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_DELTA_HELPER = REPO_ROOT / "automation" / "orchestration" / "backups" / "Get-AiOsBackupWorkDelta.ps1"
POST_MAIN_SCRIPT = REPO_ROOT / "automation" / "orchestration" / "backups" / "Start-AiOsPostMainUpdateBackup.DRY_RUN.ps1"
DAILY_SNAPSHOT_SCRIPT = REPO_ROOT / "automation" / "orchestration" / "daily_snapshot" / "New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1"
T9_SCRIPT = REPO_ROOT / "scripts" / "backup" / "Start-AiOsT9SnapshotBackup.ps1"


def _powershell_exe():
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if exe is None:
        raise AssertionError("PowerShell is required for T9 backup work metric tests.")
    return exe


def _run_powershell_command(command: str) -> str:
    completed = subprocess.run(
        [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def _run_powershell_file(*args: str) -> dict:
    completed = subprocess.run(
        [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def test_post_main_backup_report_has_required_metric_groups_and_missing_baseline_status():
    report = _run_powershell_file(
        str(POST_MAIN_SCRIPT),
        "-OutputJson",
        "-BackupTimeslotLabel",
        "3 PM",
        "-StateFilePath",
        r"telemetry\backup_reports\AIOS_POST_MAIN_UPDATE_BACKUP_STATE_TEST_MISSING.json",
    )

    for key in [
        "backup_copied_metrics",
        "dev_work_delta_metrics",
        "daily_work_metrics",
        "timeslot_work_metrics",
        "courtesy_sos",
        "backup_timeslot_label",
        "backup_timeslot_local",
        "backup_window_start",
        "backup_window_end",
        "last_successful_backup_commit",
        "current_commit",
    ]:
        assert key in report

    assert report["status"] == "BASELINE_UNKNOWN"
    assert report["dev_work_delta_metrics"]["available"] is False
    assert report["backup_copied_metrics"]["full_snapshot_or_incremental"] == "FULL_SNAPSHOT_PREVIEW"
    assert report["backup_copied_metrics"]["copied_mb"] == 0
    assert "patch_delta_kb" in report["dev_work_delta_metrics"]
    assert report["courtesy_sos"]["required"] is True
    assert report["courtesy_sos"]["mode"] == "REPORT_ONLY"
    assert report["courtesy_sos"]["scheduler_active"] is False
    assert report["state_update_preview"]["dry_run_only"] is True
    assert report["state_update_preview"]["writes_performed"] == 0


def test_daily_snapshot_includes_daily_work_metrics_without_running_backup():
    report = _run_powershell_file(str(DAILY_SNAPSHOT_SCRIPT), "-Json")

    assert report["mode"] == "DRY_RUN"
    assert report["backup_ran"] is False
    assert report["backup_copied_metrics"]["backup_mode"] == "DAILY_SNAPSHOT_NO_BACKUP"
    assert report["backup_copied_metrics"]["copied_bytes"] == 0
    assert "daily_work_metrics" in report
    assert "patch_delta_today_kb" in report["daily_work_metrics"]
    assert "timeslot_work_metrics" in report


def test_timeslot_labels_support_examples_and_arbitrary_labels():
    command = f"""
. '{WORK_DELTA_HELPER}'
$three = Resolve-AiOsBackupTimeslotWindow -TimeslotLabel '3 PM' -Now ([datetime]'2026-06-15T12:00:00')
$ten = Resolve-AiOsBackupTimeslotWindow -TimeslotLabel '10 PM' -Now ([datetime]'2026-06-15T12:00:00')
$custom = Resolve-AiOsBackupTimeslotWindow -TimeslotLabel 'post-merge-sync' -Now ([datetime]'2026-06-15T12:00:00')
@($three, $ten, $custom) | ConvertTo-Json -Depth 5
"""
    windows = json.loads(_run_powershell_command(command))

    assert windows[0]["timeslot_label"] == "3 PM"
    assert "15:00:00" in windows[0]["timeslot_local"]
    assert windows[1]["timeslot_label"] == "10 PM"
    assert "22:00:00" in windows[1]["timeslot_local"]
    assert windows[2]["timeslot_label"] == "post-merge-sync"


def test_robocopy_exit_one_is_ok_and_snapshot_size_is_separate_from_dev_delta():
    command = f"""
. '{WORK_DELTA_HELPER}'
$copied = New-AiOsBackupCopiedMetrics `
    -BackupMode 'Full' `
    -BackupRoot 'D:\\T9_FOB' `
    -Destination 'D:\\T9_FOB\\AIOS_BACKUP_example' `
    -RobocopyExit 1 `
    -CopiedFilesCount 4819 `
    -CopiedBytes 23907532 `
    -ExcludedPaths @('.git') `
    -ExcludedSecretPatterns @('.env','*.env','*.pem','*.key','id_rsa','id_ed25519','*.pfx','*.p12','*secret*','*secrets*') `
    -FullSnapshotOrIncremental 'FULL_SNAPSHOT'
$dev = [pscustomobject]@{{
    changed_files_count = 28
    insertions = 3319
    deletions = 41
    patch_delta_kb = 204.41
    patch_delta_mb = 0.20
}}
[pscustomobject]@{{ copied = $copied; dev = $dev }} | ConvertTo-Json -Depth 5
"""
    report = json.loads(_run_powershell_command(command))

    assert report["copied"]["robocopy_status"] == "OK"
    assert report["copied"]["copied_files_count"] == 4819
    assert report["copied"]["copied_mb"] != report["dev"]["patch_delta_mb"]
    assert report["dev"]["changed_files_count"] == 28


def test_t9_snapshot_script_has_global_backup_metric_schema_and_secret_exclusions():
    text = T9_SCRIPT.read_text(encoding="utf-8")

    for expected in [
        "backup_copied_metrics",
        "dev_work_delta_metrics",
        "daily_work_metrics",
        "timeslot_work_metrics",
        "courtesy_sos",
        "BackupTimeslotLabel",
        ".env",
        "*.env",
        "*.pem",
        "*.key",
        "id_rsa",
        "id_ed25519",
        "*.pfx",
        "*.p12",
        "*secret*",
        "*secrets*",
    ]:
        assert expected in text


def test_backup_reporting_does_not_activate_scheduler_daemon_delete_or_mirror_behavior():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [WORK_DELTA_HELPER, POST_MAIN_SCRIPT, DAILY_SNAPSHOT_SCRIPT, T9_SCRIPT]
    )

    forbidden = [
        "Register-ScheduledTask",
        "Start-ScheduledTask",
        "New-ScheduledTask",
        "New-Service",
        "Start-Service",
        "/MIR",
        "/PURGE",
        "Remove-Item -Recurse",
    ]
    for token in forbidden:
        assert token not in combined

