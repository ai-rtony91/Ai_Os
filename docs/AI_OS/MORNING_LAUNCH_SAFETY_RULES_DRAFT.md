# AI_OS Morning Launch Safety Rules Draft

## Purpose

This draft defines future safe launch rules without enabling launch automation. It does not approve opening apps, browsers, Codex, Task Scheduler changes, startup tasks, screen recording, screenshots, or helper scripts.

## Future Morning Launch Purpose

The Morning Launch workflow should help prepare the correct AI_OS work environment only after explicit user approval. It should keep the user in control and avoid automatic changes to the desktop, browser, startup tasks, or repo state.

## Default Workday Targets

Future planned targets may include:

- PowerShell in the active repo path.
- Codex CLI in the active repo path.
- File Explorer in the active repo path.
- ChatGPT companion window.
- GitHub repo page only if later approved.

No browser, game, app, Codex, or external tool launch is approved by this draft.

## Codex Launch And Session-Start Rule

- Codex opening may mark `session_start_time`.
- Codex opening may set `codex_opened=true`.
- Codex must verify the active repo path before work begins.
- Codex must not auto-record.
- Codex must not launch browsers, apps, or external tools unless separately approved.

## Screen Recording Status

- Planning only.
- No automatic recording.
- Recording requires separate approval.
- Microphone defaults to OFF under the draft screen recording policy.
- Sensitive-window stop rules must apply before any future recording.

## Future Telemetry Capture Plan

Future Morning Launch telemetry may include:

- `session_start_time`
- `codex_opened`
- `planned_windows_opened`
- `unexpected_windows_detected`
- `user_input_char_count`
- `progress_percent`
- `final_git_status`

## Known Unresolved Items

- Codex launch method remains UNKNOWN.
- App/browser launch approval model remains UNKNOWN.
- Privacy-safe window detection remains unresolved.
- `progress_percent` formula remains UNKNOWN.
- Morning workflow could become unsafe if converted into app launch automation without guardrails.
