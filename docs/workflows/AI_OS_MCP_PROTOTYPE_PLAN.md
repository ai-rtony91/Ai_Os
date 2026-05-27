# AI_OS MCP Prototype Plan

Status: prototype plan only

This plan describes a future read-first MCP layer for AI_OS. It does not create MCP servers, start MCP processes, call APIs, expose secrets, mutate queues, grant approvals, execute commands, merge PRs, deploy cloud resources, or trade.

## Purpose

MCP should close the manual relay loop by letting ChatGPT inspect governed local AI_OS evidence through narrow local tools instead of requiring Anthony to copy prompts, paste terminal output, and manually summarize status. MCP must remain subordinate to AI_OS approval, validator, lane, and stop-point rules.

## ChatGPT to MCP to AI_OS local runtime

The intended flow is:

```text
ChatGPT intent
-> MCP read tool
-> AI_OS local evidence
-> packet or command preview
-> human approval when required
-> approved local runner in a later phase
-> telemetry receipt
-> ChatGPT summary
```

MCP closes relay work by making status, queues, approvals, telemetry, workers, and runtime state directly inspectable. It must not become approval authority.

## Prototype Servers

| MCP | Purpose | Allowed reads | Allowed writes | Blocked actions | Approval requirements | Safest first version | Future version |
|---|---|---|---|---|---|---|---|
| Filesystem MCP | Read scoped repo files and schemas | `AGENTS.md`, `README.md`, `docs/`, `schemas/`, approved automation evidence | None in v1 | secrets, `.env`, deletes, moves, renames | Writes require separate APPLY packet | Read-only file fetch with allowlist | Approved report writes to generated evidence paths |
| Git MCP | Inspect repo state | status, diff, log, branch, remote | None in v1 | reset, clean, checkout, branch delete, commit, push, merge | Commit/push/merge require explicit separate approval | Read-only status and diff | Approved PR-lane command preview |
| Shell MCP | Represent local command previews | command request and allowlist preview | None in v1 | arbitrary shell, unknown scripts, installs, destructive commands | Execution requires approval and local runner gate | Preview-only classifier | Approved allowlisted runner receipt |
| Queue MCP | Inspect packet and command queues | queue items, stale states, blocked states | None in v1 | queue mutation, packet movement | Queue mutation requires explicit APPLY packet | Read-only queue summary | Approved enqueue of packet drafts |
| Approval MCP | Inspect approval state | pending, approved, rejected, expired evidence | None in v1 | self-approval, approval mutation | Human Owner only | Read-only approval inbox summary | Approved approval receipt import |
| Telemetry MCP | Inspect append-only evidence | JSONL replay, counts, latest events | None in v1 | history rewrite, secret capture, authority grants | Telemetry writes require approved append-only policy | Read-only telemetry HUD | Approved append-only event writer |
| Worker Registry MCP | Inspect workers and locks | worker profiles, assignments, locks, heartbeats | None in v1 | worker launch, lock release, cross-lane edit | Launch/lock changes require approval | Read-only worker capacity | Approved heartbeat receipt |
| Runtime State MCP | Inspect runtime state | runtime bundle, health, scheduler preview | None in v1 | daemon startup, scheduler persistence, subprocesses | Runtime persistence requires explicit approval | Read-only runtime health | Approved local supervisor status endpoint |

## Approval Boundary

MCP must not bypass approvals. It may expose evidence and prepare previews, but human approval remains required for APPLY, commit, push, PR creation, merge, deletes, moves, renames, installs, cloud changes, startup tasks, scheduled tasks, secrets, broker actions, OANDA, webhooks, live trading, and real orders.

## Fail-Closed Rule

Every MCP tool must fail closed when path scope, command class, approval state, validator status, lane ownership, or stop point is unknown. Unknown evidence must be reported as `UNKNOWN` or `BLOCKED`, not inferred as safe.

## No Auto-Trade Or Auto-Merge

MCP must never auto-trade or auto-merge. Passing checks, available telemetry, or a clean queue is evidence only. Broker/OANDA/trading/webhook/live order actions and PR merges remain hard-gated human-only actions.

## Next Safe Action

Implement read-only filesystem, queue, approval, telemetry, worker registry, and runtime-state MCP prototypes only after command request, audit ledger, and runner preview contracts are validated.
