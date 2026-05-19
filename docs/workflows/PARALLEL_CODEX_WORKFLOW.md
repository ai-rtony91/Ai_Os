# AI_OS Parallel Codex Workflow

Status: canonical workflow
Source: `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md`

## Purpose

This workflow defines supervised parallel DRY_RUN lanes and a controlled serial APPLY lane. It is an operator pattern, not permission to launch workers, commit, push, merge, or run live systems.

## Lane Model

- DRY_RUN workers may inspect and plan in parallel when their scopes do not overlap.
- APPLY work must be serialized for overlapping files.
- Each lane must declare allowed paths, blocked paths, expected report path, validation commands, and stop condition.
- The integration lane reviews reports before any APPLY, commit, push, or merge decision.

## Worker Report Contract

Worker reports should include:

- worker ID and label.
- mode.
- planned files.
- files changed, if APPLY was approved.
- files deleted, expected to be empty.
- validation commands.
- blockers.
- next safe action.

## Safety Rules

- No protected root file edits without approval.
- No secrets.
- No broker, OANDA, webhook, real order, or live trading work.
- No overlapping planned file edits.
- No commit or push from worker scripts.
- No package install or external service connection unless separately approved.

## Validation

Before integration:

- Validate worker reports.
- Check for overlapping planned files.
- Run targeted validators.
- Run `git diff --check`.
- Run `git status --short --branch`.

