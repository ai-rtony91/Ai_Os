# OpenAI API Worker Bridge Packet Flow

Status: DRY_RUN planning artifact
Scope: packet flow design only

## Purpose

This document defines the safe flow for converting an operator goal into an inert OpenAI API Worker Bridge packet.

The packet flow is designed to reduce manual copy-paste work while preserving AI_OS approval gates.

## Required Flow

```text
goal intake
-> task graph
-> packet creation
-> worker assignment
-> repo execution
-> validator runner
-> approval inbox
-> commit package
-> clean-state verifier
```

## Step 1: Goal Intake

The bridge receives a human goal and classifies:

- objective.
- visible success condition.
- non-goals.
- allowed paths.
- forbidden paths.
- likely autonomy level.
- required validators.
- stop condition.

If any field is missing, the packet remains `deferred` or `BLOCKED`.

## Step 2: Task Graph

The bridge may split the goal into tasks only when each task has:

- one lane.
- one worker.
- one write boundary.
- one output.
- one stop point.

Tasks that involve secrets, runtime mutation, trading execution, broker access, OANDA, package installs, or protected Git actions must be isolated and blocked until future approval.

## Step 3: Packet Creation

Every bridge-drafted packet must include:

- identity marker.
- supervisor identity.
- packet ID.
- mode.
- zone.
- worker identity.
- lane.
- branch.
- worktree.
- allowed paths.
- forbidden paths.
- approval authority.
- validator chain.
- stop point.
- final report requirements.

The packet must preserve `CODEX-ONLY PROMPT` routing when intended for Codex.

## Step 4: Worker Assignment

The bridge may recommend a worker. It must not launch a worker.

Recommended assignment must identify:

- why the worker owns the lane.
- what paths the worker may read or write.
- what paths are blocked.
- whether the work is DRY_RUN, APPLY, or future proposal only.

## Step 5: Repo Execution

Repo execution remains Codex-owned or human-owned, depending on the packet.

The bridge must not execute commands, mutate files, or approve work. It may prepare inert command previews and explain expected validation.

## Step 6: Validator Runner

Validator recommendations should include:

```text
git_clean_state
allowed_paths
blocked_paths
identity_spine
json_integrity
powershell_syntax
markdown_exists
no_secrets
no_live_trading_enablement
approval_gate
commit_package_review
final_git_status
```

Validators provide evidence only. They do not approve APPLY or protected actions.

## Step 7: Approval Inbox

The bridge may prepare an approval summary for human review.

The bridge must not:

- create approval inbox records.
- update approval inbox records.
- mark records approved.
- mark records completed.
- bypass approval inbox.

APPLY remains blocked until a future exact approval exists.

## Step 8: Commit Package

The bridge may prepare a commit package preview only after files, diff, validation, and scope are known.

It must not stage, commit, push, or create PRs.

## Step 9: Clean-State Verifier

The final packet output must recommend a clean-state check.

For this DRY_RUN lane, the required final check is:

```powershell
git status --short --branch
```

## Packet Status Mapping

Use these statuses:

- `proposed`
- `queued`
- `ownership_checked`
- `blocked_path_checked`
- `ready_for_runner_preview`
- `runner_previewed`
- `ready_for_apply`
- `apply_completed`
- `validation_running`
- `validation_passed`
- `validation_failed`
- `ready_for_review`
- `done`
- `blocked`
- `deferred`

Approval status must remain separate from packet status.

## Stop Conditions

Stop and mark the packet `BLOCKED` if it requests:

- live OpenAI API calls.
- API keys or secrets.
- `.env` creation.
- package installs.
- runtime worker launch.
- approval inbox mutation.
- Night Supervisor writes.
- telemetry writes.
- control marker writes.
- broker, OANDA, live trading, webhooks, or real orders.
- commit, push, merge, stage, or PR creation without explicit approval.
