# AI_OS Morning Brief Workflow Plan Draft

## Purpose

This draft defines a text-only daily Morning Brief workflow. It does not approve app launch automation, browser launch, startup tasks, screenshots, screen recording, telemetry automation, or edits to existing scripts.

## Morning Brief Goal

The Morning Brief should give the user a safe workday starting point before any action is taken. It should summarize what is known, what is blocked, and what the next safe action is.

## Text-Only Brief Contents

A future Morning Brief should include:

- Date.
- Active repo path.
- `git status --short --branch` result.
- Current AI_OS stage or task.
- Today objective.
- Files or folders inspected.
- Planned work windows.
- Unexpected windows detected.
- Risks and unknowns.
- Unsafe actions not approved.
- Next safe action.

## Clean-Slate Window Rule

Before work begins, the workflow should identify whether open windows are part of the planned workday. It must not close, move, launch, or alter windows without separate approval.

## Window Classification

| Class | Meaning | Planned response |
|---|---|---|
| planned work window | Window expected for AI_OS work. | Report as OK. |
| unexpected window | Window not part of the current work plan. | Report and ask before action. |
| entertainment/game window | Game or entertainment-related window. | Report only; do not close. |
| private/sensitive window | Email, bank, broker, keys, personal docs, or private data. | Stop exposure-sensitive work and request user direction. |
| ignored/background process | Normal system or background process. | Ignore unless suspicious. |

## Known Unresolved Items

- Codex launch method remains UNKNOWN.
- App/browser launch approval model remains UNKNOWN.
- Privacy-safe window detection remains unresolved.
- `progress_percent` formula remains UNKNOWN.
- Morning workflow could become unsafe if converted into app launch automation without guardrails.
