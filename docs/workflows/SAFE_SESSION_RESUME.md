# AI_OS Safe Session Resume

Status: canonical workflow
Source material: `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md`

`docs/AI_OS/**` is reference/source material only. Current workflow authority lives in `docs/workflows/` unless a specific rule is promoted through governance.

## Purpose

Safe session resume restores context after a pause, crash, restart, or new chat. It restores state for review only; it does not resume execution.

## Resume Evidence

A resume packet should show:

- last completed phase.
- current in-progress phase.
- active workers.
- unresolved conflicts.
- stale workers.
- uncommitted files.
- last known git status.
- pending approvals.
- next safe action.

## Restore Rules

AI_OS may restore context, worker state, conflict state, pending approvals, validator position, and next safe action.

AI_OS must not restore active execution, autonomous APPLY, automatic commit, automatic push, merge execution, background worker state, broker execution, OANDA, API key handling, or live trading.

## Stale Or Invalid State

If evidence is old, missing, or unverifiable, mark it `STALE` or `UNKNOWN` and block promotion.

If resume evidence conflicts with the current repo, mark it `INVALID DATA` and stop until reviewed.

