# AI_OS Workflow Registry Draft

## Purpose

This registry documents approved DRY_RUN workflow names, mapped helper scripts, risk level, and approval rules for the AI_OS workflow router.

## Registry Rules

The registry is documentation-first. It does not approve APPLY work, app launch, browser opening, startup changes, report writing, broker actions, trading actions, credential handling, or git checkpoint commands.

Router and dashboard workflows must use registered workflow names. Future dashboard buttons must map to workflow names, not raw scripts.

## Approved Workflows

| Workflow name | Operator phrase | Risk level | Mode | Writes files | Requires git checkpoint | Requires human review |
|---|---|---|---|---|---|---|
| `REPO_HEALTH` | check repo health | LOW | DRY_RUN | NO | NO | YES |
| `DAILY_START` | start daily work | LOW | DRY_RUN | NO | NO | YES |
| `WORK_SESSION` | log work session | LOW | DRY_RUN | NO | NO | YES |
| `CHECKPOINT_ONLY` | draft checkpoint | LOW | DRY_RUN | NO | NO | YES |
| `DAILY_METRICS_DRAFT` | draft daily metrics | LOW | DRY_RUN | NO | NO | YES |
| `FULL_DRY_RUN_CHAIN` | run full dry chain | LOW | DRY_RUN | NO | NO | YES |

## Helper Mapping

`REPO_HEALTH` uses:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`

`DAILY_START` uses:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`
- `automation\modes\Test-AiOsModeSelection.DRY_RUN.ps1 -ModeName WORK_MODE`
- `automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1`

`WORK_SESSION` uses:

- `automation\health\Test-AiOsRepoHealthChain.DRY_RUN.ps1`
- `automation\sessions\New-AiOsSessionEvidenceLog.DRY_RUN.ps1`

`CHECKPOINT_ONLY` uses:

- `automation\checkpoints\New-AiOsCheckpointDraft.DRY_RUN.ps1`

`DAILY_METRICS_DRAFT` uses:

- `automation\reporting\New-AiOsDailyMetricsRow.DRY_RUN.ps1`

`FULL_DRY_RUN_CHAIN` uses:

- `automation\orchestration\Test-AiOsOperationalChain.DRY_RUN.ps1`

## Risk Levels

LOW means read-only DRY_RUN console-output.

MEDIUM means creates approved files but no git commit.

HIGH means moves, deletes, overwrites, launches, changes settings, touches credentials, or touches trading systems.

The approved workflows in this registry are LOW risk only.

Required registry safety fields:

- risk level LOW
- DRY_RUN
- writes files NO
- requires human review YES

## Approval Requirements

Each registered workflow requires human review before the output is used for any follow-up action.

Any APPLY, report write, protected file edit, git add, git commit, git push, app launch, browser open, startup change, settings change, credential handling, broker action, or trading action requires separate explicit human approval.

## Blocked Workflow Types

No broker, trading, or live execution workflows are approved.

Blocked workflow types include:

- Broker order placement.
- Live trading.
- Credential, secret, token, private key, or recovery key handling.
- App launch.
- Browser opening.
- Startup settings changes.
- Scheduled task creation.
- Registry, firewall, VPN, BIOS/UEFI, BitLocker, or browser policy changes.
- File deletion, movement, rename, overwrite, reset, or cleanup.

## Future Dashboard Use

Future dashboard buttons must map to registered workflow names, not raw scripts. A dashboard should show the workflow name, risk level, mode, approval requirement, and blocked actions before a human runs anything.

## Future Stage 11

Future Stage 11 may propose dashboard-facing workflow selection, richer registry validation, or a text-only workflow status report. It must remain DRY_RUN-first and must not enable autonomous execution.
