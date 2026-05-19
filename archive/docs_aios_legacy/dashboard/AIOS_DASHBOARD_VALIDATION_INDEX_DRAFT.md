# AI_OS Dashboard Validation Index Draft

Status: Draft
Mode: Dashboard validator and report index
Date: 2026-05-08

## 1. Dashboard Validator Scripts

Dashboard-related DRY_RUN validators and helpers currently found in `automation/status/`:

- `Get-AiOsDashboardSnapshot.DRY_RUN.ps1`
- `Test-AiOsDashboardFixtureLayer.DRY_RUN.ps1`
- `Test-AiOsDashboardImplementationSelection.DRY_RUN.ps1`
- `Test-AiOsDashboardPrepContract.DRY_RUN.ps1`
- `Test-AiOsDashboardPrototypeMegabatch.DRY_RUN.ps1`
- `Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `Test-AiOsDashboardThemeReadiness.DRY_RUN.ps1`
- `Test-AiOsDashboardThemeSelector.DRY_RUN.ps1`
- `Test-AiOsDashboardCommandCenterReadiness.DRY_RUN.ps1`
- `Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1`
- `Test-AiOsStaticDashboardMockContract.DRY_RUN.ps1`
- `Test-AiOsStaticDashboardPrototypeArchitecture.DRY_RUN.ps1`
- `Test-AiOsVisualDashboardRenderPrep.DRY_RUN.ps1`

Related non-dashboard-specific fixture validators also exist, but this index focuses on dashboard readiness and theme-selector coverage.

## 2. Theme Readiness Validator

Validator:

`automation/status/Test-AiOsDashboardThemeReadiness.DRY_RUN.ps1`

Supports:

- Stage 15 dashboard theme readiness validation.
- Theme token foundation verification.
- Inactive theme flavor class verification.

Does not cover:

- Theme selector HTML markup.
- Theme selector JavaScript behavior.
- Browser-rendered visual QA.
- React dashboard parity.

## 3. Theme Selector Validator

Validator:

`automation/status/Test-AiOsDashboardThemeSelector.DRY_RUN.ps1`

Supports:

- Stage 18 selector safety validation.
- Stage 21 CSS polish coverage.
- Stage 24 validation coverage backfill.

Current checks:

- Static dashboard HTML exists.
- Static dashboard JS exists.
- Static dashboard CSS exists.
- Selector markup exists.
- Default theme option exists.
- JavaScript selector binding exists.
- Default reset behavior exists.
- JS references only approved theme classes.
- CSS contains matching `body.theme-*` flavor classes.
- Stage 21 focus and mobile wrapping polish exists.
- Selector-scoped forbidden terms are absent.
- Validator modifies no files when run.

Does not cover:

- Actual rendered browser pixels.
- Cross-browser behavior.
- Automated accessibility scoring.
- React app integration.
- Cloud preference sync.

## 4. Fixture/Readiness Validators If Found

Relevant fixture/static preview validators found:

- `Test-AiOsDashboardFixtureLayer.DRY_RUN.ps1`
- `Test-AiOsDashboardStaticPreviewTransition.DRY_RUN.ps1`
- `Test-AiOsStaticDashboardMockContract.DRY_RUN.ps1`
- `Test-AiOsVisualDashboardRenderPrep.DRY_RUN.ps1`

These support earlier dashboard fixture, static preview, and visual render readiness workflows.

They do not replace the theme selector validator because they are broader dashboard readiness checks and do not specifically assert the Stage 21 theme selector polish details.

Lifetime telemetry fixture:

- `apps/dashboard/mock-data/lifetime-telemetry-fixture.example.json`

This fixture is mock-data only. Complete lifetime time-spent and complete lifetime bytes/KB/MB changed remain `UNKNOWN` unless future evidence-backed telemetry proves those values.

## Command-Center Readiness Validator

Validator:

`automation/status/Test-AiOsDashboardCommandCenterReadiness.DRY_RUN.ps1`

Supports:

- Stage 31 command-center readiness validation.
- Stage 34 reporting/index checkpoint.
- Stage 35 control-plane readiness reporting.
- Stage 36 push-readiness confirmation.

Current checks:

- Static dashboard HTML, JS, and CSS exist.
- Core command-center areas exist.
- Required dashboard safety labels exist.
- Stage 29 control-panel organization doc exists.
- Stage 30 operator action map doc exists.
- Command-center scoped execution-looking forbidden patterns are absent.
- Validator modifies no files when run.

Does not cover:

- Browser screenshots.
- Real API/service readiness.
- React implementation parity.
- Live automation execution.

## Lifetime Development Telemetry Validator

Validator:

`automation/status/Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1`

Supports:

- Stage 40 lifetime telemetry fixture and contract validation.
- Stage 42 lifetime telemetry checkpoint reporting.
- Stage 43 dashboard validation index coverage.
- Stage 44 lifetime telemetry push-readiness confirmation.

Current checks:

- Lifetime telemetry evidence model exists.
- Lifetime telemetry storage contract exists.
- Lifetime telemetry mock fixture exists.
- Mock fixture is valid JSON.
- Complete lifetime time-spent values are `UNKNOWN`.
- Complete lifetime bytes/KB values are `UNKNOWN`.
- Real telemetry collector behavior is disabled.
- Evidence-backed commit count matches the inspected repository state used for Stage 37.
- Execution-looking forbidden patterns are absent from the scoped telemetry files.
- Validator modifies no files when run.

Does not cover:

- Real telemetry collection.
- Complete lifetime time-spent proof.
- Complete lifetime bytes/KB/MB proof.
- Dashboard UI wiring for a Lifetime Telemetry panel.
- React dashboard parity.
- Canonical `Reports/telemetry/` ledger creation.

## 5. Checkpoint Reports

Relevant dashboard and theme checkpoint reports:

- `Reports/checkpoints/CHECKPOINT_PHASE13_DASHBOARD_THEME_SYSTEM.md`
- `Reports/checkpoints/CHECKPOINT_STAGE17_20_DASHBOARD_THEME_SELECTOR.md`
- `Reports/checkpoints/CHECKPOINT_STAGE22_23_DASHBOARD_THEME_SELECTOR_BROWSER_QA.md`
- `Reports/checkpoints/CHECKPOINT_STAGE24_DASHBOARD_STATUS_VALIDATION_COVERAGE.md`
- `Reports/checkpoints/CHECKPOINT_STAGE29_34_DASHBOARD_COMMAND_CENTER_INDEX.md`
- `Reports/checkpoints/CHECKPOINT_STAGE37_42_LIFETIME_TELEMETRY_MODEL.md`

Earlier dashboard planning and implementation DRY_RUN checkpoint reports also exist in `Reports/checkpoints/`.

## 6. Browser QA Reports

Browser QA report:

`Reports/checkpoints/CHECKPOINT_STAGE22_23_DASHBOARD_THEME_SELECTOR_BROWSER_QA.md`

Supports:

- Stage 22 browser visual QA preparation.
- Stage 23 operator browser QA result.

Recorded result:

`GOOD TO GO`

Does not cover:

- Every browser engine.
- Automated accessibility audit.
- React dashboard implementation.
- Long-term regression screenshots.

## 7. Stage Support Map

- Stage 15: `Test-AiOsDashboardThemeReadiness.DRY_RUN.ps1`
- Stage 18: `Test-AiOsDashboardThemeSelector.DRY_RUN.ps1`
- Stage 20: `CHECKPOINT_STAGE17_20_DASHBOARD_THEME_SELECTOR.md`
- Stage 21: `Test-AiOsDashboardThemeSelector.DRY_RUN.ps1` after Stage 24 backfill
- Stage 22: `CHECKPOINT_STAGE22_23_DASHBOARD_THEME_SELECTOR_BROWSER_QA.md`
- Stage 23: `CHECKPOINT_STAGE22_23_DASHBOARD_THEME_SELECTOR_BROWSER_QA.md`
- Stage 24: `CHECKPOINT_STAGE24_DASHBOARD_STATUS_VALIDATION_COVERAGE.md`
- Stage 25: `AIOS_DASHBOARD_THEME_SELECTOR_HANDOFF_PACKET.md`
- Stage 26: `AIOS_STATIC_DASHBOARD_OPERATOR_QUICKSTART_DRAFT.md`
- Stage 27: this validation index
- Stage 29: `AIOS_DASHBOARD_CONTROL_PANEL_ORGANIZATION_DRAFT.md`
- Stage 30: `AIOS_DASHBOARD_OPERATOR_ACTION_MAP_DRAFT.md`
- Stage 31: `Test-AiOsDashboardCommandCenterReadiness.DRY_RUN.ps1`
- Stage 32: `AIOS_DASHBOARD_MOCK_ACTION_SAFETY_REGISTRY_DRAFT.md`
- Stage 33: `AIOS_DASHBOARD_COMMAND_CENTER_CONTROL_PLANE_DRAFT.md`
- Stage 34: `CHECKPOINT_STAGE29_34_DASHBOARD_COMMAND_CENTER_INDEX.md`
- Stage 37: `AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_EVIDENCE_MODEL_DRAFT.md`
- Stage 38: `AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_STORAGE_CONTRACT_DRAFT.md`
- Stage 39: `lifetime-telemetry-fixture.example.json`
- Stage 40: `Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1`
- Stage 41: `AIOS_DASHBOARD_LIFETIME_TELEMETRY_PANEL_PLAN_DRAFT.md`
- Stage 42: `CHECKPOINT_STAGE37_42_LIFETIME_TELEMETRY_MODEL.md`
- Stage 43: this validation index update

## 8. What Each Validator Does Not Cover

Theme readiness validator does not cover browser QA or selector JS.

Theme selector validator does not cover rendered screenshots, accessibility scoring, or React parity.

Command-center readiness validator does not cover executable automation, API readiness, React parity, or browser screenshots.

Lifetime telemetry validator does not cover real telemetry collection, complete lifetime time evidence, complete lifetime bytes/KB evidence, dashboard UI wiring, or React parity.

Fixture validators do not cover local theme preference storage, body class switching, or Stage 21 selector polish.

Visual render prep validators do not prove all theme options were manually inspected.

No current validator connects APIs, reads secrets, deploys, executes broker/trading logic, or runs live AI execution.

## 9. Recommended Next Validation Gaps

Recommended future gaps:

- Add a DRY_RUN-only browser QA checklist report template for future visual passes.
- Add a static screenshot capture plan only if explicitly approved.
- Add accessibility checklist coverage without installing tools.
- Add React parity DRY_RUN planning only after explicit React approval.
- Add dashboard validation index maintenance rules when new validators are created.
- Add fixture-only Lifetime Telemetry dashboard panel wiring only after separate DRY_RUN approval.
- Create canonical `Reports/telemetry/` ledger and summary files only after separate APPLY approval.
- Keep complete lifetime time and bytes/KB/MB changed as `UNKNOWN` until evidence exists.

Blocked until separately approved:

- API validation.
- Deployment validation.
- Broker/trading execution validation.
- Live AI execution validation.
- Account or secret validation.
