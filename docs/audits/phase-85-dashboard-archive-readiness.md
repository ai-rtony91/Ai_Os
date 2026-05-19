# Phase 85 Dashboard Archive Readiness

Date: 2026-05-19
Branch: `phase-83-docs-aios-dashboard-dispatcher-triage`
Mode: report-only readiness scan

## Purpose

Determine whether `docs/AI_OS/dashboard` can be archived safely, partially archived, or needs another extraction pass.

No files were moved, deleted, renamed, or edited under `docs/AI_OS/dashboard`, `apps/dashboard`, `automation`, `scripts`, `services`, `schemas`, `tests`, `.github`, or `archive`.

## Files and Folders Inspected

- `docs/AI_OS/dashboard`
- `docs/concepts/aios-dashboard-and-interface-concepts.md`
- `docs/roadmap/aios-product-roadmap.md`
- `docs/audits/phase-83-dashboard-dispatcher-orchestration-triage.md`
- `docs/audits/phase-84-dashboard-summary-extraction.md`

Reference scan scope:

- `docs`
- `apps`
- `automation`
- `scripts`
- `services`
- `schemas`
- `tests`
- `.github`

## Counts

| Item | Count |
| --- | ---: |
| Total tracked files in `docs/AI_OS/dashboard` | 127 |
| Dashboard files matching draft/planning/generated patterns | 124 |
| Dashboard subfolders | 1 |
| Files under `docs/AI_OS/dashboard/sidebar` | 5 |

The dashboard folder is still mostly generated/planning material, but active references prevent a whole-folder archive right now.

## Likely Source-of-Truth or Contract-Style Files

These files contain useful contract or boundary ideas that should be extracted before archive:

- `AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md`
- `AIOS_DASHBOARD_STATUS_MOCK_DATA_CONTRACT_DRAFT.md`
- `AIOS_DASHBOARD_FIXTURE_DATA_RULES_DRAFT.md`
- `AIOS_DASHBOARD_ALLOWED_DATA_SOURCES_DRAFT.md`
- `AIOS_DASHBOARD_BLOCKED_DATA_SOURCES_DRAFT.md`
- `AIOS_DASHBOARD_CHECKPOINT_INPUT_CONTRACT_DRAFT.md`
- `AIOS_DASHBOARD_NEXT_ACTION_INPUT_CONTRACT_DRAFT.md`
- `AIOS_DASHBOARD_VALIDATOR_HEALTH_INPUT_CONTRACT_DRAFT.md`
- `AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md`
- `AIOS_AI_ASSISTANT_PANEL_CONTRACT_DRAFT.md`
- `AIOS_DASHBOARD_COMMAND_CENTER_CONTROL_PLANE_DRAFT.md`
- `AIOS_DASHBOARD_MOBILE_STATUS_BEHAVIOR_PLAN_DRAFT.md`
- `AIOS_DASHBOARD_OPERATOR_READABILITY_ACCESSIBILITY_DRAFT.md`
- `AIOS_STATIC_DASHBOARD_PROTOTYPE_ARCHITECTURE_DRAFT.md`

## Likely Archive-Safe Groups After Reference Cleanup

These groups are likely archive candidates after contract extraction and reference retirement:

- `AIOS_DASHBOARD_*_DRAFT.md`
- `AIOS_*_MOCK_*`
- `AIOS_*_FIXTURE_*`
- `AIOS_PHASE13_*_IMPLEMENTATION_PLAN_DRAFT.md`
- `AIOS_SCREENSHOT_*`
- `AIOS_*_WIRING_*`
- `AIOS_*_READINESS_*`
- `docs/AI_OS/dashboard/sidebar/AIOS_LEFT_COLLAPSIBLE_SIDEBAR_REQUIREMENT_DRAFT_2026-05-07_153925.md`

Do not move these yet. The current pass is report-only.

## Human-Review Items

- Whether `docs/specs/aios-dashboard-data-contracts.md` should become the canonical dashboard contract.
- Whether dashboard planning remains under `docs/concepts` or gets a `docs/specs` promotion.
- Whether `apps/dashboard` should own dashboard implementation docs instead of `docs/AI_OS/dashboard`.
- Whether static mock contract, fixture rules, and source maps are still valid after PR #180 archived `Reports/`.
- Whether dashboard AI assistant concepts remain mock-only.

## Reference Scan Results

### Folder-Level References

References to `docs/AI_OS/dashboard` remain in docs, app mock data, and automation.

Active non-audit references found:

