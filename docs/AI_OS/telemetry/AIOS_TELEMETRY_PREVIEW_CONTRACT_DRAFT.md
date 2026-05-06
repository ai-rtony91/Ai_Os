# AI_OS Telemetry Preview Contract Draft

## Purpose

This draft defines how future telemetry writers may preview telemetry output safely before any telemetry persistence exists.

Telemetry persistence requires separate approval.

## Preview Scope

Telemetry preview may print proposed fields, blocked fields, approval requirement, retention concept, and validator to run after a future write.

The preview is console-output-only in this stage.

## Preview Non-Scope

No telemetry file is written in this stage.

No production telemetry collector is created.

No service, daemon, agent, scheduled task, startup automation, broker integration, trading execution, webhook execution, or credential access is created.

## Allowed Preview Fields

Allowed telemetry preview fields:

- timestamp
- workflow_name
- workflow_state
- dashboard_state
- approval_state
- morning_brief_state
- report_boundary_state
- snapshot_boundary_state
- protected_files_changed
- telemetry_mode
- production_ready

## Blocked Fields

Blocked fields:

- secrets
- credentials
- broker tokens
- private keys
- recovery keys
- live trading data
- uncontrolled screen contents

## DRY_RUN Rules

DRY_RUN mode must remain console-output-only.

DRY_RUN mode must not create, edit, move, rename, delete, stage, commit, push, launch apps, open browsers, change settings, access secrets, write telemetry, write reports, or touch broker/trading systems.

## APPLY Requirements

APPLY mode is not approved in this stage.

Future APPLY telemetry writing requires a target file, source input, allowed fields, blocked fields, backup/checkpoint behavior, retention rule, validator, and separate human approval.

Telemetry persistence requires separate approval.

## Retention Concepts

Future telemetry retention may define target path, rotation, retention days, archival boundary, protected-file checks, and deletion rules.

Retention rules are conceptual only in this stage.

## Protected File Restrictions

Telemetry preview must not edit protected root files, `Reports\DAILY_METRICS.csv`, or `Reports\CHECKPOINT_INDEX.md`.

Validators must check both unstaged and staged protected-file changes.

## Future Stage 24

Future Stage 24 may propose a telemetry preview schema validator or a stricter retention draft.

Future Stage 24 must not write telemetry files unless separate human approval explicitly changes scope.
