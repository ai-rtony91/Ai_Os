# AI_OS Protected File Approval Rules Draft

## Purpose

This draft defines protected-file approval requirements only. It does not approve edits to protected files.

## Protected File Rule

Protected files must not be edited, moved, renamed, deleted, overwritten, reformatted, staged, committed, or pushed without separate human approval and a backup/checkpoint.

## Approval Requirements

Before any protected-file APPLY action, require:

- Exact file path.
- Reason for the proposed change.
- Current Git status.
- Backup/checkpoint plan.
- Confirmation that the file does not contain secrets, credentials, broker information, private data, or personal data requiring special handling.
- Human approval naming the exact protected file.
- Clear stop condition.
- Final report after APPLY.

## Blocked Without Separate Approval

- Editing protected root files.
- Overwriting protected files.
- Moving protected files.
- Renaming protected files.
- Deleting protected files.
- Auto-formatting protected files.
- Resolving source-of-truth conflicts without review.
- Migrating report metrics or archive material.
- Implementing secret/private-data scanning automation.

## Protected Review Outcomes

Allowed planning outcomes:

- `PROTECTED_SOURCE_OF_TRUTH`
- `HUMAN_REVIEW_REQUIRED`
- `INVALID_DATA`
- `UNKNOWN`

No protected-file classification grants permission to edit the file.

## Known Unresolved Items

- White paper source-of-truth remains unresolved.
- `progress_percent` formula remains undefined.
- Secret/private-data detection policy is not implemented.