- `apps/dashboard/mock-data/app-registry.example.json`
- `automation/status/Test-AiOsDashboardCommandCenterReadiness.DRY_RUN.ps1`
- `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `automation/status/Test-AiOsPhase12IntegrationAudit.DRY_RUN.ps1`
- `automation/status/Test-AiOsStage7To12MasterValidation.DRY_RUN.ps1`

Historical/docs references also remain in:

- `docs/AI_OS/audits/*`
- `docs/AI_OS/change_control/CHANGE_OWNERSHIP_MAP.json`
- `docs/AI_OS/governance/*`
- `docs/AI_OS/problem_resolution/PROBLEM_TO_OWNER_MAP.json`
- prior cleanup audits under `docs/audits/`
- canonical dashboard concept and roadmap docs

### Important Filename References

Dashboard contract files still have active automation references:

- `AIOS_DASHBOARD_DATA_CONTRACT_DRAFT.md`
  - `automation/startup/Get-AiOsMorningBriefState.DRY_RUN.ps1`
  - `automation/status/Get-AiOsApprovalState.DRY_RUN.ps1`
  - `automation/status/Get-AiOsDashboardSnapshot.DRY_RUN.ps1`
  - `automation/status/Test-AiOsApprovalQueueValidator.DRY_RUN.ps1`
  - `automation/status/Test-AiOsFullReadinessAudit.DRY_RUN.ps1`

- `AIOS_STATIC_DASHBOARD_MOCK_CONTRACT_DRAFT.md`
  - `automation/status/Test-AiOsDashboardImplementationSelection.DRY_RUN.ps1`
  - `automation/status/Test-AiOsDashboardPrototypeMegabatch.DRY_RUN.ps1`
  - `automation/status/Test-AiOsOperatorManualArchitecture.DRY_RUN.ps1`
  - `automation/status/Test-AiOsRenderingStackEvaluation.DRY_RUN.ps1`
  - `automation/status/Test-AiOsStaticDashboardMockContract.DRY_RUN.ps1`
  - `automation/status/Test-AiOsStaticDashboardPrototypeArchitecture.DRY_RUN.ps1`
  - `automation/status/Test-AiOsVisualDashboardRenderPrep.DRY_RUN.ps1`

- `AIOS_DASHBOARD_FIXTURE_DATA_RULES_DRAFT.md`
  - `automation/status/Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`

- `AIOS_DASHBOARD_COMMAND_CENTER_CONTROL_PLANE_DRAFT.md`
  - referenced by `docs/AI_OS/dashboard/AIOS_DASHBOARD_VALIDATION_INDEX_DRAFT.md`
  - concept extracted in Phase 84, but not retired from active validator checks.

These references mean whole-folder archival would break active DRY_RUN validators and app fixture references unless those references are retired first.

## Data-Contract Need

Data-contract extraction is still needed.

The Phase 84 concept doc captured direction, but not enough exact contract detail to replace active dashboard contract files. Legacy dashboard docs still contain contract-level specifics for:

- dashboard state fields,
- status fixture shape,
- allowed status values,
- fixture safety rules,
- validator health fields,
- checkpoint fields,
- next safe action source priority,
- static dashboard mock boundaries,
- command-center maturity levels,
- AI assistant panel inputs and outputs,
- mobile status behavior.

Recommended destination:

- `docs/specs/aios-dashboard-data-contracts.md`

This spec should explicitly say it is read-only, local-first, fixture-first, no secrets, no live AI, no broker/OANDA, no real webhook, and no live trading.

## Archive Readiness Decision

Decision: **NEEDS DATA-CONTRACT EXTRACTION FIRST**

Secondary decision: **NOT ARCHIVE READY as a whole folder**

Reason:

- active automation still references exact dashboard contract files,
- `apps/dashboard/mock-data/app-registry.example.json` references a dashboard doc path,
- contract-level details are not fully captured in canonical docs,
- some docs under `docs/AI_OS/governance` and `docs/AI_OS/change_control` still describe `docs/AI_OS/dashboard` as the requirements location.

Partial archive may become safe after Phase 86 if active references are retired.

## Exact Phase 86 Recommendation

Recommended Phase 86:

`AI_OS PHASE 86 - DASHBOARD DATA-CONTRACT EXTRACTION AND REFERENCE RETIREMENT`

Scope should be tightly controlled.

Allowed outputs:

- create `docs/specs/aios-dashboard-data-contracts.md`
- create `docs/audits/phase-86-dashboard-data-contract-extraction.md`
- optionally update active automation validators only if explicitly approved to repoint from legacy dashboard contract files to the new spec

Phase 86 should not move or delete dashboard source files.

Phase 86 should extract:

- dashboard state schema,
- fixture contract,
- status card contract,
- validator health contract,
- checkpoint contract,
- next action contract,
- command-center readiness levels,
- AI assistant panel contract,
- mobile/responsive behavior contract,
- blocked source and paper-only safety language.

Only after Phase 86 reference retirement should a later archive pass consider moving `docs/AI_OS/dashboard`.

## Risks

- Archiving now would break active DRY_RUN validators.
- Some dashboard docs point at `Reports/` paths that were archived in PR #180, so contract extraction must refresh source paths.
- `apps/dashboard` was scanned for references only; implementation behavior was not reviewed.
- The new data-contract spec must not imply dashboard APPLY, live AI, broker, OANDA, webhook, or trading activation.
- If `docs/AI_OS/dashboard` remains active too long, it will continue to compete with canonical docs.

## Validation Results

Validation required after creating this report:

```powershell
git status --short
git diff --stat
```

Expected:

- only `docs/audits/phase-85-dashboard-archive-readiness.md` changed.
