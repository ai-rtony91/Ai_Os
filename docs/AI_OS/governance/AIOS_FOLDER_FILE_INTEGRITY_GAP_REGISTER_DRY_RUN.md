> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Folder File Integrity Gap Register DRY_RUN

## Purpose

This DRY_RUN records folder/file integrity gaps that could cause future agents to write files into the wrong place.

## Missing README_FOLDER_PURPOSE Coverage

Many folders do not have `README_FOLDER_PURPOSE.txt`, including:

- `agent/runtime`
- `apps/dashboard`
- `apps/dashboard/css`
- `apps/dashboard/icons`
- `apps/dashboard/js`
- `apps/dashboard/mock-data`
- `apps/dashboard/public`
- `apps/dashboard/skeleton`
- `apps/dashboard/src`
- `apps/dashboard/src/assets`
- most `automation/*` subfolders
- most `docs/AI_OS/*` subfolders
- `docs/specs`
- `internal/source-artifacts/*`
- `Reports/checkpoints`
- `Reports/daily`
- `services/orchestrator`

Risk: agents may infer ownership incorrectly.

Next safe action: README_FOLDER_PURPOSE coverage batch only.

## Duplicate / Timestamped Draft Variants

Observed timestamped variants include:

- roadmap DRY_RUN/APPLY variants
- mobile dashboard readiness variants
- PWA app-store boundary variants
- sidebar requirement variants
- OANDA boundary variants
- OANDA no-live-execution variants
- OANDA sandbox requirement variants
- broker adapter interface variants

Risk: source-of-truth ambiguity.

Next safe action: duplicate/timestamped doc review only.

## Stale References

README references missing root folders:

- `plugins/`
- `scripts/`
- `tests/`

AGENTS references missing paths:

- root `White_Paper.md`
- `tools/python/create_folder_purpose_notes.py`
- `tools/powershell/RUN_FOLDER_NOTE_AUTOMATION.ps1`
- `docs/AI_OS/system_wizards/AI_OS_FOLDER_NOTE_AUTOMATION_SPEC.txt`

Risk: agents may create or edit wrong paths.

Next safe action: protected README/AGENTS mismatch proposal only.

## Protected File Reference Mismatch

AGENTS protects `White_Paper.md`, but root `White_Paper.md` was not found. Root `WHITEPAPER.md` and `docs/White_Paper.md` exist.

Risk: protected-file rules may be applied to the wrong file path.

Next safe action: proposal-only report; do not edit protected files.

## Empty Folder Tracking Risk

Git does not track empty folders. Future empty placeholder folders need either approved purpose files or tracked content.

Risk: planned folder structure may disappear from commits.

Next safe action: README_FOLDER_PURPOSE coverage only.

## Source-Of-Truth Ambiguity

Generated Reports and canonical docs can both contain audit/roadmap content.

Rule:

- `docs/AI_OS/` owns canonical planning.
- `Reports/` owns generated outputs.

Next safe action: governance index docs only.

## DRY_RUN Result

PASS with REVIEW items. This gap register does not approve edits, moves, deletes, renames, overwrites, or implementation.
