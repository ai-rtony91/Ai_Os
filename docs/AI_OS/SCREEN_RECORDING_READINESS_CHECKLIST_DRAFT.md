# AI_OS Screen Recording Readiness Checklist Draft

## Purpose

This draft defines manual recording readiness only. It does not approve screen recording, screenshots, recording automation, folder creation, Windows setting changes, Xbox Game Bar setting changes, Snipping Tool setting changes, startup task changes, or external app launch.

## Manual Readiness Checklist

Before any optional future work-session recording, verify:

- User explicitly approved recording for this session.
- Recording is manual only.
- No silent recording is enabled.
- No automatic recording is enabled.
- No scheduled recording is enabled.
- No background recording is enabled.
- Microphone is OFF by default.
- No passwords are visible.
- No broker or trading account pages are visible.
- No email, bank, tax, ID, address, key, API token, recovery key, or private document is visible.
- Save location is known before recording starts.
- Privacy review is required after recording.
- Recording stops immediately if sensitive content may appear.

## Codex Session-Start Rule

Codex opening may mark `session_start_time` and may set `codex_opened=true`. Codex opening does not approve recording, screenshots, app launch, browser launch, settings changes, or telemetry automation.

## Blocked Actions

- Start recording.
- Take screenshots.
- Change Windows settings.
- Change Xbox Game Bar settings.
- Change Snipping Tool settings.
- Change startup tasks or Task Scheduler.
- Launch apps or browsers.
- Create evidence folders.
- Move, rename, delete, or cleanup videos.

## Known Unresolved Items

- OneDrive/video storage risk remains unresolved.
- Recording tool choice remains UNKNOWN.
- Privacy review process remains undefined.
- Retention/delete policy remains undefined.
- Evidence folder location is proposal only.
- Recording metadata/path belongs in telemetry later, but no telemetry migration is approved.
