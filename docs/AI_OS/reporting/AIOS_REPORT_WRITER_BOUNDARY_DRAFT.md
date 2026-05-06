# AI_OS Report Writer Boundary Draft

## Purpose

This draft explains the difference between console-output DRY_RUN helpers and future file-writing report helpers.

## Current Reporting State

Current Stage 14 work remains console-output-focused and boundary-focused. It does not create a real report writer and does not write report files.

## DRY_RUN Console Output

DRY_RUN console-output helpers may print status, proposed rows, proposed snapshots, validation results, warnings, failures, and next safe actions. Console output is evidence for review but is not persistent history unless later saved by an approved reporting helper.

## Future File-Writing Reports

Future file-writing report helpers may write reports only after separate approval. The approval must define exact paths, file naming rules, backup/checkpoint expectations, sensitive data exclusions, and verification steps.

## Approval Requirements

File-writing report helpers require human approval before APPLY. Git staging, commits, and pushes require separate human approval.

## Protected Report Files

Protected report files and report indexes must not be edited without separate approval. Historical reports should be preserved as evidence unless a later approved policy says otherwise.

## Daily Metrics Boundary

`Reports\DAILY_METRICS.csv` must not be edited without separate approval.

Any future daily metrics writer needs a backup/checkpoint rule, a schema check, and a DRY_RUN preview before writing.

## Checkpoint Index Boundary

`Reports\CHECKPOINT_INDEX.md` must not be edited without separate approval.

Any future checkpoint index writer needs a backup/checkpoint rule, a duplicate-entry check, and a DRY_RUN preview before writing.

## Non-Scope

This boundary does not approve report writing, snapshot writing, dashboard UI creation, broker or trading actions, credential handling, startup changes, scheduled tasks, app launch, browser opening, or git checkpoint commands.

Report writing must never include secrets, credentials, broker tokens, private keys, or recovery keys.

## Future Stage 15

Future Stage 15 may propose a DRY_RUN report-writer design or report output contract. It must not edit protected report files without separate approval.
