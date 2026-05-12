# Agent Runtime Control Model

Runtime means a local control layer that decides which safe work packet should happen next.

Orchestration means routing work to the right file, agent, and validator.

A validator is a safety check that looks for broken rules before work is saved.

## Runtime Flow

USER_GOAL_RECEIVED
-> TASK_CLASSIFIED
-> AGENT_SELECTED
-> OWNERSHIP_CHECKED
-> TASK_QUEUED
-> AGENT_OUTPUT_EXPECTED
-> VALIDATION_RUN
-> SUMMARY_WRITTEN
-> NEXT_ACTION_WRITTEN
-> USER_APPROVAL_REQUIRED

## Task Classification

Task classification means deciding what kind of work the user is asking for. Examples include docs, dashboard fixture, validator, paper backend plan, business checklist, or integration boundary.

## Ownership Check

Ownership check means confirming the assigned agent owns the kind of work being requested. If the agent does not own it, the task should be reassigned or blocked for review.

## Blocked Path Check

Blocked path check means confirming the task does not edit protected files, secret files, broker files, live execution files, dashboard code outside approval, or unrelated folders.

## Validation Required

Every task should name the validation it needs. A validator can check JSON parsing, blocked terms, missing files, unsafe statuses, or other local safety rules.

## Summary Compression

Summary compression means writing a short report that says what changed, what is blocked, what validation ran, and what the next safe action is. It should be short enough for the next Codex or ChatGPT step to reuse.

## Next-Action Rule

Every completed task must write one direct next action. The next action should be a safe PowerShell command, a Codex prompt, a review instruction, or a checkpoint instruction.

## No Background Autonomy

The runtime does not run in the background. It does not schedule jobs. It does not start on boot. It does not call external LLMs. It waits for the user to approve the next task.

