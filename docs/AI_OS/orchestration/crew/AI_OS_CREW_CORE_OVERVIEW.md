# AI_OS Crew Core Overview

## Purpose

AI_OS Crew Core defines the internal AI_OS builder system that OCC workers can create and improve. OCC workers are the outside construction crew. AI_OS Crew is the inside builder system being built.

The first Crew Core foundation is DRY_RUN-first and governance-first. It converts human goals into structured AI_OS tasks, assigns one packet to one worker, checks locks, captures DRY_RUN output, routes approvals, selects validators, and builds exact commit package previews.

## Build Spine

```text
Task Intake
-> Crew Roles
-> Work Packet Queue
-> Worker Assignment
-> File Lock
-> DRY_RUN Result
-> Approval Inbox
-> APPLY Candidate
-> Validator
-> Commit Package
```

## Non-Replacement Rule

Crew Core must reuse current AI_OS systems:

- Work packets stay under `automation/orchestration/work_packets/`.
- Locks stay under `automation/orchestration/locks/`.
- Approval records stay under `automation/orchestration/approval_inbox/`.
- Validators stay under `automation/orchestration/validators/`.
- Commit packages stay under `automation/orchestration/commit_packages/`.

Crew Core docs and helpers describe and preview how those systems cooperate. They do not create an alternate orchestration brain.

## Safety Boundary

Crew Core must not introduce live trading, broker connections, OANDA, API-key handling, real webhooks, real orders, branch deletion, destructive Git, broad staging, direct push to main, or autonomous APPLY.
