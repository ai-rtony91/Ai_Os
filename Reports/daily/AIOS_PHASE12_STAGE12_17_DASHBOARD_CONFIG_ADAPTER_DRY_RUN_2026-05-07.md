# AI_OS Phase 12 Stage 12.17 Dashboard Config + Data Adapter Foundation DRY_RUN

Date: 2026-05-07
Mode: DRY_RUN
Classification: AI_OS project work only
Phase: Phase 12 - Productization + System-Wide Integration
Stage: Stage 12.17 - Dashboard Config + Data Adapter Foundation
Current commit inspected: 692e600

## Task

Create a DRY_RUN plan for making the existing dashboard configurable, editable, and data-adapter ready. The goal is to make future buttons, labels, cards, order, and data sources changeable through clean local config and adapter boundaries rather than messy hardcoded edits.

This DRY_RUN creates only this report and the matching checkpoint. It does not edit dashboard HTML, CSS, or JavaScript.

## Mismatch

User-provided status said the current commit should be the latest clean pushed commit after Stage 12.16. Terminal evidence shows the repo is on `main` at `692e600`, but two untracked files from the prior Stage 12.17 dashboard UI DRY_RUN are present:

- Reports/checkpoints/CHECKPOINT_2026-05-07_PHASE12_STAGE12_17_DASHBOARD_STATUS_UI_DRY_RUN.md
- Reports/daily/AIOS_PHASE12_STAGE12_17_DASHBOARD_STATUS_UI_DRY_RUN_2026-05-07.md

This is marked as MISMATCH. The files were not overwritten, deleted, moved, renamed, or edited. Protected `ERROR_LOG.md` was not modified because this prompt explicitly blocks protected root governance edits.

## Files Inspected

- apps/dashboard/AIOS_STATIC_PREVIEW.html
- apps/dashboard/css/aios-static-preview.css
- apps/dashboard/js/aios-static-preview.js
- apps/dashboard/mock-data/
- docs/AI_OS/dashboard/
- Reports/progress/

## Existing Hardcoded UI Areas

Current hardcoded areas observed:

- Sidebar app dock buttons use inline button text and `data-tab` / `data-action` attributes.
- Top status strip buttons are hardcoded as `status-chip` buttons.
- Work table cards are hardcoded as `work-card` articles with fixed labels, headings, and descriptions.
- Tool registry buttons are hardcoded as `registry-chip` buttons.
- App registry cards are hardcoded as `glass-card app-card` articles with fixed labels, headings, metrics, and descriptions.
- Assistant and console response copy is hardcoded in the JavaScript `messages` object.
- Tap targets are selected through static CSS selectors in JavaScript.
- Layout order is controlled by HTML order and CSS grid rules, not a registry.

## Step 1 - Inspect Existing Dashboard Structure

Findings:

- The existing dashboard structure should be reused.
- No separate redesign folder is needed.
- Config work should preserve `dashboard-shell`, `command-sidebar`, `status-strip`, `command-stage`, `work-table`, `assistant-rail`, `registry-section`, `panel-grid`, and `console-panel`.
- Future APPLY should only introduce config-driven lookup and rendering where it reduces hardcoded edits.

## Step 2 - Dashboard Card / Button Config Registry Plan

Plan:

- Create `apps/dashboard/mock-data/dashboard-ui-registry.example.json`.
- Define registries for:
  - sidebar buttons
  - status strip buttons
  - work table cards
  - tool registry chips
  - app registry cards
  - assistant/console messages
- Each registry item should include:
  - id
  - label
  - title
  - description
  - action
  - tab if applicable
  - status or metric if applicable
  - enabled/blocked state
  - display order

Boundary:

- This registry is local mock/config data only.
- It must not contain secrets, account IDs, broker data, database credentials, or external URLs.

## Step 3 - Local Mock-Data Adapter Boundary Plan

Plan:

- Create `apps/dashboard/mock-data/dashboard-data-sources.example.json`.
- Define local file sources for status fixtures, dashboard fixture groups, and UI registry files.
- Define a read-only adapter boundary that reads local JSON and returns normalized dashboard data.
- Missing files must return UNKNOWN.
- Invalid JSON must return INVALID DATA.
- Conflicting sources must return MISMATCH.

Current existing doc:

- `docs/AI_OS/dashboard/AIOS_DASHBOARD_DATA_ADAPTER_BOUNDARY_DRAFT.md` already exists and should be skipped on APPLY.

## Step 4 - Future API / Database Adapter Boundary Plan

Architecture rule:

```text
Dashboard UI -> local config / mock-data now -> API adapter later -> database/backend later
```

Plan:

- Create `docs/AI_OS/dashboard/AIOS_DASHBOARD_FUTURE_API_DATABASE_BOUNDARY_DRAFT.md`.
- Document that the browser dashboard must not connect directly to a database.
- Future API adapter may provide read-only status endpoints after separate approval.
- Future database/backend access must be server-side only and must use approved secrets management.
- Dashboard code must not store database credentials, broker tokens, API keys, or private credentials.

