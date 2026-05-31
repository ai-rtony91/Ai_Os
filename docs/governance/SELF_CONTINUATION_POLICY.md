# AI_OS Self-Continuation Policy

## Purpose

Self-continuation lets AI_OS propose one next goal after a clean cycle. It does not let AI_OS approve, execute, or enqueue that goal directly.

## Boundary

The controller may only read from the bounded backlog at:

```text
control/self_continuation/BACKLOG.json
```

It must not invent goals from open-ended reasoning, logs, chat history, telemetry, or model judgment. If a goal is not in the backlog, it is out of scope.

## Clean-Cycle Gate

The controller may propose a next goal only when the latest cycle state is clean:

- supervisor status is `PASS` or `CLEAN`
- blocked count is zero
- approval-needed count is zero
- must-see entries are empty

If the latest state is `BLOCKED`, `NEEDS_APPROVAL`, `WARN`, missing, stale, malformed, or ambiguous, the controller must stop and write nothing.

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

The controller selects at most one candidate per run:

1. backlog is enabled
2. candidate status is `READY`
3. candidate risk level is `GREEN`
4. highest numeric priority wins
5. ties sort by candidate id

Non-GREEN candidates are never auto-queued. They remain bounded backlog candidates and require explicit human approval before any execution packet may be created.

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
