# AI_OS Operator Workflows

Status: canonical summary extracted from legacy `docs/AI_OS`

## Purpose

This document summarizes operator workflow doctrine from legacy `docs/AI_OS/operator`, `operator_workflows`, orchestration, governance, and cleanup reports. It does not authorize automation, commits, pushes, or worker launches.

## Current Doctrine

MAIN CONTROL owns architecture direction, clean-state validation, PR review, merge decisions, conflict resolution, branch protection, worker boundaries, and AI_OS doctrine.

The operating loop is:

1. Inspect current state.
2. Produce DRY_RUN or bounded plan.
3. Get human approval before APPLY.
4. Make exact scoped changes.
5. Validate.
6. Report files changed, validation, commit status, push status, and next safe action.
7. Commit or push only after explicit approval.

## MAIN CONTROL Workflow

MAIN CONTROL should:

- keep `main` protected,
- require clean-state checks before changes,
- prevent overlapping worker file ownership,
- approve architecture direction,
- review PRs before merge,
- preserve human authority for protected actions.

MAIN CONTROL should not:

- allow uncontrolled scope drift,
- merge without validation,
- bypass clean-state checks,
- let workers touch the same files simultaneously.

## Codex Lane Workflow

Codex is the repo implementer. Codex may edit files only when the prompt gives exact scope and mode.

Rules:

- DRY_RUN means plan/report only unless explicit APPLY is approved.
- APPLY means edit only approved paths.
- Never use `git add .`.
- Never commit or push unless explicitly asked.
- Never touch secrets, live broker paths, OANDA, real webhooks, or live trading.
- Validate JSON, PowerShell, and whitespace when relevant.

## Claude Review/Audit Workflow

Claude is treated as an isolated specialist worker, not a standing authority.

Recommended use:

- bounded read-only audits,
- architecture review,
- dependency mapping,
- validation interpretation,
- compliance or approval-gap checks.

Claude tasks require a delegation packet with role, mode, scope, blocked actions, return format, stop point, and approval state.

## Clean-State, Commit, and No-Push Rules

Before work:

- run `git status --short --branch`,
- verify branch,
- inspect relevant files,
- identify dirty state before editing.

After work:

- run `git diff --check` when files changed,
- run targeted validators,
- show `git status --short`,
- report commit status and push status.

Commit and push are separate protected actions. They require explicit operator approval.

## Worktree Isolation Doctrine

Parallel work is allowed only when file ownership is separated.

Rules:

- one APPLY lane at a time for overlapping files,
- no simultaneous edits to the same file,
- workers need allowed paths and blocked paths,
- stale worker or lock evidence must be reviewed before resuming,
- conflict or unknown state stops the workflow.

## Planned/Future Ideas

- More structured work packets.
- Safer operator loop runner.
- Better dashboard visibility into packets, validators, approvals, and clean-state.
- Optional specialist worker lanes once boundaries are stable.

## Human-Review Items

- Decide canonical names for worker lanes.
- Decide how much of the operator loop belongs in scripts versus manual prompts.
- Review any workflow that implies automated commit, push, merge, deployment, or worker launch.
