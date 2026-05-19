# AI_OS Agent Runtime Architecture

Status: canonical architecture summary
Sources: `docs/AI_OS/agent_runtime`

## Purpose

This document summarizes the AI_OS agent runtime architecture while leaving active runtime JSON fixtures in `docs/AI_OS/agent_runtime` until a separate migration is approved.

## Runtime Model

The agent runtime is a local file-based control layer for selecting safe work packets. It is not an autonomous trading system, broker connector, external LLM framework install, background service, scheduler, account login system, webhook runner, or order execution path.

Runtime flow:

```text
USER_GOAL_RECEIVED
-> TASK_CLASSIFIED
-> AGENT_SELECTED
-> OWNERSHIP_CHECKED
-> BLOCKED_PATH_CHECKED
-> TASK_QUEUED
-> VALIDATION_RUN
-> SUMMARY_WRITTEN
-> NEXT_ACTION_WRITTEN
-> USER_APPROVAL_REQUIRED
```

## Active Runtime Fixtures

The following remain active in `docs/AI_OS/agent_runtime` until a future fixture migration is designed and validated:

- queue JSON.
- status JSON.
- ownership rules JSON.
- gap log JSON.
- task schema JSON.
- workflow lifecycle JSON.
- blocked actions matrix JSON.
- handoff packet schema JSON.

Dashboard mock data and `automation/agent_runtime` validators still reference these paths.

## Task State Boundary

Tasks may move through proposed, queued, ownership checked, blocked path checked, runner previewed, validation passed/failed, ready for review, done, blocked, or deferred states.

Any task requesting live trading, broker execution, OANDA execution, API keys, secrets, real webhooks, real orders, external LLM install, background execution, startup persistence, scheduled automation, account login systems, financial claims, or profitability guarantees must be blocked.

Unclear tasks must move to deferred or ready for review, not APPLY.

## Worker Boundary

Future LLM workers may read local task files and write local output files only after approval. They must stay within allowed paths, respect blocked paths, wait for validation, and wait for user approval before APPLY, commit, or push.

Workers cannot directly trade, access secrets, bypass validators, connect brokers, or place orders.

## Approval And Validation

Every work packet should declare:

- assigned agent.
- allowed paths.
- blocked paths.
- required inputs.
- expected outputs.
- validation command.
- safety status.
- next safe action.
- user approval requirement.

The runtime does not run in the background, schedule jobs, start on boot, call external LLMs, or bypass human approval.

