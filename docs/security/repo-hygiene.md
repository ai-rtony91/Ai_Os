# Repository Hygiene Policy

Status: baseline scaffold, pending human review.

## Purpose

Keep AI_OS clean, reviewable, and safe for public repository exposure.

## Canonical Source Areas

The following are primary source-of-truth areas:

- automation/
- aios/
- apps/
- services/
- docs/

## Generated or Runtime Areas

The following may contain generated or runtime material and require review before long-term tracking:

- Reports/
- runtime/
- dispatcher/runtime/
- work_packets/
- approval queues
- generated status snapshots

## Duplicate File Review

Duplicate filenames are not automatically wrong.

Normal duplicates may include:

- README.md
- package.json
- package-lock.json
- .gitignore

Risky duplicates include:

- launcher scripts
- approval inbox examples
- packet queue examples
- generated status files
- copied governance docs
- old bootstrap wrappers

## Cleanup Rules

- Do not mass-delete.
- Identify canonical owner before removal.
- Prefer moving generated outputs to ignored runtime locations.
- Preserve audit/proof artifacts until retention policy is approved.
- Do not delete orchestration state structures without lifecycle documentation.
