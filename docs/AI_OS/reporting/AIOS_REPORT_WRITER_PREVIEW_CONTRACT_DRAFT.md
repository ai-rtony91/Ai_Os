# AI_OS Report Writer Preview Contract Draft

## Purpose

This draft defines how future report writers may preview intended file output before APPLY mode.

Report writers must preview intended changes before any file write.

## Preview Scope

Future report-writer preview mode may show the target file, source input, proposed action, proposed fields, blocked fields, backup requirement, validator, and approval requirement.

Preview output is for human review and validator review only.

## Preview Non-Scope

No report files are written in this stage.

No report writer is activated.

No telemetry writer is activated.

No daily metrics, checkpoint index, production telemetry, broker, trading, credential, daemon, service, scheduled task, or startup automation is created.

## Required Preview Fields

Every future report-writer preview must include:

- target_file
- source_input
- proposed_action
- proposed_fields
- blocked_fields
- backup_required
- validator_to_run
- approval_required

## Allowed Report Targets

Allowed report targets may be proposed later only after separate approval.

Potential future targets may include approved health report files, approved daily report summaries, approved status summaries, or approved workflow review notes.

## Blocked Report Targets

Blocked report targets include protected root governance files, unapproved production telemetry files, trading execution logs, credential files, broker files, and any file outside the approved writer contract.

DAILY_METRICS and CHECKPOINT_INDEX remain protected.

## DRY_RUN Preview Rules

DRY_RUN preview mode must not write, overwrite, append, move, rename, delete, stage, commit, push, launch, open, change settings, access credentials, or touch broker/trading systems.

DRY_RUN preview mode must print intended output to the console or to an explicitly approved preview-only artifact in a future stage.

## APPLY Mode Requirements

APPLY mode requires a separate approval, a target file declaration, source input declaration, allowed fields, blocked fields, backup/checkpoint behavior, and validator_to_run after writing.

APPLY mode is not approved in this stage.

## Protected File Restrictions

Protected root files, `Reports\DAILY_METRICS.csv`, and `Reports\CHECKPOINT_INDEX.md` must not be edited by report writers unless separately approved.

Validators must check both unstaged and staged protected-file changes.

## Future Stage 22

Future Stage 22 may propose a console-only report-writer preview helper.

Future Stage 22 must not write real report files unless separate human approval explicitly changes scope.
