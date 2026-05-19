# docs/AI_OS Reference Retirement Pass 13

Date: 2026-05-19
Branch: phase-82-copy-paste-reduction-runner
Mode: APPLY within scoped automation reference retirement

## Purpose

Retire active automation dependencies on generated legacy `docs/AI_OS` folders so a later archive pass can move the remaining generated folders safely.

Legacy folders in scope:

- `docs/AI_OS/checkpoints`
- `docs/AI_OS/progress`
- `docs/AI_OS/backfill`
- `docs/AI_OS/morning_brief`

No source files under `docs/AI_OS` were edited, moved, or deleted.

## Files Inspected

- `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `automation/status/Test-AiOsDocumentationConsolidation.DRY_RUN.ps1`
- `automation/status/Test-AiOsPhase12IntegrationAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsProductionReadinessReview.DRY_RUN.ps1`
- `automation/status/Test-AiOsRepoGapAuditBackfillPlan.DRY_RUN.ps1`
- `automation/status/Test-AiOsStage7To12MasterValidation.DRY_RUN.ps1`
- `automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1`
- `automation/status/Test-AiOsWriterPromotionPlanning.DRY_RUN.ps1`
- `automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json`

## Files Changed

- `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `automation/status/Test-AiOsDocumentationConsolidation.DRY_RUN.ps1`
- `automation/status/Test-AiOsPhase12IntegrationAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsProductionReadinessReview.DRY_RUN.ps1`
- `automation/status/Test-AiOsRepoGapAuditBackfillPlan.DRY_RUN.ps1`
- `automation/status/Test-AiOsStage7To12MasterValidation.DRY_RUN.ps1`
- `automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1`
- `automation/status/Test-AiOsWriterPromotionPlanning.DRY_RUN.ps1`
- `automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json`
- `docs/audits/docs-aios-reference-retirement-pass-13.md`

## Exact References Retired

| Legacy reference | Replacement |
| --- | --- |
| `docs/AI_OS/checkpoints/AIOS_STAGE80_DASHBOARD_PREVIEW_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md` | `docs/concepts/aios-dashboard-and-interface-concepts.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE59_DOCUMENTATION_CONSOLIDATION_CHECKPOINT_DRAFT.md` | `docs/architecture/aios-system-architecture.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE60_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md` | `docs/workflows/aios-operator-workflows.md` |
| `docs/AI_OS/progress` in Phase 12 integration audit | `docs/roadmap/aios-product-roadmap.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE99_FINAL_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md` | `docs/governance/aios-governance-model.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE100_FINAL_APPROVAL_GATE_REVIEW_DRAFT.md` | `docs/infrastructure/aios-runtime-infrastructure.md` |
| `docs/AI_OS/backfill/AIOS_STAGE104_CONTROLLED_BACKFILL_PLAN_DRAFT.md` | `docs/audits/docs-aios-promotion-archive-plan-pass-10.md` |
| `docs/AI_OS/backfill/AIOS_STAGE105_SOURCE_EVIDENCE_REQUIREMENTS_DRAFT.md` | `docs/audits/docs-aios-promotion-archive-plan-pass-10.md` |
| `docs/AI_OS/backfill/AIOS_STAGE106_FOLDER_FILE_POPULATION_MATRIX_DRAFT.md` | `docs/audits/docs-aios-promotion-archive-plan-pass-10.md` |
| `docs/AI_OS/backfill/AIOS_STAGE107_PROTECTED_ROOT_BACKFILL_EXCLUSION_DRAFT.md` | `docs/audits/docs-aios-canonical-summary-pass-11.md` |
| `docs/AI_OS/backfill/AIOS_STAGE108_BACKFILL_VALIDATOR_PLAN_DRAFT.md` | `docs/audits/docs-aios-canonical-summary-pass-11.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE109_BACKFILL_READINESS_CHECKPOINT_DRAFT.md` | `docs/audits/docs-aios-canonical-summary-pass-11.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE110_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md` | `docs/audits/docs-aios-canonical-summary-pass-11.md` |
| `docs/AI_OS/progress` in Stage 7-12 master validation | `docs/roadmap/aios-product-roadmap.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE89_TELEMETRY_REPORTING_PERSISTENCE_CHECKPOINT_DRAFT.md` | `docs/infrastructure/aios-runtime-infrastructure.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE90_PERSISTENCE_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md` | `docs/infrastructure/aios-runtime-infrastructure.md` |
| `docs/AI_OS/checkpoints/AIOS_STAGE70_WRITER_PROMOTION_HUMAN_APPROVAL_CHECKPOINT_DRAFT.md` | `docs/workflows/aios-operator-workflows.md` |
| `docs/AI_OS/checkpoints` in work intelligence config | `docs/audits` |

