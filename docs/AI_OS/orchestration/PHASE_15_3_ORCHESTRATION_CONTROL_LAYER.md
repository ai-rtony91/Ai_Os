# Phase 15.3 Orchestration Control Layer

## Purpose

Phase 15.3 creates the first automation-ready control layer for AI_OS worker coordination.

The layer organizes packets, locks, approvals, validators, commit packages, recovery notes, and status snapshots so multiple Codex workers can operate without file collisions or blind commits.

## Why This Exists

AI_OS needs a simple operator-controlled structure before any deeper automation. The structure must keep work visible, bounded, and reversible.

## Short-Term Automation Goal

The short-term goal is to make worker assignments readable and reviewable:

- one worker packet
- one owner
- exact allowed paths
- exact blocked paths
- explicit approval before APPLY
- validators before commit packaging

## Long-Term Automation Goal

The long-term goal is safe orchestration that can support more workers, better telemetry, stronger validators, and cleaner recovery without enabling unsafe execution.

## Worker Flow

1. Create or review a worker packet.
2. Confirm allowed and blocked paths.
3. Claim one packet for one worker.
4. Run DRY_RUN first.
5. Request approval before APPLY.
6. Validate outputs.
7. Package exact files for commit review.

## Approval Flow

Approval is required before APPLY, lock override, recovery resume, staging, commit, or push.

Approval must name the requested action, packet ID, risk level, and exact paths.

## Validator Flow

Validators check clean state, allowed paths, blocked paths, JSON parsing, Markdown presence, secret safety, broker and live trading blocks, commit package readiness, and final git status.

Validators report. They do not edit, stage, commit, push, approve, or resume work.

## Commit Flow

Commit packages must list exact files to stage and exact files not to stage.

The required strategy is `explicit_files_only`.

`git add .` is blocked.

## Recovery Flow

Recovery starts with reading state. If the state is unclear, mark it `REVIEW_REQUIRED`.

Do not automatically resume APPLY, release locks, reassign packets, stage files, commit, push, merge, or rebase.

## Blocked Actions

- live trading
- broker connections
- OANDA connections
- API key collection
- secrets
- real webhooks
- real orders
- startup tasks
- scheduled tasks
- external network calls
- blind commits
- push without approval
- edits outside approved paths

## Next Phases

Next phases should connect this control layer to read-only validators, operator check summaries, packet assignment reports, and clean-state verification.

Next safe action: validate this scaffold and keep commit approval separate.
