# docs/AI_OS Archive Pass 12

Date: 2026-05-19
Branch: phase-82-copy-paste-reduction-runner
Mode: APPLY, archive move only

## Purpose

Archive the first obvious generated or historical `docs/AI_OS` folder batch after Pass 11 created compact canonical summaries. This pass did not delete files and did not edit source docs under `docs/AI_OS`.

## Folders Inspected

| Folder | Exists | Tracked file count | Classification |
| --- | --- | ---: | --- |
| `docs/AI_OS/checkpoints` | YES | 11 | KEEP FOR NOW |
| `docs/AI_OS/progress` | YES | 9 | KEEP FOR NOW |
| `docs/AI_OS/backfill` | YES | 6 | KEEP FOR NOW |
| `docs/AI_OS/morning_brief` | YES | 5 | KEEP FOR NOW |
| `docs/AI_OS/roadmaps` | YES | 4 | ARCHIVE SAFE |

## Reference Scan Results

### `docs/AI_OS/checkpoints`

Active references found in automation:

- `automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json`
- `automation/status/Test-AiOsDocumentationConsolidation.DRY_RUN.ps1`
- `automation/status/Test-AiOsWriterPromotionPlanning.DRY_RUN.ps1`
- `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1`
- `automation/status/Test-AiOsRepoGapAuditBackfillPlan.DRY_RUN.ps1`
- `automation/status/Test-AiOsProductionReadinessReview.DRY_RUN.ps1`

Decision: KEEP FOR NOW. Although the folder looks stage/checkpoint-generated, active automation still requires exact paths.

### `docs/AI_OS/progress`

Active references found in automation:

- `automation/progress/Test-AiOsProgressLedgerAutomationReadiness.DRY_RUN.ps1`
- `automation/progress/Test-AiOsProgressLedgerReadiness.DRY_RUN.ps1`
- `automation/status/Test-AiOsPhase12IntegrationAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsStage7To12MasterValidation.DRY_RUN.ps1`

Decision: KEEP FOR NOW. This folder includes progress source-of-truth docs still used by validators.

### `docs/AI_OS/backfill`

Active references found in automation:

- `automation/status/Test-AiOsRepoGapAuditBackfillPlan.DRY_RUN.ps1`

Decision: KEEP FOR NOW. The folder is generated/planning style but still directly validated by an active automation script.

### `docs/AI_OS/morning_brief`

Active references found in automation:

- `automation/startup/Test-AiOsMorningBriefTextContract.DRY_RUN.ps1`
- `automation/status/Test-AiOsFullReadinessAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsOperatorTelemetryMap.DRY_RUN.ps1`
- `automation/status/Test-AiOsMorningBriefPreviewGenerator.DRY_RUN.ps1`
- `automation/status/Test-AiOsSafeFilePopulationWorkflow.DRY_RUN.ps1`

Decision: KEEP FOR NOW. The folder is planning style but active automation still validates exact contract files.

### `docs/AI_OS/roadmaps`

References found only in docs/audit planning context:

- Pass 9 classification report
- Pass 10 promotion/archive plan
- Pass 11 canonical summary report

Decision: ARCHIVE SAFE. High-level roadmap ideas were preserved in `docs/roadmap/aios-product-roadmap.md`; no active automation/code references require this folder path.

## Folders Moved

- `docs/AI_OS/roadmaps/` -> `archive/docs_aios_legacy/roadmaps/`

Moved files:

- `AIOS_AUTONOMY_BOUNDARY_MATRIX_DRAFT.md`
- `AIOS_COMMERCIALIZATION_READINESS_DRAFT.md`
- `AIOS_MASTER_EXECUTION_ROADMAP_DRAFT.md`
- `AIOS_PHASE_DEPENDENCY_GRAPH_DRAFT.md`

## Folders Kept

- `docs/AI_OS/checkpoints/`
- `docs/AI_OS/progress/`
- `docs/AI_OS/backfill/`
- `docs/AI_OS/morning_brief/`

## Remaining docs/AI_OS Size Estimate

Before this pass, `docs/AI_OS` had 770 tracked files. This pass moved 4 tracked files out of `docs/AI_OS`, so the estimated remaining tracked count is 766.

## Risks

- The kept folders are still clutter, but moving them now would break active automation path checks.
- The active automation scripts may themselves be historical. That should be reviewed in a later automation cleanup pass before moving the folders.
- Docs and audits still mention the old `docs/AI_OS/roadmaps` path as historical context.

## Recommended Next Cleanup Pass

Before the next docs archive batch, update or retire active validators that require exact legacy docs paths:

- checkpoint validators under `automation/status/`
- progress validators under `automation/progress/`
- backfill validator under `automation/status/`
- morning brief validators under `automation/startup/` and `automation/status/`

Recommended title:

`AI_OS DOCS PASS 13 - CLEAR AUTOMATION REFERENCES TO GENERATED docs/AI_OS FOLDERS`

## Validation Commands

```powershell
git status --short
git diff --stat
git diff --name-status
git diff --check
rg -n "docs/AI_OS/checkpoints|docs/AI_OS/progress|docs/AI_OS/backfill|docs/AI_OS/morning_brief|docs/AI_OS/roadmaps" docs automation scripts apps services aios schemas tests .github
```
