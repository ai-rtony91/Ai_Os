# AI_OS T9 Backup Workflow

Status: Specification only. No backup automation is implemented by this document.

## Purpose

The Samsung T9 is support infrastructure for AI_OS backups, logs, reports, exports, evidence packets, dashboard assets, and operator recovery material.

This workflow records the approved backup architecture before any script, folder creation, robocopy command, or scheduled task is created.

## Non-Goals

- The T9 is not the canonical repo.
- The T9 does not replace `C:\Dev\Ai.Os`.
- The T9 must not store secrets, credentials, API keys, broker credentials, or live trading material.
- This document does not create scheduled tasks.
- This document does not run robocopy.
- This document does not create folders on the T9.
- This document does not copy, move, delete, rename, stage, commit, push, reset, clean, or stash anything.
- This document does not authorize reusing high-risk reorganization scripts for backup.

## Discovered T9 State

- T9 drive detected at `D:`.
- T9 label: `T9_FOB`.
- Filesystem: `exFAT`.
- Free space: about 931 GB.
- No `AIOS_T9`, `AI_OS_T9`, or `AiOS_T9` folder exists at `C:\` or `D:\`.
- No recursive exact `AIOS_T9` folder was found on `D:\`.
- Existing T9 numbered layout exists:
  - `D:\00_COMMAND_CENTER`
  - `D:\01_ACTIVE_OPERATIONS`
  - `D:\02_AI_WORKERS`
  - `D:\04_REPOS`
  - `D:\05_MEDIA`
  - `D:\06_MODELS`
  - `D:\07_KNOWLEDGE`
  - `D:\08_ARCHIVE`
  - `D:\99_STAGING`
  - `D:\AIOS_TERMINAL`
- No dedicated T9 or robocopy backup helper was found.
- No active Task Scheduler creation script was found.
- `automation/Ai_Os_Reorganize.ps1` is high risk and must not be reused for backup.
- Local `main` was aligned with `origin/main` during discovery.
- Known untracked backlog existed during discovery and must not be touched by backup design or future helper creation unless explicitly approved.

## Approved Root Strategy

Use the existing T9 numbered layout.

Do not create `D:\AIOS_T9` unless separately approved by the operator in a future APPLY lane.

The T9 layout should remain readable as an operator support drive, not as a second canonical repo or a hidden automation target.

## Recommended Folder Mapping

| Purpose | Recommended path |
|---|---|
| Command center / dashboard | `D:\00_COMMAND_CENTER\AI_OS` |
| Active operations | `D:\01_ACTIVE_OPERATIONS\AI_OS` |
| Repo backup mirror | `D:\04_REPOS\AI_OS\Ai_Os\current_mirror` |
| Snapshots | `D:\04_REPOS\AI_OS\Ai_Os\snapshots\YYYY-MM-DD_HHMM` |
| Logs | `D:\04_REPOS\AI_OS\Ai_Os\logs` |
| Archive | `D:\08_ARCHIVE\AI_OS` |
| Staging | `D:\99_STAGING\AI_OS` |

## Backup Source

```text
C:\Dev\Ai.Os
```

## Backup Destination

Primary mirror:

```text
D:\04_REPOS\AI_OS\Ai_Os\current_mirror
```

Snapshot destination:

```text
D:\04_REPOS\AI_OS\Ai_Os\snapshots
```

## Log Path

Recommended backup log directory:

```text
D:\04_REPOS\AI_OS\Ai_Os\logs
```

Recommended log naming pattern:

```text
backup_YYYY-MM-DD_HHMM.log
```

## Recommended Exclusions

Future backup helpers should exclude:

- `.git\`
- `.venv\`
- `venv\`
- `node_modules\`
- build, cache, and generated output folders
- `.codex_backups\`
- temporary files
- secrets, credentials, API keys, broker credentials, and live trading material
- known untracked backlog until classified or explicitly approved for backup

The future helper should report excluded categories plainly so the operator knows what was intentionally skipped.

## Recommended Schedule

Schedule creation is not approved by this document.

Recommended schedule after a DRY_RUN helper proves safe:

1. Manual DRY_RUN first.
2. Manual APPLY backup second, with explicit operator approval.
3. One daily scheduled backup after the work session ends, around 21:00 local time.
4. Optional logon/startup check in report-only mode.

No Task Scheduler registration may occur until a future APPLY lane explicitly authorizes:

- exact script path
- exact task name
- exact schedule
- exact source and destination
- exact exclusions
- log path
- rollback/removal plan
- validation steps

## Future Helper Design

The next helper should start as DRY_RUN/report-only.

Recommended future script path:

```text
automation/orchestration/backup_t9/Invoke-AiOsT9Backup.DRY_RUN.ps1
```

Initial DRY_RUN behavior should:

- confirm `C:\Dev\Ai.Os` exists
- confirm `D:` exists and is labeled `T9_FOB`
- confirm the recommended destination paths
- print the planned mirror and snapshot paths
- print the planned exclusions
- print the planned robocopy command as text only
- refuse to run robocopy
- refuse to create scheduled tasks
- refuse to touch known untracked backlog
- produce console output only

An APPLY version must be separate and explicitly approved later.

## Robocopy Safety Notes

Robocopy must not run in this specification lane.

Future robocopy use should avoid destructive mirror behavior until proven safe. In particular:

- Do not use `/MIR` until the destination is confirmed to be dedicated to AI_OS backup output.
- Prefer a non-destructive copy preview first.
- Log every run.
- Confirm source and destination before execution.
- Stop if the T9 drive label does not match `T9_FOB`.
- Stop if source is not `C:\Dev\Ai.Os`.
- Stop if destination resolves outside the approved T9 layout.

## Risk Controls

- The T9 filesystem is `exFAT`; NTFS permissions and some metadata may not preserve exactly.
- The T9 must not become a second source of truth.
- Known untracked backlog must not be copied into authority accidentally.
- High-risk reorganizer scripts must not be reused for backup.
- Backup helpers must not silently delete destination files.
- Task Scheduler must not be created until manual DRY_RUN and APPLY behavior are proven.
- Secrets and credentials must be excluded and must not be logged.

## Next Approved Sequence

1. Commit this specification after review.
2. Create a future DRY_RUN-only backup preview helper.
3. Validate that the helper prints paths, exclusions, and planned commands without mutation.
4. Run a separate APPLY lane only after operator approval.
5. Consider Task Scheduler only after the manual APPLY path is reliable.

