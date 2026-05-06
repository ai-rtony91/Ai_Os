# AI_OS Automation Helper Dry Run Requirements Draft

## Purpose

This draft defines requirements for future dry-run-only helper scripts only. It does not approve helper script creation.

## Required Helper Behavior

Future helper scripts must:

- Default to DRY_RUN.
- Print the repo root being evaluated.
- Print `git status --short --branch` when repo state matters.
- Avoid editing existing files unless a later APPLY mode is separately approved.
- Avoid overwrite, move, rename, delete, cleanup, staging, commit, and push.
- Stop on target-path collisions.
- Report files inspected, files that would be created, files that would be changed, errors, unknowns, and next safe action.
- Label unverifiable facts as UNKNOWN.
- Label conflicts with verified evidence as MISMATCH or INVALID DATA.
- Avoid reading or printing secrets, credentials, broker tokens, private keys, recovery keys, or personal data.
- Avoid opening external apps, recording screens, taking screenshots, or changing startup tasks.

## Required Output

Each future dry-run helper should end with:

- Task.
- Files inspected.
- Files created.
- Files changed.
- Dry-run result.
- Errors.
- Unknowns.
- Protected action involved.
- Approval required.
- Next safe action.

## Blocked Until Separate Approval

- Editing `automation\reporting\New-AiOsReport.ps1`.
- Editing `automation\startup\Start-AiOsMorningWorkflow.ps1`.
- Editing `Reports\DAILY_METRICS.csv`.
- Editing `Reports\TELEMETRY_SESSION_TEMPLATE_DRAFT.csv`.
- Creating startup tasks.
- Implementing screen recording or screenshot capture.
- Implementing telemetry automation.
- Implementing duplicate cleanup or archive migration.
- Implementing broker/trading automation.
- Implementing secret/key handling automation.
