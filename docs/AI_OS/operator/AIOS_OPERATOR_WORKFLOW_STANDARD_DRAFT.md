# AIOS Operator Workflow Standard Draft

Status: Draft planning doc

## Purpose

Plan a simplified operator workflow for non-technical use.

## Workflow

1. Open Codex in the AI_OS repo.
2. Run the workload prompt.
3. Read the DRY_RUN report.
4. Approve APPLY only when the report is correct.
5. Run validation.
6. Commit and push after approval.
7. Verify clean Git status.

## Stop Conditions

- unknown repo path
- dirty worktree outside approved scope
- protected action without approval
- secrets or broker paths detected
- live trading path detected

## Boundary

This is a workflow draft and not a protected root governance edit.
