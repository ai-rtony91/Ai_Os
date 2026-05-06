# AI_OS Workflow Router Runbook Draft

## Purpose

This runbook explains how the operator uses `Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` to run approved DRY_RUN workflow checks. The router is a safe command layer that maps workflow names to existing DRY_RUN helper scripts.

## Safety Position

The router is evidence-only. It does not approve APPLY, does not edit files, does not launch apps, does not open browsers, does not change startup settings, does not touch trading or broker systems, and does not run git checkpoint commands.

Router output is evidence only unless later saved by an approved reporting helper.

## Active Repo Requirement

All commands in this runbook must be run from:

```powershell
C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN
```

Stop if PowerShell is not in that folder.

## Router Script Path

The router script path is:

```text
automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1
```

## Allowed Initial Workflows

Allowed initial workflow names are:

- `REPO_HEALTH`
- `DAILY_START`
- `WORK_SESSION`
- `CHECKPOINT_ONLY`
- `DAILY_METRICS_DRAFT`
- `FULL_DRY_RUN_CHAIN`

`BAD_TEST_MODE` is not an allowed workflow. It is used only to verify that the router fails safely.

## Command Examples

Run repo health:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName REPO_HEALTH
```

Start daily work:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName DAILY_START
```

Log work session:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName WORK_SESSION
```

Draft checkpoint:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName CHECKPOINT_ONLY
```

Draft daily metrics:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName DAILY_METRICS_DRAFT
```

Run full dry chain:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName FULL_DRY_RUN_CHAIN
```

Run bad mode safety test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1" -WorkflowName BAD_TEST_MODE
```

## Expected Output

Router output should show:

- Task name.
- Router mode.
- Repo root.
- Selected workflow.
- Allowed actions.
- Blocked actions.
- Approval requirement.
- Helper scripts that would be used.
- Helper scripts found or missing.
- Final PASS/WARN/FAIL summary.

## PASS/WARN/FAIL Meaning

PASS means the router recognized the workflow, found the expected DRY_RUN helpers, and no unsafe action was attempted.

WARN means the router or helper found something that needs review, such as an uncommitted working tree or a missing helper that did not block the whole run.

FAIL means the workflow name is unknown, the repo root is missing, or another blocking condition was detected.

## What To Do After PASS

Review the output. If the output matches the expected workflow and no protected paths changed, the next safe action is a human decision: continue with another DRY_RUN, approve a scoped APPLY work-order, or approve a separate git checkpoint.

## What To Do After WARN

Read the warning text. Do not continue into APPLY until the warning is understood. If git status shows unexpected changes, stop and review before continuing.

## What To Do After FAIL

Stop. Read the failure message. Use the valid workflow list if the workflow name was wrong. Do not work around the failure by running unknown scripts.

## What Not To Do

Do not use the router to launch apps, open browsers, change startup settings, create scheduled tasks, edit protected files, write reports, edit `Reports\DAILY_METRICS.csv`, update `Reports\CHECKPOINT_INDEX.md`, handle credentials, touch broker systems, place trades, or enable live trading.

## Human Approval Gate

The router does not approve APPLY. Human approval is required before any APPLY work, report writing, protected file edit, settings change, app launch, browser open, or trading/broker action.

## Git Checkpoint Rule

`git add`, `git commit`, and `git push` remain separate human-approved actions. Do not run them as part of the router workflow.

## Future Expansion Rule

Future workflows must be proposed in a DRY_RUN plan first. A new workflow should list its helper mapping, allowed actions, blocked actions, approval gates, and risk level before it is added to the router.
