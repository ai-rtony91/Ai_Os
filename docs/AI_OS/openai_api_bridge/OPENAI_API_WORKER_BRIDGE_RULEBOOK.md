# OpenAI API Worker Bridge Rulebook

Status: DRY_RUN planning artifact
Task: AIOS-P16-S16.1-OPENAI-RULEBOOK-DRYRUN-001
Scope: docs-only governance plan

## Purpose

This rulebook defines the first safety layer for a future OpenAI API Worker Bridge in AI_OS.

The bridge is not an executor. It is a planner and packet-preparation layer that may reduce operator relay work by producing bounded, reviewable, Codex-ready planning output.

No live OpenAI API calls, API keys, package installs, runtime workers, broker integrations, webhooks, commits, pushes, or trading execution are approved by this document.

## Authority

The bridge is subordinate to:

- `AGENTS.md`
- `README.md`
- `docs/workflows/AI_OS_API_INTEGRATION_SAFETY_WORKFLOW.md`
- `docs/governance/AI_OS_AUTONOMY_LEVELS.md`
- `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
- `automation/orchestration/approval_inbox/APPROVAL_STATUS_RULES_001.md`
- `automation/orchestration/validators/VALIDATOR_CHAIN_RUNBOOK_001.md`

If this rulebook conflicts with those authorities, the stricter rule wins.

## Allowed Behavior

The OpenAI API Worker Bridge may:

- read approved repo context.
- summarize repo state.
- generate Codex-ready packets.
- classify work by safety level.
- suggest validator commands.
- prepare approval summaries.
- produce docs-only or fixture-only plans.
- mark missing evidence as `UNKNOWN`, `REVIEW_REQUIRED`, or `BLOCKED`.
- recommend the next safe action without executing it.

## Blocked Behavior

The OpenAI API Worker Bridge must not:

- commit.
- push.
- merge.
- stage files.
- delete files.
- move files.
- rename files.
- overwrite protected files.
- store secrets.
- request or log API keys.
- create `.env` files.
- install packages.
- call broker APIs.
- touch live trading.
- place orders.
- create real webhooks.
- bypass `AGENTS.md`.
- bypass approval inbox rules.
- bypass validators.
- bypass protected action gates.
- write to Night Supervisor runtime paths.
- mutate runtime, telemetry, control, approval, lock, memory, broker, OANDA, or trading execution paths.

## Autonomy Levels

AI_OS maps future bridge behavior as follows:

| Level | Name | Bridge status |
| --- | --- | --- |
| Level 0 | Human-only | Human decides direction, approvals, secrets, protected actions, trading escalation, commit, push, merge, deployment, and broker scope. |
| Level 1 | Read-only summary | Allowed only for approved context reads and summaries. No writes. |
| Level 2 | Packet drafting | Allowed to draft inert packets, validator suggestions, and approval summaries. No execution. |
| Level 3 | Fixture/docs proposal | Allowed to create or propose docs-only and fixture-only artifacts inside an approved path. |
| Level 4 | Staged patch proposal | Allowed to prepare exact patch proposals for human review. No staging, commit, push, or merge. |
| Level 5 | APPLY with human approval only | Allowed only after a separate APPLY packet names exact paths, files, validation, approval authority, and stop point. |
| Level 6+ | Future autonomous execution | Blocked until future governance explicitly approves the level, scope, validator chain, rollback path, and human control model. |

When unsure, choose the lower level.

## Required Workflow

The bridge must preserve the AI_OS workflow chain:

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

The bridge may draft or summarize this chain. It must not skip a step, self-approve a step, or convert a preview into execution.

## Copy-Paste Reduction Plan

The bridge should reduce manual relay work by producing structured outputs that the operator can review instead of hand-assembling long prompts.

Allowed reductions:

- convert a user goal into a complete Codex packet draft.
- include lane, allowed paths, forbidden paths, validator chain, and stop point.
- classify blocked actions before the operator spends time relaying unsafe work.
- prepare approval summaries from validator evidence.
- prepare exact next safe commands as inert text.

Blocked reductions:

- no automatic paste into Codex as execution authority.
- no automatic APPLY.
- no automatic approval inbox mutation.
- no automatic commit package execution.
- no automatic branch, PR, merge, or push.

The bridge saves relay time by preparing safer work packets, not by removing human approval.

## Secret Handling

Secret handling is blocked at this stage.

Rules:

- Use environment variable names only, such as `OPENAI_API_KEY`, when describing future configuration.
- Do not include real keys.
- Do not create `.env` files.
- Do not log keys.
- Do not place keys in docs.
- Do not place keys in fixtures.
- Do not inspect private browser sessions or account pages.
- Treat key availability as `UNKNOWN` unless a separately approved future validator proves metadata-only readiness without revealing secrets.

## Trading Safety

Trading Lab / Forex defaults to paper simulation and supervised demo review unless separately governed and approved.

Blocked:

- live trading.
- broker execution.
- OANDA.
- real orders.
- real webhooks.
- broker credentials.
- LLMs directly in live order execution paths.

Any packet that includes broker, OANDA, live trading, real orders, or credential scope must be marked `BLOCKED`.

## Night Supervisor Boundary

The bridge must not interfere with Night Supervisor.

Blocked write paths:

- `telemetry/night_supervisor/`
- `control/`
- `automation/orchestration/locks/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/memory/`
- `telemetry/`
- `automation/orchestration/night_supervisor/`

Before future bridge APPLY work, the packet must confirm clean git status, no active Night Supervisor lock, and no active in-progress cycle marker.

## Stop Conditions

Stop and report `BLOCKED` if the requested work includes:

- live API calls.
- API keys or secrets.
- `.env` creation.
- package installs.
- runtime behavior changes.
- Night Supervisor runtime writes.
- approval inbox mutation.
- broker, OANDA, live trading, webhooks, or real orders.
- commit, push, merge, stage, PR creation, or destructive Git action without explicit protected-action approval.
- missing lane, allowed paths, forbidden paths, validator chain, approval authority, or stop point.

## First Future APPLY Candidate

The next safe APPLY packet should create a local fixture-only OpenAI planner adapter scaffold.

Constraints:

- no live API call.
- no API key request.
- no `.env`.
- no package install.
- no runtime worker.
- no telemetry writes.
- no Night Supervisor writes.
- no broker or trading execution.
- output limited to a future approved docs/fixtures path.
