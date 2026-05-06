# AI_OS Stage 9 Operational Scaffold Plan

## Purpose

Stage 9 converts documented AI_OS architecture into reusable operational tooling. The goal is to make repo checks, evidence logging, checkpoints, daily metrics, and future launcher planning repeatable without removing human approval gates.

Executable automation remains DRY_RUN unless explicitly approved in a separate APPLY work-order.

## Scope

Stage 9 covers small, portioned work-orders for:

- Reusable reporting framework support.
- Repo health verification chain.
- Session and evidence logging drafts.
- Daily metrics writer groundwork.
- Checkpoint generator groundwork.
- Future Morning Brief and Morning Launch support.
- Launcher and mode system groundwork.

## Non-Scope

Stage 9 does not approve:

- Live trading.
- Broker orders.
- Broker API integration.
- Credential, token, key, or secret handling.
- Registry, firewall, VPN, BIOS/UEFI, BitLocker, browser policy, startup setting, or Task Scheduler changes.
- App launch automation.
- Browser launch automation.
- Startup automation.
- File deletion, movement, rename, or cleanup.

Launcher, startup, trading, and broker actions are not approved.

## Current Known Assets

Current known automation and reporting assets include:

- `automation\reporting\New-AiOsReport.ps1`
- `automation\reporting\Test-AiOsRepoCleanStatus.DRY_RUN.ps1`
- `automation\reporting\Test-AiOsFolderPurposeCoverage.DRY_RUN.ps1`
- `automation\reporting\Test-AiOsFinalCleanStop.DRY_RUN.ps1`
- `automation\startup\Start-AiOsMorningWorkflow.ps1`
- `Reports\DAILY_METRICS.csv`
- `Reports\CHECKPOINT_INDEX.md`
- `Reports\checkpoints`
- `Reports\daily`

Existing report and checkpoint files are historical evidence and should not be rewritten or migrated without separate approval.

## Stage 9B Docs Layer

Stage 9B creates documentation that defines the operational scaffold before more scripts are added. This layer explains the repo health chain, approval gates, protected paths, and safe next actions.

## Stage 9C Repo Health Chain

Stage 9C adds a DRY_RUN-only repo health helper. The helper should verify the active repo path, git branch/upstream state, protected files, top-level folders, Reports folders, Stage helper scripts, and unsafe-action warnings.

The Stage 9C helper must remain read-only and must not run `git add`, `git commit`, or `git push`.

## Stage 9D Session Evidence Layer

Stage 9D should define a DRY_RUN-only session and evidence logging layer. It may print proposed session or evidence rows, but it must not create recordings, screenshots, telemetry migrations, or report artifacts without later approval.

## Stage 9E Daily Metrics Writer

Stage 9E should define a careful daily metrics writer plan. Existing `Reports\DAILY_METRICS.csv` must not be rewritten or migrated unless a separate work-order approves the exact behavior and backup/checkpoint plan.

## Stage 9F Mode Launcher Groundwork

Stage 9F should define launcher and mode groundwork as text-first planning. Any future Work Mode, Return to Work Mode, Retire/Shutdown Mode, Morning Brief, or Morning Launch helper must keep app launch, browser launch, startup changes, broker actions, and trading execution blocked unless separately approved.

## Approval Gates

Each Stage 9 work-order must:

1. Start with a scoped DRY_RUN or inspection step.
2. Name the exact files and folders involved.
3. Avoid protected files unless separately approved.
4. Avoid destructive actions.
5. Produce a beginner-readable report.
6. Stop before staging, committing, pushing, launching apps, changing settings, or touching trading systems.

## Protected Paths

Protected root files include:

- `README.md`
- `AGENTS.md`
- `RISK_POLICY.md`
- `SOURCE_LOG.md`
- `ERROR_LOG.md`
- `HALLUCINATION_LOG.md`
- `AAR.md`
- `DAILY_REPORT.md`
- `WHITEPAPER.md`

Protected evidence/report paths include:

- `Reports\DAILY_METRICS.csv`
- `Reports\CHECKPOINT_INDEX.md`
- `Reports\checkpoints`
- `Reports\daily`
- `internal\source-artifacts`

These paths must not be edited, overwritten, moved, renamed, deleted, staged, committed, or pushed without separate approval and a backup/checkpoint plan.

## Human Verification Checkpoint

After each Stage 9 batch, the human should verify:

- Git status shows only expected files.
- New files are in the approved paths.
- No protected root files changed.
- No unsafe actions were attempted.
- The next action is either another DRY_RUN, an approved APPLY batch, or an explicit human git checkpoint.
