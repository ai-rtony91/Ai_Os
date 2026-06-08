# T9 Backup Patch Validation DRY_RUN

Status: DRY_RUN REPORT - evidence only.
Packet ID: T9_BACKUP_PATCH_VALIDATION_DRY_RUN_002
Lane: T9_BACKUP_PATCH_VALIDATION_DRY_RUN
Worker: Codex CLI Worker
Branch: feature/full-operator-relief-closed-loop-v1
Worktree: C:\Dev\Ai.Os

## Purpose

Validate the current patch to `scripts/backup/Start-AiOsT9SnapshotBackup.ps1` by reading the git diff only. This report does not edit scripts, protected files, scheduled tasks, source files, broker paths, trading paths, secrets, commits, or pushes.

## Files Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- Git diff for `scripts/backup/Start-AiOsT9SnapshotBackup.ps1`

## Diff Summary

The patch adds:

- `Format-AiOsSizeReport`, which reports byte counts as `KB / MB`.
- A narrowed `Get-AiOsGitStatus` classification:
  - raw dirty lines are still captured.
  - untracked `Reports/` and `telemetry/` lines are classified as allowed report-only output.
  - all other dirty lines remain blocking.
- `Add-AiOsBackupReportFields`, which adds source, synced/copied, destination, verification, and failure-reason fields to result objects.
- `Write-AiOsFinalBackupReport`, which prints one visible final report with:
  - status
  - backup mode
  - selected reason
  - source path
  - source size in KB/MB
  - backup root
  - snapshot path
  - manifest path
  - verification status
  - synced/copied size in KB/MB
  - backup-root size after run in KB/MB
  - robocopy exit code
  - process exit code
  - failure reason
  - failure report path
  - mutation/scheduler markers
- `Write-AiOsFailureBackupReport`, which writes failed results to `telemetry/backup_reports/AIOS_T9_BACKUP_FAILURE_<timestamp>.json`.
- Calls to the final report helper in preview, manifest-only success, delta success, full backup success/failure result handling, and catch/failure handling.

## Validation Questions

### 1. Does the patch guarantee final visible SUCCESS reports?

Diff-only answer: mostly yes for non-JSON manual/scheduled console output.

Evidence:

- Preview mode now calls `Write-AiOsFinalBackupReport` before `exit 0`.
- Manifest-only success now calls `Write-AiOsFinalBackupReport` before `exit 0`.
- Delta success now calls `Write-AiOsFinalBackupReport` before `exit 0`.
- Full backup completion now calls `Write-AiOsFinalBackupReport` before `exit $exitCode`.
- The report includes `Status: $($Result.status)`, so successful result objects print `Status: SUCCESS`.

Limit:

- When `-OutputJson` is used, the script emits JSON instead of the visible host report. That appears intentional and preserves machine-readable mode, but it means "visible report" is guaranteed for normal non-JSON output, not for `-OutputJson`.

### 2. Does the patch guarantee final visible FAILED reports?

Diff-only answer: yes for the catch/failure path in non-JSON mode, and yes for full-mode verification/robocopy failure that reaches the full-mode result block.

Evidence:

- The catch block now builds a failed result, adds report fields, attempts to write failure JSON, and calls `Write-AiOsFinalBackupReport` when `-OutputJson` is not set.
- Full-mode robocopy or verification failure sets `$manifestStatus = "FAILED"`, records `$failureReason`, adds report fields, and calls `Write-AiOsFinalBackupReport`.
- The report prints `Failure reason: <reason>` when present, otherwise `Failure reason: NONE`.

Limit:

- This is a diff-only validation. A real failing run still must confirm the console/session actually shows the final report before process exit.

### 3. Is failure JSON written under `telemetry/backup_reports/`?

Diff-only answer: yes for catch/failure exceptions and for non-throwing full-mode failed manifests.

Evidence:

- `$backupReportRoot` is `Join-Path $normalizedSource "telemetry\backup_reports"`.
- `Write-AiOsFailureBackupReport` creates the directory if needed.
- It writes `AIOS_T9_BACKUP_FAILURE_<timestamp>.json` under that root.
- The catch block calls `Write-AiOsFailureBackupReport`.
- The full backup result block now calls `Write-AiOsFailureBackupReport` when `$manifestStatus -eq "FAILED"` before JSON or console output is emitted.

Limit:

- This remains a diff-and-parser validation. A real full-mode failed run was not executed because it can create backup artifacts before failure.

