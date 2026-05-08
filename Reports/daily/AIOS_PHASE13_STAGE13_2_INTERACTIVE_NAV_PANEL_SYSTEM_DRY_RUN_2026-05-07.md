# AI_OS Phase 13 Stage 13.2 Interactive Navigation + Panel Organization System DRY_RUN

Date: 2026-05-07
Mode: DRY_RUN
Classification: AI_OS project work only

## Phase

Phase 13 - Dashboard UI Implementation

## Stage

Stage 13.2 - Interactive Navigation + Panel Organization System

## Mission

Plan a cleaner interactive command-center dashboard where top navigation and drawer controls reveal related panels, widgets, and detail views inside one dashboard shell. No dashboard HTML/CSS/JS edits are included in this DRY_RUN.

## Files Inspected

- apps/dashboard/AIOS_STATIC_PREVIEW.html
- apps/dashboard/css/aios-static-preview.css
- apps/dashboard/js/aios-static-preview.js
- apps/dashboard/mock-data/
- docs/AI_OS/dashboard/
- Reports/progress/
- Reports/checkpoints/
- Reports/health/
- Reports/daily/

## Current Buttons And Panels Found

Drawer app dock:

- Work Table
- App Store
- Connectors
- Calendar
- Notes
- Build Queue

Top status strip:

- MENU drawer reopen
- Work Table
- Reports
- Telemetry
- Admin
- System Status
- Run Diagnostics

Status panel tabs:

- Status
- Progress
- Validator
- Checkpoint
- Safety
- AI Assistance
- Work Table AI
- Next Action

Work Table cards:

- Project Brief
- Prompt Stack
- Build Instructions
- Tool Output
- Approval Gate
- Validation Queue

Tool Registry chips:

- ChatGPT
- Codex
- Claude
- GitHub
- PowerShell
- Web/Research
- Files/OneDrive
- Reports
- Telemetry

App Registry cards:

- Calendar App
- Notes App
- Reports App
- Telemetry App

Other surfaces:

- AI Assistant Guide
- Console panel
- Static mock-data fixture loaders

## Duplicate Or Overlap Risks

- Reports appears as top nav, tool registry, app registry, and expected report panel content.
- Telemetry appears as top nav, tool registry, app registry, and expected telemetry panel content.
- Validator appears in status-panel tabs and Work Table validation queue.
- Safety appears in status-panel tabs, drawer safety locks, approval gates, and admin/system actions.
- AI Assistance appears as status card, assistant rail, and future assistant panel.
- Work Table AI appears as status card but not yet as an organized work-table intelligence panel.
- Current layout mixes primary navigation, status cards, work cards, app examples, and tool registry in a way that can feel scattered.

## Proposed Main Nav

1. Command Center
2. Current Project / About
3. Progress
4. Reports + Telemetry
5. Validators
6. Safety
7. AI Assistance
8. Work Table AI
9. Apps / Admin

## Proposed Panel Groups

Command Center:

- AI_OS current status
- Next safe action
- Latest checkpoint
- Latest commit
- Major stats summary

Current Project / About:

- What AI_OS is
- Current phase/stage
- Project purpose
- Local-first system boundaries
- No-live-trading product boundary

Progress:

- Phase completion
- Stage completion
- Files created
- KB / MB created
- Daily growth
- Progress ledger snapshot

Reports + Telemetry:

- Daily reports
- Checkpoint reports
- Telemetry snapshots
- Progress ledger
- Separate labels for report evidence and telemetry evidence inside the same panel

Validators:

- Master validator status
- Recent PASS/WARN/FAIL
- Validation queue
- Missing validator flags

Safety:

- No secrets
- No broker/live trading
- Blocked actions
- Approval gates
- Protected file status

AI Assistance:

- Assistant status
- Mock assistant output
- Next-action guidance
- Approval reminders

Work Table AI:

- Row/card intelligence
- Scoring/recommendation placeholder
- Approval-required flags
- Sorting/filtering recommendation model

Apps / Admin:

- App registry
- Tool registry
- Admin/system actions
- Connector review boundaries

## Reports + Telemetry Decision

Reports and Telemetry should be grouped under one main nav tab because they are operational evidence surfaces. They must remain separately labeled inside that tab:

- Reports = daily reports, checkpoints, audit outputs, operator evidence.
- Telemetry = health snapshots, validator summaries, dashboard status signals, runtime-style state.

This reduces duplicate top-level navigation while preserving the difference between report artifacts and telemetry/status signals.

## Major AI_OS Stats Layout

Primary Command Center stats to plan:

- Current phase
- Current stage
- Phase progress %
- Stage progress %
- Latest commit
- Latest checkpoint
- Validator status
- Safety status
- Files created today
- KB / MB created today
- Next action
- AI Assistance status
- Work Table AI status

Recommended layout:

- One top summary strip with phase, stage, validator, safety, next action.
- One compact metrics grid with progress %, files/KB/MB, latest commit, latest checkpoint.
- One detail panel area that changes with selected nav item.

## Interaction Model

- One dashboard shell only.
- One major panel active at a time.
- Top nav and drawer nav should map to the same panel model.
- Drawer can remain an app/tool dock, but primary content should be governed by main nav panel state.
- Work cards should open contextual detail widgets or update an active panel, not feel like unrelated duplicate pages.
- Optional modal/popup should be reserved for detail expansion only.
- Smooth panel transitions should use lightweight opacity/transform CSS only.
- All data remains local mock-data or static fixture content.
- No external APIs, database, broker, live AI API, deployment, or trading logic.

## Mobile / Desktop Ergonomics

Desktop:

- Keep drawer full-hide/full-show behavior.
- Keep MENU in top nav leading slot.
- Use one active panel region below the command hero/stats.
- Avoid duplicated rows of unrelated buttons.

Mobile:

- Drawer remains overlay.
- Main nav should wrap cleanly or become horizontally scrollable if needed.
- Major stats should collapse to two-column then one-column.
- Detail widgets should stack vertically.
- No horizontal overflow.
- Touch targets stay at least current status-chip size.

## Files To Create On APPLY

- docs/AI_OS/dashboard/AIOS_DASHBOARD_NAVIGATION_INFORMATION_ARCHITECTURE_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_PANEL_GROUPING_MODEL_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_INTERACTIVE_WIDGET_MODEL_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_REPORTS_TELEMETRY_GROUPING_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_MAJOR_STATS_LAYOUT_DRAFT.md
- docs/AI_OS/dashboard/AIOS_DASHBOARD_TRANSITION_ERGONOMICS_DRAFT.md
- apps/dashboard/mock-data/dashboard-navigation-model.example.json
- apps/dashboard/mock-data/dashboard-panel-groups.example.json
- apps/dashboard/mock-data/dashboard-major-stats.example.json

## Safety Blocks Confirmed

- No secrets.
- No external APIs.
- No database connection.
- No broker connection.
- No live AI API connection.
- No live trading code.
- No trade placement.
- No deployment.
- No protected root governance file edits.
- No dashboard code edits during DRY_RUN.
- No dual Codex / POI / worktree files.

## DRY_RUN Result

DRY_RUN_COMPLETE_PENDING_APPLY

## Next Safe Action

After operator approval, create the planned docs and mock-data model files only. Do not edit dashboard HTML/CSS/JS until a later explicit APPLY stage.
