# Agent Workflow Runner DRY_RUN Spec

The workflow runner is a future read-only preview tool.

It does not edit target work files. It does not install packages. It does not call the internet. It does not run in the background. It does not touch secrets. It does not trade. It does not connect to brokers.

## Purpose

The runner previews one task and says whether it looks safe enough for user review.

## Required Behavior

The future runner must:

1. Read `docs/AI_OS/agent_runtime/AGENT_RUNTIME_QUEUE.json`.
2. Select one task only.
3. Check the assigned agent exists in `AGENT_RUNTIME_OWNERSHIP_RULES.json`.
4. Check the major or minor agent boundary.
5. Check allowed paths.
6. Check blocked paths.
7. Check blocked words and actions.
8. Verify required input files exist when they are real paths.
9. Verify validation command exists or is explicitly planned.
10. Print or write a preview result.
11. Recommend the next safe action.

## Scope Rule

Major agents own the main lane. Minor agents can fill gaps only inside the assigned major agent scope. Minor agents cannot expand scope.

## Block Rule

Any task requesting live trading, broker execution, OANDA execution, API keys, secrets, real webhooks, real orders, external LLM installs, background execution, startup persistence, scheduled automation, account login systems, financial claims, or profitability guarantees must be blocked.

## Human Approval Rule

The runner can say a task is ready for APPLY, but it cannot approve APPLY. The human must approve before edits, commit, push, install, login, integration, or any risky action.

