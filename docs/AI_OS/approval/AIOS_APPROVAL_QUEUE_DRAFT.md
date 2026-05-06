# AI_OS Approval Queue Draft

## Purpose

This draft explains how future AI_OS systems may present pending approvals before APPLY actions occur.

## Queue Scope

The approval queue is a read-only visibility concept at this stage. It can describe pending review items, risk levels, blocked action types, and the human approval required before any action.

## Queue Non-Scope

No autonomous approvals exist.

No trading or broker approvals exist.

Queue visibility is read-only at this stage.

The queue does not execute APPLY, git checkpoint, app launch, browser open, startup change, settings change, credential handling, broker action, trading action, or report writing.

## Approval Categories

Conceptual approval categories:

- `DRY_RUN_REVIEW`
- `APPLY_PENDING`
- `GIT_CHECKPOINT_PENDING`
- `PROTECTED_FILE_REVIEW`
- `BLOCKED_HIGH_RISK`

## Approval Priority Concepts

Lower-risk review items can be shown below blocking items. High-risk and blocked items should be displayed prominently and require explicit human review.

## Protected File Approval Rules

Protected root files, protected reports, metrics files, checkpoint indexes, credentials, and evidence files require separate review before any edit, overwrite, movement, rename, deletion, staging, commit, or push.

## Git Checkpoint Approval Rules

`git add`, `git commit`, and `git push` are separate human-approved actions. They should never be triggered by queue visibility alone.

## Risk Escalation Concepts

Conceptual risk levels:

- `LOW`
- `MEDIUM`
- `HIGH`
- `BLOCKED`

HIGH and BLOCKED require explicit human review.

## Dashboard Visibility Concepts

Future dashboards may show pending approvals by category, risk level, workflow, file scope, and next safe action. Dashboard visibility must not become an execution queue without separate approval.

## Future Stage 12D

Future Stage 12D may define a read-only approval queue data contract or validation helper. It must remain DRY_RUN-first and must not execute approvals.
