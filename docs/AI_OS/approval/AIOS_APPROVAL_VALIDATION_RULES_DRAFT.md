# AI_OS Approval Validation Rules Draft

## Purpose

This draft explains how future AI_OS systems may validate approval-state consistency before APPLY actions occur.

## Validation Scope

Approval validation may check whether required approval documents, workflow registry entries, router mappings, dashboard fields, and approval-state helpers exist and agree with each other.

## Validation Non-Scope

Validators remain DRY_RUN only.

Validators do not approve APPLY.

Validators do not touch trading or broker systems.

Validators do not stage, commit, push, launch apps, open browsers, change startup settings, create scheduled tasks, edit protected files, or write reports.

## Approval Validation Rules

Validation should confirm:

- The approval queue component exists.
- The workflow registry exists.
- The workflow router exists.
- The dashboard data contract exists.
- Workflow names are registered before use.
- Workflow state values are valid.
- Approval categories are known.

## Risk Escalation Rules

LOW risk means read-only DRY_RUN console-output.

MEDIUM risk means creates approved files but no git commit.

HIGH risk requires explicit human review.

BLOCKED risk means no action is allowed until explicit human review resolves the block.

## Protected File Rules

Unexpected protected file modification is a validation failure. Protected files include root policy/source files, `Reports\DAILY_METRICS.csv`, and `Reports\CHECKPOINT_INDEX.md`.

## Git Checkpoint Rules

`git add`, `git commit`, and `git push` require separate human approval and must never be triggered by validation.

## FAIL Conditions

Conceptual FAIL conditions:

- missing approval queue component
- protected files modified unexpectedly
- workflow not registered
- invalid workflow state
- blocked risk level detected

## WARN Conditions

Conceptual WARN conditions:

- git status not clean
- missing optional dashboard field
- stale snapshot state

## Human Review Requirements

Human review is required before APPLY, report writing, protected file editing, git checkpointing, app launching, browser opening, startup changes, settings changes, credential handling, broker action, trading action, or live execution.

## Future Stage 13

Future Stage 13 may add deeper DRY_RUN validation for snapshot contracts, dashboard bindings, or approval queue data fields. It must not execute approvals.
