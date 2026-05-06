# AI_OS Workflow Router Draft

## Purpose

The AI_OS workflow router is the control layer that maps named work modes to approved DRY_RUN helper chains. It gives the operator one safe entry point for checking what would run before any APPLY work is considered.

This is not autonomous execution.

## Current Stage

Stage 10B creates the first DRY_RUN-only controlled workflow router. The router selects a named workflow, prints the mapped helper chain, verifies helper availability, and may call existing DRY_RUN helper scripts.

## Router Scope

The router may:

- Accept a workflow name.
- Confirm the active repo root.
- Print allowed actions and blocked actions.
- List helper scripts mapped to the workflow.
- Check whether helpers are present or missing.
- Call existing helper scripts only when their path contains `.DRY_RUN.`.

## Router Non-Scope

The router does not approve APPLY.

The router does not launch apps.

The router does not open browsers.

The router does not modify startup tasks or startup settings.

The router does not touch trading or broker systems.

The router does not edit `Reports\DAILY_METRICS.csv`.

The router does not update `Reports\CHECKPOINT_INDEX.md`.

The router does not run `git add`, `git commit`, or `git push`.

## Approved Initial Workflows

Initial workflow names are:

- `REPO_HEALTH`
- `DAILY_START`
- `WORK_SESSION`
- `CHECKPOINT_ONLY`
- `DAILY_METRICS_DRAFT`
- `FULL_DRY_RUN_CHAIN`

Unknown workflow names must fail safely and print the valid workflow list.

## Helper Mapping

`REPO_HEALTH` maps to:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`

`DAILY_START` maps to:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`
- `automation\modes\Test-AiOsModeSelection.DRY_RUN.ps1 -ModeName WORK_MODE`
- `automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1`

`WORK_SESSION` maps to:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`
- `automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1`

`CHECKPOINT_ONLY` maps to:

- `automation\checkpoints\New-AiOsCheckpointDraft.DRY_RUN.ps1`

`DAILY_METRICS_DRAFT` maps to:

- `automation\reporting\New-AiOsDailyMetricsRow.DRY_RUN.ps1`

`FULL_DRY_RUN_CHAIN` maps to:

- `automation\orchestration\Test-AiOsOperationalChain.DRY_RUN.ps1`

## Safety Rules

The router must remain DRY_RUN-only and console-output-only. It must not create, edit, move, rename, delete, stage, commit, push, launch apps, open browsers, change settings, create scheduled tasks, touch credentials, touch secrets, touch broker systems, place trades, or enable live trading.

The router may call only helper scripts whose paths contain `.DRY_RUN.`. Any non-DRY_RUN helper path must be blocked.

Missing helpers should produce WARN output, not a crash.

## Approval Gates

Human approval is required before any APPLY, `git add`, `git commit`, or `git push`.

Human approval is also required before any report write, protected file edit, startup change, launcher action, browser open, app launch, broker action, trading action, credential handling, or security setting change.

## Future Stage 10C

Future Stage 10C may add a written router runbook, more workflow names, and clearer operator prompts. It should remain DRY_RUN-first and must not become autonomous execution.
