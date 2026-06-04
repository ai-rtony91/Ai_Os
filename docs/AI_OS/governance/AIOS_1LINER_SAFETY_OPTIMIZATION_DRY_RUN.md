> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS 1Liner Safety Optimization DRY_RUN

## Purpose

This DRY_RUN defines safety standards for future large Codex 1Liner prompts.

## Required 1Liner Structure

Every large prompt should include:

- `TASK:`
- `MODE:`
- approved output paths
- blocked output paths
- protected-file rules
- overwrite rules
- duplicate detection rules
- batch sequence
- stop conditions
- verification requirements
- final report requirements

## MODE Line

Allowed mode labels:

- `DRY_RUN ONLY`
- `APPLY BATCH [name] ONLY`
- `SEQUENTIAL APPLY BATCHES [range] ONLY`

If mode is missing, default to DRY_RUN and write a proposal report only.

## Approved Output Paths

Every APPLY prompt must list exact approved folders. If a file target is not under an approved folder, block it.

## Blocked Output Paths

Default blocked paths:

- protected root files unless explicitly approved
- `.env` and environment files
- `apps/dashboard/` during docs-only work
- `services/` during docs-only work
- `automation/` during docs-only work
- broker/OANDA implementation paths
- GitHub workflow paths unless explicitly approved

## Protected-File Rules

Protected root files require:

- explicit approval
- backup plan
- exact target file list
- DRY_RUN report first
- final verification

## Overwrite Rules

- Do not overwrite existing files.
- If a target exists, create a timestamped variant only when the prompt explicitly allows variants.
- If variants are not allowed, stop and report.

## Duplicate Detection Rules

Before APPLY:

- check target file existence
- scan sibling folder for similar names
- identify timestamped variants
- report duplicate risks

## Git Status Requirements

Run `git status --short`:

- before APPLY
- after each batch
- in final report

Do not stage, commit, or push unless explicitly approved.

## Verification Requirements

After each batch:

- verify created files exist
- verify files are inside approved paths
- verify protected roots unchanged
- verify no code paths changed during docs-only work
- print batch result

## Fail-Closed Conditions

Stop if:

- folder ownership is unclear
- output path is ambiguous
- target exists and overwrite would be required
- protected file edit is required
- secrets/API/broker data are requested
- code is requested in planning folder
- docs are requested in automation folder
- Git action is requested without approval

## Staged Batch Design

Safe batch design:

- one folder family per batch
- one document family per batch
- verification after each batch
- continue only if prior batch has no errors

## Maximum Safe APPLY Scope

Maximum safe docs-only APPLY scope:

- one governance family
- one dashboard planning family
- one telemetry schema family
- one generated report family

Larger scopes should be split.

## Mandatory Final Report Fields

- Task
- Files inspected
- Folders inspected
- Files created
- Files changed
- Errors
- Unknowns
- Protected action involved: YES/NO
- Approval required before next step: YES/NO
- `git status --short`
- Next safe action

## DRY_RUN Result

These are proposed 1Liner standards only. No protected files or code were edited.
