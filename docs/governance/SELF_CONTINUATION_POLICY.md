# AI_OS Self-Continuation Policy

## Purpose

Self-continuation lets AI_OS propose one next goal after a clean cycle. It does not let AI_OS approve, execute, or enqueue that goal directly.

## Boundary

The controller may only read from the bounded backlog at:

```text
control/self_continuation/BACKLOG.json
```

It must not invent goals from open-ended reasoning, logs, chat history, telemetry, or model judgment. If a goal is not in the backlog, it is out of scope.

## Gate States

Self-continuation reports one of these gate states:

- `PASS_CLEAN`: latest cycle is clean enough to propose one approval item.
- `SUPERVISED_BACKLOG`: validators and QA are safe, but human approval or expected supervised review is still pending.
- `TRUE_BLOCKED`: safety, scheduler, credential, trading, git write, broker, OANDA, secret, API-key, malformed, missing, or ambiguous evidence blocks progress.
- `FAILED_VALIDATION`: validator, parse, integrity, or QA evidence failed.
- `NOOP`: no eligible backlog goal exists.
- `STOPPED`: kill switch, disabled backlog, missing required state, or an explicit stop condition halted the controller.

## Clean-Cycle Gate

The controller may propose a next goal only when the latest cycle state is `PASS_CLEAN`:

- supervisor status is `PASS` or `CLEAN`
- blocked count is zero
- approval-needed count is zero
- must-see entries are empty

`NEEDS_APPROVAL` or approval-needed backlog is `SUPERVISED_BACKLOG` when validator and QA evidence are safe and no true blocker is present. This state is expected in supervised mode. It still prevents self-continuation from writing an approval item, but it is not treated as a safety failure.

If the latest state is `BLOCKED`, `WARN`, missing, stale, malformed, ambiguous, or contains true blocker evidence, the controller must classify it as `TRUE_BLOCKED` or `STOPPED` and write nothing. If validator or QA evidence failed, the controller must classify it as `FAILED_VALIDATION` and write nothing.

## Proposal Gate

Every self-continuation output is an approval item under:

```text
relay/approvals/
```

The controller must never write a self-generated goal directly to:

```text
relay/inbox/
```

The approval item must include the backlog source, selected goal, risk level, gate flags, allowed paths, forbidden paths, and provenance showing it came from self-continuation.

## Selection Rule

The controller selects at most `max_auto_goals_per_cycle` candidates per run:

1. backlog is enabled
2. candidate status is `READY`
3. candidate `risk_level` is `GREEN`
4. highest numeric priority wins
5. ties sort by candidate id
6. `control/self_continuation/STOP` is absent

Non-GREEN candidates are never auto-queued as goals. They route to `relay/approvals/` and require explicit human approval before any execution packet may be created.

## Backlog Pull Discipline

`automation/orchestration/backlog/Pull-AiOsBacklog.ps1` is the only approved helper for pulling backlog work into the relay goal queue. It may pull at most `max_auto_goals_per_cycle` items per invocation, and only when all gates match:

- `status` is `READY`
- `risk_level` is `GREEN`
- `control/self_continuation/STOP` is absent

Non-GREEN, ambiguous, missing, or malformed items must not become goals. READY non-GREEN items route to `relay/approvals/{id}.approval.md`. The helper writes at most `max_auto_goals_per_cycle` `relay/goals/{id}.goal.txt` files per run. Recurring GREEN candidates remain `READY`; non-recurring GREEN candidates are marked `PULLED` using a separate atomic temp-file replace.

## Kill Switch

Self-continuation halts when either condition is true:

- `control/self_continuation/STOP` exists
- `control/self_continuation/BACKLOG.json` is missing, disabled, or invalid

The kill switch is intentionally simple: create the STOP file or remove/disable the backlog.

## Forbidden Actions

The self-continuation controller must not:

- execute a proposed goal
- write to `relay/inbox/`
- approve its own output
- modify approval source stores
- register or start scheduled tasks
- run git write actions
- access secrets
- touch broker or live trading paths
