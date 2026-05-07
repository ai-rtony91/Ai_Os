# Dashboard Structure Reference

## Working File

`apps/dashboard/AIOS_STATIC_PREVIEW.html` is the current working dashboard.

## Skeleton Role

This skeleton defines the preferred structure for future dashboard work. It is a design standard/reference only.

## Current Structure

- Left sidebar: App Dock, App Store, app categories, and connectors.
- Top strip: workspace modes, reports, telemetry, admin, system status, and diagnostics.
- Center/main area: Ai_Os Work Table.
- Right rail: AI Assistant Guide for tour/help text.
- Tool Registry lane: static tool list for ChatGPT, Codex, Claude, GitHub, PowerShell, Web/Research, Files/OneDrive, Reports, and Telemetry.
- App Registry lane: static examples for Calendar App, Notes App, Reports App, and Telemetry App.
- Console panel: static Work Table console output.

## Work Table Areas

- Project Brief.
- Prompt Stack.
- Build Instructions.
- Tool Output.
- Approval Gate.
- Validation Queue.

## Future Folder Shape

- `concepts/`: experimental UI concepts.
- `styles/`: split-out CSS when approved.
- `scripts/`: local UI-only JavaScript when approved.
- `mock-data/`: static placeholder data when approved.

## Boundary

This file does not approve backend calls, API calls, credentials, persistence, service-worker registration, broker/trading automation, live order path behavior, or production dashboard activation.

Future restructuring requires explicit approval and validation.
