# AI_OS Dashboard Control Panel Organization Draft

Status: Draft
Mode: Static dashboard command-center planning
Date: 2026-05-08

## Purpose

Define the current static dashboard control-panel organization and the next safe organization priorities for moving from theme/control work into operational command-center readiness.

## Current Visible Dashboard Control Areas

### App Dock

Purpose: left-side navigation for Work Table, App Store, Connectors, Calendar, Notes, and Build Queue.

Current mode: selectable navigation and mock assistant output only.

Future category: action-gated navigation surface.

### Status Strip

Purpose: top-level workspace mode buttons, diagnostics mock action, system status mock action, and local-only theme selector.

Current mode: selectable status/navigation controls and local visual preference.

Future category: command-center control bar with strict mock/live boundary labels.

### Status Panels

Purpose: read-only status cards for overall status, progress, validator, checkpoint, safety, AI assistance, Work Table AI, and next action.

Current mode: fixture-backed visibility with local fallback.

Future category: read-only operational status plane before any automation is considered.

### Work Table

Purpose: center workspace for project brief, prompt stack, build instructions, tool output, approval gate, and validation queue.

Current mode: static cards that update mock assistant/console text.

Future category: primary operator work queue, still approval-gated.

### Work Table AI

Purpose: fixture-only insight panel showing metadata, cards, safe mock actions, blocked actions, and source references.

Current mode: read-only local fixture display.

Future category: AI-assisted review surface with no execution until separately approved.

### Tool Registry

Purpose: fixture-backed display of tool readiness and allowed/blocked tool boundaries.

Current mode: local mock data display only.

Future category: readiness registry, not an install or account connector.

### App Registry

Purpose: static examples for future Calendar, Notes, Reports, and Telemetry apps.

Current mode: mock cards only.

Future category: app launch surface after approval and validator coverage.

### Assistant Rail

Purpose: mock tour/help area with a preview input and Send button.

Current mode: local mock message only; no prompt is sent anywhere.

Future category: local guidance surface before any live AI integration.

### Console Preview

Purpose: static console-style output summarizing selected mock actions.

Current mode: read-only preview text.

Future category: operator event feed after explicit logging rules exist.

## Read-Only, Selectable, And Future Action-Gated Areas

Read-only:

- Status panels.
- Tool registry readiness cards.
- Work Table AI fixture insights.
- Console preview output.

Selectable:

- App Dock buttons.
- Status strip buttons.
- Status panel tabs.
- Work Table cards.
- Tool Registry chips.
- App Registry cards.
- Theme selector.

Future action-gated:

- Diagnostics execution.
- Report generation.
- Checkpoint writing.
- Validator chain execution.
- AI-assisted recommendations.
- Any local automation beyond static preview.

## Fixture-Only Boundaries

The current dashboard may read local mock fixtures and static page state only.

Fixture-only excludes:

- Live APIs.
- Account connections.
- Secrets.
- Credential storage.
- Broker connections.
- Trading execution.
- Deployment.
- Live AI execution.

## Human Approval Gates

Human approval remains required for:

- APPLY actions.
- File writes.
- Commits.
- Pushes.
- Validator additions.
- Dashboard code changes.
- Any future local automation.
- Any future service integration.

## Actions That Must Remain Blocked

Blocked:

- API calls.
- Secret access.
- Account connection.
- Software installation.
- Deployment.
- Broker/trading execution.
- Live AI execution.
- Destructive file operations.
- React edits unless explicitly approved.

## Recommended Next UI Organization Priorities

1. Define operator action categories for each visible control.
2. Create a mock action safety registry.
3. Expand command-center validator coverage.
4. Document the command-center control plane.
5. Keep static dashboard code unchanged until docs and validators agree on the next UI APPLY scope.
