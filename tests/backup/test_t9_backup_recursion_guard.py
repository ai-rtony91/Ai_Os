import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "backup" / "Start-AiOsT9SnapshotBackup.ps1"


def _powershell_exe():
    exe = shutil.which("powershell") or shutil.which("pwsh")
    if exe is None:
        raise AssertionError("PowerShell is required for T9 backup recursion guard tests.")
    return exe


def _run_guard(source, backup_root, snapshot, candidate_sources=None, approved_backup_root=None):
    candidate_sources = candidate_sources or [source]
    approved_backup_root = approved_backup_root or backup_root
    candidates_json = json.dumps(candidate_sources)
    command = f"""
$script = Get-Content -Raw -LiteralPath '{SCRIPT_PATH}'
$marker = '$expectedSource ='
$functionBlock = $script.Substring(0, $script.IndexOf($marker))
Invoke-Expression $functionBlock
$candidates = ConvertFrom-Json @'
{candidates_json}
'@
$result = Test-AiOsBackupRecursionGuard `
    -SourceFullPath (ConvertTo-AiOsFullPath -Path '{source}') `
    -BackupRootFullPath (ConvertTo-AiOsFullPath -Path '{backup_root}') `
    -SnapshotPathFullPath (ConvertTo-AiOsFullPath -Path '{snapshot}') `
    -ApprovedBackupRootFullPath (ConvertTo-AiOsFullPath -Path '{approved_backup_root}') `
    -CandidateCopySourcePaths @($candidates) `
    -ExcludedFolderNames @('.git','node_modules','snapshots','current_mirror','AIOS_BACKUP*')
$result | ConvertTo-Json -Depth 8
"""
    completed = subprocess.run(
        [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def _run_relative_exclusion(relative_path):
    command = f"""
$script = Get-Content -Raw -LiteralPath '{SCRIPT_PATH}'
$marker = '$expectedSource ='
$functionBlock = $script.Substring(0, $script.IndexOf($marker))
Invoke-Expression $functionBlock
Test-AiOsRelativePathExcluded `
    -RelativePath '{relative_path}' `
    -ExcludedFolderNames @('.git','node_modules','snapshots','current_mirror','AIOS_BACKUP*','secrets','credentials') `
    -ExcludedFilePatterns @('.env','*.env','.env.*','*.pem','*.key','id_rsa','id_ed25519','*.pfx','*.p12','*secret*','*secrets*','*credential*')
"""
    completed = subprocess.run(
        [_powershell_exe(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip().lower() == "true"


def test_source_inside_backup_root_blocks():
    result = _run_guard(
        source=r"D:\T9_FOB\Ai_Os",
        backup_root=r"D:\T9_FOB",
        snapshot=r"D:\T9_FOB\AIOS_BACKUP_test",
    )

    assert result["recursive_backup_detected"] is True
    assert result["source_inside_backup_root"] is True
    assert result["safe_to_copy"] is False


def test_backup_root_inside_source_blocks():
    result = _run_guard(
        source=r"C:\Dev\Ai.Os",
        backup_root=r"C:\Dev\Ai.Os\AIOS_BACKUP_nested",
        snapshot=r"C:\Dev\Ai.Os\AIOS_BACKUP_nested\AIOS_BACKUP_test",
        approved_backup_root=r"C:\Dev\Ai.Os\AIOS_BACKUP_nested",
    )

    assert result["recursive_backup_detected"] is True
    assert result["backup_root_inside_source"] is True
    assert result["safe_to_copy"] is False


def test_snapshot_inside_source_blocks():
    result = _run_guard(
        source=r"C:\Dev\Ai.Os",
        backup_root=r"D:\T9_FOB",
        snapshot=r"C:\Dev\Ai.Os\snapshots\AIOS_BACKUP_test",
    )

    assert result["recursive_backup_detected"] is True
    assert result["snapshot_inside_source"] is True
    assert result["safe_to_copy"] is False


def test_normal_aios_to_t9_path_passes():
    result = _run_guard(
        source=r"C:\Dev\Ai.Os",
        backup_root=r"D:\T9_FOB",
        snapshot=r"D:\T9_FOB\AIOS_BACKUP_test",
    )

    assert result["recursive_backup_detected"] is False
    assert result["recursive_backup_reason"] == "NONE"
    assert result["safe_to_copy"] is True


def test_candidate_backup_folder_pattern_blocks():
    result = _run_guard(
        source=r"C:\Dev\Ai.Os",
        backup_root=r"D:\T9_FOB",
        snapshot=r"D:\T9_FOB\AIOS_BACKUP_test",
        candidate_sources=[r"C:\Dev\Ai.Os\snapshots\old.txt"],
    )

    assert result["recursive_backup_detected"] is True
    assert result["candidate_copy_source_contains_backup_pattern"] is True
    assert result["safe_to_copy"] is False


def test_delta_candidate_excludes_secret_env_and_snapshot_paths():
    assert _run_relative_exclusion(r".env") is True
    assert _run_relative_exclusion(r"local.env") is True
    assert _run_relative_exclusion(r"id_rsa") is True
    assert _run_relative_exclusion(r"client.pfx") is True
    assert _run_relative_exclusion(r"secrets\api.key") is True
    assert _run_relative_exclusion(r"snapshots\old\file.txt") is True


def test_excluded_folder_list_contains_required_backup_and_cache_names():
    text = SCRIPT_PATH.read_text(encoding="utf-8")

    for expected in [".git", "node_modules", "snapshots", "current_mirror", "AIOS_BACKUP*"]:
        assert f'"{expected}"' in text
