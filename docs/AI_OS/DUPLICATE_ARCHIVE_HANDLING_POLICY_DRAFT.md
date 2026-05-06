# AI_OS Duplicate And Archive Handling Policy Draft

## Purpose

This draft defines duplicate and archive decision rules only. It does not approve file cleanup, movement, deletion, renaming, overwrite, archive migration, or protected-file edits.

## Duplicate Decision Criteria

Before classifying a file as a duplicate, collect and compare:

- Exact path.
- File name.
- File extension.
- File size.
- Created date if available.
- Modified date if available.
- Git tracked status.
- Content purpose.
- Whether a newer replacement exists.
- Whether reports or docs reference it.
- Whether it is historical evidence.
- Whether it contains secrets, credentials, broker information, private data, or personal data.
- Whether it belongs in active repo, `Reports`, `inputs`, `internal`, `docs`, `automation`, `services`, `apps`, or hold/archive.

## Duplicate Handling Rules

- Similar names do not prove duplication.
- Newer modified date does not prove replacement.
- Smaller file size does not prove a file is obsolete.
- Generated output must not replace source-of-truth material without review.
- Historical evidence must be preserved unless a separate archive policy is approved.
- Referenced files require human review before any structural decision.
- Files with possible secrets or private data require immediate protected handling and must not be copied into reports.

## Archive Candidate Rules

A file may be marked `ARCHIVE_CANDIDATE_LATER` only when:

- Its active purpose is no longer clear or no longer current.
- A newer replacement appears to exist.
- References and historical evidence value have been reviewed.
- No secret/private-data issue blocks handling.
- Human review is still required before any archive action.

## Blocked Actions

The following actions are not approved by this draft:

- Delete.
- Move.
- Rename.
- Overwrite.
- Cleanup.
- Archive migration.
- Protected-file edit.
- Automatic duplicate merge.
- Staging, commit, or push.

## Known Unresolved Items

- `AIOS_WorkOrder_Stages28_to_31_CodexPrep_ReportOnly_v1.ps1` remains INVALID_DATA / UNKNOWN.
- White paper source-of-truth remains unresolved.
- Archive retention policy remains undefined.
- Secret/private-data detection policy is not implemented.
