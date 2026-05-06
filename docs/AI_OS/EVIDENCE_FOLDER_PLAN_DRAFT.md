# AI_OS Evidence Folder Plan Draft

## Purpose

This draft explains the proposed evidence folder and future telemetry path reference without creating folders. It does not approve recording, screenshots, folder creation, video movement, telemetry migration, or automation.

## Proposed Future Evidence Folder

Future proposal only:

```text
Reports\evidence\screen-recordings
```

This folder must not be created until a separate create-only APPLY approval is granted.

## Proposed Future Recording Filename

Future proposal only:

```text
AIOS_WORKSESSION_YYYY-MM-DD_STAGE_LABEL.mp4
```

Example format only:

```text
AIOS_WORKSESSION_2026-05-07_STAGE6B_READINESS.mp4
```

## Future Telemetry Reference

If recording is separately approved later, telemetry may reference:

- `screen_recording_used`
- `screen_recording_path`
- `privacy_review_required`
- `session_start_time`
- `codex_opened`

Recording metadata/path belongs in telemetry later, but no telemetry migration is approved by this draft.

## Storage And Privacy Notes

- Recording files are evidence.
- Evidence may contain sensitive data and must be reviewed before sharing.
- OneDrive/video storage risk remains unresolved.
- Retention/delete policy remains undefined.
- Privacy review process remains undefined.

## Blocked Actions

- Creating `Reports\evidence\screen-recordings`.
- Starting recording.
- Taking screenshots.
- Moving or renaming videos.
- Editing telemetry files.
- Changing Windows, Xbox Game Bar, Snipping Tool, startup, or Task Scheduler settings.