Approved-prefix lists were updated in the affected validators so the compact canonical docs are allowed paths. Canonical summary files are checked for existence only; the older stage-specific phrase scans remain limited to the historical draft files that still exist under active `docs/AI_OS` topic folders.

## References Kept

No references to the four scoped legacy folders remain in `automation` or `scripts` after the Pass 13 scan.

References to other `docs/AI_OS` topic folders remain intentionally out of scope, including dashboard, governance, security, source_control, runbooks, telemetry, reporting, writers, operator, and other active/human-review folders.

## Archive Safety Assessment

- `docs/AI_OS/checkpoints`: archive-safe from the automation/scripts dependency perspective after Pass 13.
- `docs/AI_OS/progress`: archive-safe from the automation/scripts dependency perspective after Pass 13.
- `docs/AI_OS/backfill`: archive-safe from the automation/scripts dependency perspective after Pass 13.
- `docs/AI_OS/morning_brief`: archive-safe from the automation/scripts dependency perspective after Pass 13 because no current automation/scripts references remain in the validation scan.

Before Pass 14 moves folders, run a final full-repo reference scan to catch historical docs references and decide whether they are acceptable audit-only references.

## Validation Commands

Required validation commands for this pass:

```powershell
git status --short
git diff --stat
git diff --name-status
git diff --check
$files = @(
  "automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1",
  "automation/status/Test-AiOsDocumentationConsolidation.DRY_RUN.ps1",
  "automation/status/Test-AiOsPhase12IntegrationAudit.DRY_RUN.ps1",
  "automation/status/Test-AiOsProductionReadinessReview.DRY_RUN.ps1",
  "automation/status/Test-AiOsRepoGapAuditBackfillPlan.DRY_RUN.ps1",
  "automation/status/Test-AiOsStage7To12MasterValidation.DRY_RUN.ps1",
  "automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1",
  "automation/status/Test-AiOsWriterPromotionPlanning.DRY_RUN.ps1"
)
foreach ($file in $files) {
  $tokens = $null
  $errors = $null
  [System.Management.Automation.Language.Parser]::ParseFile($file, [ref]$tokens, [ref]$errors) | Out-Null
  if ($errors.Count -gt 0) { $errors }
}
Get-Content -Raw automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json | ConvertFrom-Json | Out-Null
Get-ChildItem automation,scripts -Recurse -File | Select-String -Pattern 'docs/AI_OS/checkpoints|docs/AI_OS/progress|docs/AI_OS/backfill|docs/AI_OS/morning_brief'
git status --short
```

## Validation Results

- `git diff --check`: PASS. Only line-ending warnings were reported by Git for existing working-copy normalization behavior.
- PowerShell parser check: PASS for all eight changed `.ps1` files.
- JSON parse check: PASS for `automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json`.
- Legacy path scan across `automation` and `scripts`: PASS, no matches for `docs/AI_OS/checkpoints`, `docs/AI_OS/progress`, `docs/AI_OS/backfill`, or `docs/AI_OS/morning_brief`.
- Scope check: PASS, all changed files are in the allowed file list.
- `docs/AI_OS` change check: PASS, no files under `docs/AI_OS` changed.
- Commit status: no commit created.
- Push status: no push performed.

## Risks

- These validators still depend on many historical `docs/AI_OS` topic draft files that were not in scope for Pass 13.
- `Reports/*` references remain in the validators and may need a separate cleanup pass because `Reports` was archived earlier.
- The compact canonical docs are summaries, not full replacements for every historical stage draft.
- Pass 14 should still use `git mv` only and should not delete generated folders.

## Recommended Pass 14

Move the four now-unblocked generated legacy folders to `archive/docs_aios_legacy/` after one final reference scan:

- `docs/AI_OS/checkpoints`
- `docs/AI_OS/progress`
- `docs/AI_OS/backfill`
- `docs/AI_OS/morning_brief`

Keep dashboard, dispatcher, orchestration, operator, governance, security, architecture, source_control, runbooks, product, and productization out of Pass 14 unless MAIN CONTROL explicitly expands scope.
