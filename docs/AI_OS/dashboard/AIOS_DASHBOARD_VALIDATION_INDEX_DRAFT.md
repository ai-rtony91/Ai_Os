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

## 5. Checkpoint Reports

Relevant dashboard and theme checkpoint reports:

- `Reports/checkpoints/CHECKPOINT_PHASE13_DASHBOARD_THEME_SYSTEM.md`
- `Reports/checkpoints/CHECKPOINT_STAGE17_20_DASHBOARD_THEME_SELECTOR.md`
- `Reports/checkpoints/CHECKPOINT_STAGE22_23_DASHBOARD_THEME_SELECTOR_BROWSER_QA.md`
- `Reports/checkpoints/CHECKPOINT_STAGE24_DASHBOARD_STATUS_VALIDATION_COVERAGE.md`

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

## 8. What Each Validator Does Not Cover

Theme readiness validator does not cover browser QA or selector JS.

Theme selector validator does not cover rendered screenshots, accessibility scoring, or React parity.

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

Blocked until separately approved:

- API validation.
- Deployment validation.
- Broker/trading execution validation.
- Live AI execution validation.
- Account or secret validation.
