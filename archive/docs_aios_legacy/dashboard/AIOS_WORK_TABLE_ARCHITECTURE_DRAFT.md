# AI_OS Work Table Architecture Draft

## Purpose

The AI_OS Work Table is the future central workspace where project packets, prompts, build instructions, tool outputs, validation results, and approval gates can be displayed before any APPLY work happens.

This draft is static/planning only. It does not create backend calls, API calls, credentials, persistence, service-worker registration, broker/trading automation, or a live order path.

## Architecture Decision

The dashboard should use this layout model:

- Left sidebar: App Dock, App Store, app categories, and connectors.
- Center/main area: Work Table.
- Right rail: AI Assistant guide, tour, and help panel.
- Top navigation: workspace mode, status, reports, telemetry, admin, and diagnostics.

The Work Table should be the default central panel and may later become an expandable center workspace.

## Work Table Responsibilities

### Active Build Area

Shows the selected app or feature packet, current objective, current stage, status label, and next safe action.

### Tool Output Area

Shows static DRY_RUN output, validator output, mismatch labels, blocked actions, and operator-facing summaries.

### Project Instruction Area

Shows approved human instructions, allowed files, blocked files, allowed mode, and expected result.

### Approval Gate Area

Shows whether APPLY is allowed, which human approval is required, required validators, git checkpoint status, and stop conditions.

## Work Table Data Shape

Future static fixture data may include:

- `packet_id`
- `packet_title`
- `stage`
- `objective`
- `allowed_files`
- `blocked_actions`
- `tools_needed`
- `validation_commands`
- `approval_required`
- `status`
- `next_safe_action`

## Tool Output Boundary

Tool outputs displayed in the Work Table must be static, approved, and non-secret. The Work Table must not execute commands, call APIs, register a service worker, write files, persist telemetry, or trigger broker/trading automation.

## App Dock Relationship

The App Dock should choose app categories or candidate apps. Selecting an app should update the Work Table with static mock information only until a future approved implementation exists.

## AI Assistant Relationship

The AI Assistant guide should explain the selected Work Table packet, safety locks, next safe action, and blocked actions. It must remain a mock/help panel unless future explicit approval allows a real assistant integration.

## Safety Boundary

No backend, no API calls, no credentials, no persistence, no service-worker registration, no broker/trading automation, and no live order path are approved by this draft.
