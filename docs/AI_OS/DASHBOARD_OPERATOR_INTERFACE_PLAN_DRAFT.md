# AI_OS Dashboard Operator Interface Plan Draft

## Purpose

This draft defines the dashboard as a future read-only operator console first. It does not approve dashboard code changes, app launch automation, browser launch automation, telemetry migration, screen recording, broker execution, live trading, or startup task changes.

## Current Dashboard State

The current dashboard is a React + Vite app under:

```text
apps\dashboard
```

It is not yet an AI_OS operator console.

## Future Operator Interface Role

The dashboard should eventually become the main AI_OS operator interface. Its first safe role should be read-only visibility, not action execution.

## Read-Only Console First

The future dashboard should initially show:

- Repo clean status.
- Current AI_OS stage.
- `progress_percent`.
- Morning Brief summary.
- Risk and unknowns.
- Next safe action.
- Work-session status.
- Telemetry summary.

## Approval Gates

The dashboard must not perform actions until separate approval rules exist for:

- Launching apps.
- Opening browsers.
- Opening Codex.
- Running scripts.
- Editing files.
- Writing telemetry.
- Handling broker/trading workflows.

## Known Unresolved Items

- Dashboard data source remains UNKNOWN.
- `progress_percent` formula remains UNKNOWN.
- Trading Mode boundaries need later safety review.
- Codex launch integration method remains UNKNOWN.
- Mode-based launcher could become unsafe if it opens apps or broker tools without explicit approval.
- Current dashboard is still React + Vite and not yet an operator console.
