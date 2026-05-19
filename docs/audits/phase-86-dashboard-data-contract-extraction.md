# Phase 86 Dashboard Data-Contract Extraction

Date: 2026-05-19
Branch: `phase-83-docs-aios-dashboard-dispatcher-triage`
Mode: scoped extraction and reference retirement

## Purpose

Extract dashboard data-contract ideas from legacy `docs/AI_OS/dashboard` drafts into a canonical spec and retire active references to the blocking dashboard contract draft files.

No files under `docs/AI_OS/dashboard` were edited, moved, deleted, or renamed.

## Source Files Inspected

- `docs/AI_OS/dashboard/AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_DASHBOARD_FIXTURE_DATA_RULES_DRAFT.md`
- `docs/AI_OS/dashboard`
- `docs/concepts/aios-dashboard-and-interface-concepts.md`
- `docs/roadmap/aios-product-roadmap.md`
- `docs/audits/phase-85-dashboard-archive-readiness.md`

Allowed active reference areas inspected:

- `automation/status/*.DRY_RUN.ps1`
- `automation/startup/*.DRY_RUN.ps1`
- `apps/dashboard/mock-data/app-registry.example.json`

## Canonical Spec Created

Created:

- `docs/specs/aios-dashboard-data-contracts.md`

The spec extracts:

- dashboard state model,
- fixture/mock-data contract,
- status card contract,
- validator health contract,
- checkpoint and next action contract,
- command center / operator panel contract,
- telemetry panel contract,
- AI assistant panel contract as concept-only,
- static preview contract,
- responsive/mobile behavior contract,
- visual/layout guidance,
- safety boundaries and human-review items.

The spec explicitly keeps live broker, OANDA, real webhook, live AI, secrets, credential access, and live trading actions out of scope.

## References Retired

Retired exact active references to:

- `docs/AI_OS/dashboard/AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md`
- `docs/AI_OS/dashboard/AIOS_DASHBOARD_FIXTURE_DATA_RULES_DRAFT.md`

Replacement:

- `docs/specs/aios-dashboard-data-contracts.md`

Files updated:

- `automation/startup/Get-AiOsMorningBriefState.DRY_RUN.ps1`
- `automation/status/Get-AiOsApprovalState.DRY_RUN.ps1`
- `automation/status/Get-AiOsDashboardSnapshot.DRY_RUN.ps1`
- `automation/status/Test-AiOsApprovalQueueValidator.DRY_RUN.ps1`
- `automation/status/Test-AiOsDashboardImplementationSelection.DRY_RUN.ps1`
- `automation/status/Test-AiOsDashboardPrototypeMegabatch.DRY_RUN.ps1`
- `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `automation/status/Test-AiOsFullReadinessAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsOperatorManualArchitecture.DRY_RUN.ps1`
- `automation/status/Test-AiOsRenderingStackEvaluation.DRY_RUN.ps1`
- `automation/status/Test-AiOsStaticDashboardMockContract.DRY_RUN.ps1`
- `automation/status/Test-AiOsStaticDashboardPrototypeArchitecture.DRY_RUN.ps1`
- `automation/status/Test-AiOsVisualDashboardRenderPrep.DRY_RUN.ps1`
- `apps/dashboard/mock-data/app-registry.example.json`

The app registry metadata now points at the canonical dashboard data-contract spec instead of a legacy dashboard planning packet path. No app runtime code was changed.

## References Remaining

Exact references to the three blocker contract draft filenames no longer appear in the active app/automation/script/service/schema/test/.github scan.

Remaining broader references to `docs/AI_OS/dashboard` still exist in active validators:

- `automation/status/Test-AiOsDashboardCommandCenterReadiness.DRY_RUN.ps1`
- `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `automation/status/Test-AiOsPhase12IntegrationAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsStage7To12MasterValidation.DRY_RUN.ps1`

These references are not the three Phase 86 contract blockers, but they still prevent whole-folder archive of `docs/AI_OS/dashboard`.

## Dashboard Archive Readiness After Phase 86

Decision: **PARTIAL IMPROVEMENT, NOT WHOLE-FOLDER ARCHIVE READY**

Why:

- the specific data-contract blockers were retired,
- a canonical dashboard data-contract spec now exists,
- app metadata no longer points at a legacy dashboard planning packet,
- but active validators still reference other `docs/AI_OS/dashboard` files and folder paths.

## Recommended Phase 87

Recommended next pass:

`AI_OS PHASE 87 - DASHBOARD REMAINING REFERENCE RETIREMENT`

Goal:

- inspect remaining active validator references to `docs/AI_OS/dashboard`,
- replace exact required references with canonical concept/spec docs where safe,
- make historical stage references optional or non-blocking,
- do not move or delete dashboard source files yet.

Potential canonical replacements:

- `docs/concepts/aios-dashboard-and-interface-concepts.md`
- `docs/specs/aios-dashboard-data-contracts.md`
- `docs/roadmap/aios-product-roadmap.md`

## Risks

- Some validators still represent historical stage checks and may intentionally require legacy planning files.
- Repointing all dashboard references blindly could weaken stage-specific validation.
- `docs/specs/aios-dashboard-data-contracts.md` is a summary spec, not proof of implementation.
- `apps/dashboard` runtime behavior was not modified or tested.
- Future archive moves still require a final full-reference scan.

## Validation Results

Validation commands run:

```powershell
git status --short -uall
git diff --stat
git diff --name-status
git diff --check
```

Additional required checks:

- PowerShell parser check for changed `.ps1` files.
- JSON parse check for `apps/dashboard/mock-data/app-registry.example.json`.
- Search active areas for:
  - `AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md`
  - `AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md`
  - `AIOS_DASHBOARD_FIXTURE_DATA_RULES_DRAFT.md`
  - `docs/AI_OS/dashboard`
- Confirm no `docs/AI_OS` files changed.
- Confirm no unauthorized files changed.

Observed results:

- `git diff --check`: PASS. Only Git line-ending normalization warnings were reported.
- PowerShell parser check: PASS for all changed `.ps1` files.
- JSON parse check: PASS for `apps/dashboard/mock-data/app-registry.example.json`.
- Exact blocker scan: PASS for the three retired blocker filenames in active app/automation/script/service/schema/test/.github paths.
- Broader `docs/AI_OS/dashboard` scan: still reports remaining active validator references listed above.
- `docs/AI_OS` change check: PASS, no files under `docs/AI_OS` changed.
- Scope check: PASS, only allowed files changed.
- Commit status: no commit created.
- Push status: no push performed.
