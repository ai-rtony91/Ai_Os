# Cleanup Session Checkpoint

## Status

Main was clean and synced before this checkpoint.

## Completed

- Archived dashboard docs.
- Archived dispatcher docs.
- Archived orchestration docs.
- Archived writers docs.
- Archived bootstrap_engine docs.
- Classified automation/orchestration cleanup candidates.
- Removed local AIOS_WORKERS clutter from active workspace.

## Current Counts

- docs/AI_OS: 460
- archive/docs_aios_legacy: 310

## Active docs/AI_OS reduction

- Started: 735
- Current: 460
- Moved out of active docs: 275

## Remaining Active docs/AI_OS Top Areas

- agent_runtime: 24
- operator: 23
- telemetry: 23
- governance: 22
- security: 21
- autonomous: 17
- audits: 14
- roadmap: 13

## Next Safe Candidates

- autonomous
- roadmap
- audits

## Avoid Broad Cleanup

Do not touch governance, security, operator, telemetry, or agent_runtime without a dedicated scan and preservation pass.

## Rule Going Forward

Use one target at a time:

scan -> extract -> repoint -> archive -> validate -> commit -> PR -> sync

## Stop Rule

Do not start another folder cleanup unless:

- main is clean
- one target is selected
- active references are scanned first
- old drafts are replaced by canonical docs before archive
