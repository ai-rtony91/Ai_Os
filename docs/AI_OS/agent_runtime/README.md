# AI_OS Agent Runtime

The agent runtime is a local control layer that decides which safe work packet should happen next.

Orchestration means routing work to the right file, agent, and validator. A validator is a safety check that looks for broken rules before work is saved.

## What This Is

This folder is the first local AI_OS runtime scaffold. It uses plain files, task queues, ownership rules, validation reports, summaries, and next-action notes.

It helps AI_OS build faster because future work can be split into clear packets:

1. Read the user goal.
2. Classify the task.
3. Select the right agent.
4. Check ownership and blocked paths.
5. Queue the task.
6. Run a validator.
7. Write a compact summary.
8. Write the next safe action.
9. Wait for user approval before risky work.

## What This Is Not

This is not autonomous trading. It is not live execution. It is not a broker connection. It is not an external LLM framework install. It does not create background tasks, scheduled automation, account logins, API keys, real webhooks, or real orders.

## Why It Exists

AI_OS already has Trading Lab paper-only work, dashboard mock data, validators, reports, and product planning. This runtime gives those pieces a safer routing layer so larger builds can happen without losing the one-button-one-task discipline.

One-button-one-task means one approved work packet runs at a time, with clear allowed paths, blocked paths, expected output, and validation before the next step.

## Future Support

This runtime can support future paper-only Trading Lab work, chart panels, TradingView handoff planning, TradersPost handoff planning, validators, summaries, and business setup checklists. Those future steps still require user approval before APPLY, commit, push, install, login, or any risky action.

## Current Status

- Current status: local file-based runtime scaffold
- Live execution: BLOCKED
- External LLM install: NOT ENABLED
- Broker/OANDA/API keys/secrets: BLOCKED