## Dirty Repo Behavior

### 4. Do untracked `Reports/` and `telemetry/` folders no longer block backup?

Diff-only answer: yes, for git status lines that begin with `?? Reports/` or `?? telemetry/`.

Evidence:

```powershell
if ($line -match '^\?\?\s+(Reports[\\/]|telemetry[\\/])') {
    $allowedReportOnlyUntracked += $line
} else {
    $blockingDirtyLines += $line
}
```

`is_clean` now means no blocking dirty lines, not no dirty lines at all.

Limit:

- Only untracked report/telemetry lines are allowed.
- Modified tracked files under `Reports/` or `telemetry/` would still be blocking because they do not match `??`.

### 5. Do modified tracked files still block unless `-AllowDirty` is passed?

Diff-only answer: yes.

Evidence:

- Any line not matching untracked `Reports/` or `telemetry/` goes into `blocking_dirty_lines`.
- The existing guard remains:

```powershell
if (-not $Preview -and -not $AllowDirty -and -not $gitStatus.is_clean) {
    throw "DIRTY_REPO: ..."
}
```

- A modified tracked file line such as ` M scripts/backup/Start-AiOsT9SnapshotBackup.ps1` does not match the allowed untracked output pattern, so it remains blocking unless `-AllowDirty` is passed.

## What Still Must Be Manually Tested

Run these manually only when Anthony wants to exercise the backup worker. They may inspect local disk state or write backup/report output, so they were not run in this DRY_RUN validation packet.

1. Preview success path:

```powershell
powershell -NoProfile -File .\scripts\backup\Start-AiOsT9SnapshotBackup.ps1 -Preview
```

Expected:

- final visible report prints.
- source size appears in KB/MB.
- synced/copied size is `0.00 KB / 0.00 MB`.
- exit code is `0`.

2. Dirty-state allowed output path:

With only untracked `Reports/` and/or `telemetry/` output present, run preview first. Then run an approved non-preview backup only if Anthony intends to create a backup.

Expected:

- untracked output folders do not trigger `DIRTY_REPO`.
- modified tracked files still trigger `DIRTY_REPO`.

3. Catch-path failure report:

Use a safe, intentionally invalid parameter such as a wrong source path in a controlled manual test:

```powershell
powershell -NoProfile -File .\scripts\backup\Start-AiOsT9SnapshotBackup.ps1 -SourceRepo C:\Dev\DOES_NOT_EXIST
```

Expected:

- final visible report prints `Status: FAILED`.
- failure reason is exact.
- JSON failure report is written under `telemetry/backup_reports/`.
- exit code is `1`.

4. Full backup failure path:

Only test this with explicit operator intent, because it can create backup artifacts before failure.

Expected:

- visible report prints `Status: FAILED`.
- manifest path is reported.
- verification status is `FAILED`.
- separate telemetry failure JSON is written under `telemetry/backup_reports/AIOS_T9_BACKUP_FAILURE_<timestamp>.json`.

## Remaining Gap

No remaining diff-level gap is known for the documented non-throwing full-mode failure telemetry requirement. The patched full backup result block writes `telemetry/backup_reports/AIOS_T9_BACKUP_FAILURE_<timestamp>.json` whenever `$manifestStatus -eq "FAILED"`, and catch-path failures continue to use the same helper.

Remaining validation limit:

- A live full-mode failure was not executed because it can create backup artifacts before failing.

## Final APPLY Validation

Final validation after the narrow APPLY fix:

- PowerShell parser check: PASS.
- Preview validation command: PASS. `powershell -NoProfile -File .\scripts\backup\Start-AiOsT9SnapshotBackup.ps1 -Preview` exited `0` and printed final report `Status: PREVIEW`.
- `git diff --check`: PASS with only the known T9 script LF-to-CRLF warning.

Additional runtime note:

- An earlier preview attempt exposed strict-mode `.Count` handling in report-count arguments when changed-file collections collapse to a scalar. The script now wraps those report-count inputs in `@(...)` before reading `.Count`, preserving preview/report behavior without changing backup copy semantics.

## DRY_RUN Conclusion

The patch is directionally correct and covers the main operator-visible problem. It guarantees final visible reports for normal non-JSON success and failure output paths by diff structure. It guarantees telemetry failure JSON for thrown failures and for non-throwing full-mode failed manifests by calling the same failure-report helper in both paths. Final parser and preview validation passed.
