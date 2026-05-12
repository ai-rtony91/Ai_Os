# Readme For Non-Technical Operator

This folder helps AI_OS decide what safe work packet should happen next.

## What To Open First

Open `AGENT_RUNTIME_NEXT_ACTION.md` first. It tells you the next safe step.

## Queue Files

Open `AGENT_RUNTIME_QUEUE.json` to see the list of work packets.

A work packet says:

- What the task is
- Which agent owns it
- Which files it may touch
- Which files it must not touch
- What safety check should run
- What the next action is

## Safety Check Files

Open `AGENT_RUNTIME_VALIDATION_REPORT.json` to see validation status.

The validator script is:

`automation/agent_runtime/Test-AiOsAgentRuntimeReadiness.DRY_RUN.ps1`

It is read-only. It checks files and prints PASS or FAIL.

## What Should Never Be Clicked Or Rushed

Do not rush:

- Live trading
- Broker connection
- OANDA connection
- API keys
- Secrets
- Real webhooks
- Real orders
- User login
- Payments
- Play Store release steps

## Why One Build Lane At A Time Matters

One build lane at a time keeps the repo easier to review. It also prevents two APPLY tasks from editing the same area at once.

## Safe Multitasking

Safe multitasking means:

- One active coding lane
- One planning or business lane
- No two Codex APPLY tasks editing the same file area

