# AI_OS Writer Safety Requirements Draft

## Purpose

This draft defines writer safety requirements for DRY_RUN and future APPLY modes. This file does not activate writer behavior.

No protected root files are edited by this draft. Human approval is required before future APPLY. This draft creates no live automation and no active writer.

## Requirements

- No overwrite by default.
- Path allowlist required.
- Protected-file exclusion required.
- Backup/rollback rule before modifying existing files.
- Human approval required before APPLY.
- Validator must pass before commit.
- Source evidence required.
- Mismatch reporting required.
- No credentials/private data.
- No broker/trading execution path.
- No startup task creation.
- No hidden background services.
- No LLM placement in a live order path.

## DRY_RUN Mode

DRY_RUN mode may inspect expected paths, compare allowlists, scan boundary phrases, parse structured files, and print PASS/FAIL summaries. DRY_RUN mode must not write files unless the user has separately approved file creation for a documentation/planning batch.

## Future APPLY Mode

Future APPLY mode must require exact file scope, exact output paths, validator PASS, protected-file exclusion, rollback or backup handling, and explicit human approval before writing.

## Boundary

This draft does not grant permission to edit protected root files, create live automation, or create an active writer.
