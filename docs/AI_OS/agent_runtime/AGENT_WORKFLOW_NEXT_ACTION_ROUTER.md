# Agent Workflow Next Action Router

The next-action router is a plain rule file. It tells AI_OS what kind of next step is allowed after a task state changes.

## Router Rules

- `proposed`: Review the task fields.
- `queued`: Check ownership.
- `ownership_checked`: Check blocked paths.
- `blocked_path_checked`: Prepare read-only runner preview.
- `ready_for_runner_preview`: Run preview only.
- `runner_previewed`: Ask user for APPLY approval if edits are needed.
- `ready_for_apply`: Wait for explicit user approval.
- `apply_completed`: Run validation.
- `validation_running`: Wait for validator result.
- `validation_passed`: Write summary and prepare user review.
- `validation_failed`: Stop and report failures.
- `ready_for_review`: Ask user to review files and status.
- `done`: Choose the next queued task.
- `blocked`: Do not continue until user changes the task.
- `deferred`: Clarify scope before APPLY.

## Safe Next Action Types

Allowed next actions:

- exact PowerShell validation command
- exact Codex DRY_RUN prompt
- exact Codex APPLY prompt after user approval
- exact review instruction
- exact checkpoint instruction

Blocked next actions:

- install packages
- call internet
- start background tasks
- create scheduled automation
- add startup persistence
- connect accounts
- add API keys or secrets
- connect brokers
- place trades
- make financial claims

