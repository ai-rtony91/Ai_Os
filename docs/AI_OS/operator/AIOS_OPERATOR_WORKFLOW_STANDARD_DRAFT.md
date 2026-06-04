> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

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
