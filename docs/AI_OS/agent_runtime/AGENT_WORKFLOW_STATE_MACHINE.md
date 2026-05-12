# Agent Workflow State Machine

This file explains the local AI_OS workflow states in plain English.

The workflow is local and file-based only. It does not run in the background, install external LLM frameworks, connect to brokers, use API keys, call the internet, place orders, or use live market data.

## Workflow

user goal
-> intake packet
-> task classification
-> ownership check
-> blocked path check
-> task queue
-> runner preview
-> validator selection
-> output summary
-> next action
-> human approval

## Beginner Rule

The runner previews what would happen.

The validator checks if rules are broken.

The human approves before APPLY, commit, push, installs, integrations, or risky actions.

## States

- `proposed`: A task idea exists, but it is not ready to run.
- `queued`: The task has enough fields to enter the queue.
- `ownership_checked`: The assigned agent is allowed to own this lane.
- `blocked_path_checked`: The task paths were checked against blocked paths.
- `ready_for_runner_preview`: The task is safe enough for a read-only preview.
- `runner_previewed`: A read-only preview has been produced.
- `ready_for_apply`: The task is ready for user approval before APPLY.
- `apply_completed`: Approved file changes were made.
- `validation_running`: A validator is running or should run next.
- `validation_passed`: The validator passed.
- `validation_failed`: The validator failed.
- `ready_for_review`: The user should review the result.
- `done`: The task is complete.
- `blocked`: The task requested a blocked action.
- `deferred`: The task is unclear or should wait.

## Transitions

- `proposed -> queued` only after the task has required fields.
- `queued -> ownership_checked` only if the assigned agent exists.
- `ownership_checked -> blocked_path_checked` only if the agent owns the lane.
- `blocked_path_checked -> ready_for_runner_preview` only if no blocked path appears.
- `ready_for_runner_preview -> runner_previewed` after read-only preview.
- `runner_previewed -> ready_for_apply` only if user approval is required and pending.
- `ready_for_apply -> apply_completed` only after approved APPLY.
- `apply_completed -> validation_running -> validation_passed` when validation passes.
- `apply_completed -> validation_running -> validation_failed` when validation fails.
- `validation_passed -> ready_for_review -> done` after user review.
- Any unsafe request moves to `blocked`.
- Any unclear request moves to `deferred` or `ready_for_review`.

## Safety Lock

Live trading, broker execution, OANDA execution, API keys, secrets, real webhooks, real orders, external LLM installs, background execution, startup persistence, scheduled automation, account login systems, financial claims, and profitability guarantees remain blocked.

