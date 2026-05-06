# AI_OS Operator Command Map Draft

## Purpose

This draft provides beginner-safe operator command labels for the AI_OS workflow router and helper scripts.

## Operator Vocabulary

An operator phrase is a plain-language command the human can say or type.

A router workflow is the approved workflow name passed to the DRY_RUN router.

A helper script is the underlying DRY_RUN script used by the workflow.

## Safe Command Families

Safe command families are read-only DRY_RUN console-output commands. They report observed state and do not write files.

## Router Commands

| Operator phrase | Router workflow | Script path | Risk level | Requires approval? |
|---|---|---|---|---|
| check repo health | `REPO_HEALTH` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |
| start daily work | `DAILY_START` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |
| log work session | `WORK_SESSION` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |
| draft checkpoint | `CHECKPOINT_ONLY` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |
| draft daily metrics | `DAILY_METRICS_DRAFT` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |
| run full dry chain | `FULL_DRY_RUN_CHAIN` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |
| bad mode safety test | `BAD_TEST_MODE` | `automation\router\Invoke-AiOsWorkflowRouter.DRY_RUN.ps1` | LOW | No for DRY_RUN |

## Direct Helper Commands

Direct helper commands may be used when the operator needs to test one helper without the router:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`
- `automation\modes\Test-AiOsModeSelection.DRY_RUN.ps1`
- `automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1`
- `automation\checkpoints\New-AiOsCheckpointDraft.DRY_RUN.ps1`
- `automation\reporting\New-AiOsDailyMetricsRow.DRY_RUN.ps1`
- `automation\orchestration\Test-AiOsOperationalChain.DRY_RUN.ps1`

## Git Checkpoint Commands

Git checkpoint commands are not part of the router. `git add`, `git commit`, and `git push` require separate human approval.

## Blocked Command Families

HIGH risk command families are blocked until explicit separate approval.

Risk levels:

- LOW = read-only DRY_RUN console-output.
- MEDIUM = creates approved files but no git commit.
- HIGH = moves, deletes, overwrites, launches, changes settings, touches credentials, or touches trading systems.

Trading, broker, and live execution commands are not part of this operator map yet.

## When To Use Codex

Use Codex for scoped repo work, DRY_RUN planning, documentation drafts, helper-script creation, and safe verification summaries.

Stop and require a separate approval before asking Codex to create files, edit files, stage, commit, push, launch apps, open browsers, or touch protected areas.

## When To Use PowerShell

Use PowerShell to run approved DRY_RUN commands from the active repo path:

```powershell
C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN
```

Use PowerShell output as evidence for the next decision.

## When To Stop And Ask For Review

Stop and ask for review when:

- Git status shows unexpected files.
- A router command returns FAIL.
- A helper returns WARN that is not understood.
- A command would write files.
- A command would touch protected files.
- A command would launch apps, open browsers, change settings, handle credentials, or touch trading/broker systems.

## Future Dashboard Mapping

Future dashboard buttons should map to workflow names instead of raw scripts. This keeps the dashboard aligned with the router approval model and avoids exposing unsafe direct commands.