Blocked:

- Browser-to-database connections.
- External API calls during mock-data stage.
- Broker, trading, deployment, or credential logic.

## Step 5 - Editable Layout / Label Control Rules

Plan:

- Create `apps/dashboard/mock-data/dashboard-layout-registry.example.json`.
- Create `docs/AI_OS/dashboard/AIOS_DASHBOARD_EDITABLE_LAYOUT_RULES_DRAFT.md`.
- Create `docs/AI_OS/dashboard/AIOS_DASHBOARD_BUTTON_CARD_REGISTRY_DRAFT.md`.
- Define order and visibility through config where practical.
- Keep labels concise and editable in one registry file.
- Require stable IDs for every card, button, chip, and action.
- Use existing CSS classes unless a later approved implementation requires new classes.

Rules:

- Config may control labels, order, visibility, disabled/blocked state, and source mapping.
- Config must not execute code.
- Config must not contain secrets.
- Config must not create live broker, trading, database, or deployment paths.

## Files To Create On APPLY

- apps/dashboard/mock-data/dashboard-ui-registry.example.json
- apps/dashboard/mock-data/dashboard-data-sources.example.json
- apps/dashboard/mock-data/dashboard-layout-registry.example.json
- docs/AI_OS/dashboard/AIOS_DASHBOARD_CONFIG_REGISTRY_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_EDITABLE_LAYOUT_RULES_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_FUTURE_API_DATABASE_BOUNDARY_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_BUTTON_CARD_REGISTRY_DRAFT.md

## Files Skipped Already Existed

- docs/AI_OS/dashboard/AIOS_DASHBOARD_DATA_ADAPTER_BOUNDARY_DRAFT.md

## Existing Files That Would Be Edited Later

Only after a separate approved APPLY:

- apps/dashboard/AIOS_STATIC_PREVIEW.html
- apps/dashboard/css/aios-static-preview.css
- apps/dashboard/js/aios-static-preview.js

## Files Must Not Be Touched

- Protected root governance files.
- Secrets, credentials, API keys, broker tokens, private keys, and recovery keys.
- Live broker or trading execution files.
- Database credentials or direct browser database connection logic.
- External API integrations.
- Dual Codex, POI, worktree, or Phase 13 files.
- Separate dashboard redesign folders.

## Progress Ledger Proposal

Reports/progress exists. This DRY_RUN proposes the following row but does not append it:

```csv
date,time,stage,task_id,task_name,planned_steps,completed_steps,percent_complete,status,blocked,blocker,next_action,checkpoint_file,commit_hash,git_status,notes
2026-05-07,UNKNOWN,Phase 12 Stage 12.17,AIOS-P12-S12-17-DRYRUN,Dashboard Config + Data Adapter Foundation,5,1,20,DRY_RUN_COMPLETE_PENDING_APPLY,NO,,Approve APPLY for Phase 12 Stage 12.17 config adapter foundation,Reports/checkpoints/CHECKPOINT_2026-05-07_PHASE12_STAGE12_17_DASHBOARD_CONFIG_ADAPTER_DRY_RUN.md,692e600,main has untracked prior DRY_RUN files,MISMATCH documented; no ledger append performed
```

## Protected Files Not Touched

- README.md
- AGENTS.md
- RISK_POLICY.md
- SOURCE_LOG.md
- ERROR_LOG.md
- HALLUCINATION_LOG.md
- AAR.md
- DAILY_REPORT.md
- WHITEPAPER.md
- docs/White_Paper.md

## Safety Blocks Confirmed

- No overwrite performed.
- No delete performed.
- No move performed.
- No rename performed.
- No secrets added.
- No broker connection made.
- No real database connection made.
- No external APIs used.
- No live trading code created.
- No trades placed.
- No protected root governance files modified.
- No deployment performed.
- No dual Codex, POI, worktree, or Phase 13 files created.
- No dashboard HTML, CSS, or JavaScript edited during DRY_RUN.
- No separate redesign folder created.

## Errors

None observed during inspection.

## Unknowns

- Final config schema is UNKNOWN until APPLY creates the example registry files.
- Final adapter function shape is UNKNOWN until a later implementation stage edits JavaScript.
- Final UI render behavior is UNKNOWN because dashboard code was intentionally not edited.

## DRY_RUN Result

DRY_RUN_COMPLETE_PENDING_APPLY_WITH_MISMATCH_NOTED.

Only the DRY_RUN report and checkpoint were created. Dashboard implementation files remain unchanged.

## Next Safe Action

Approve APPLY mode for AI_OS Phase 12 Stage 12.17 Dashboard Config + Data Adapter Foundation using this DRY_RUN report.

