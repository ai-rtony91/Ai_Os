# Audit Replay And Observability

Status: CURRENT
Mode: Operations documentation

## Purpose

AI_OS observability is local-first. Runtime and dispatcher behavior are reconstructed from local telemetry events and local runtime state files.

Observability is evidence, not approval.

## Telemetry Ledger

Primary ledger:

```text
telemetry/work_ledger.jsonl
```

Telemetry events are written by:

- `services/telemetry/telemetryWriter.ts`

Telemetry is replayed by:

- `services/telemetry/telemetryReplay.ts`
- `services/telemetry/automationAuditReplay.ts`
- `services/telemetry/runtimeVisibility.ts`

## Audit Replay Model

Audit replay groups events into:

- packet lifecycle
- approval
- policy decision
- execution
- failure
- recovery
- telemetry

Replay output can identify:

- packet lifecycles
- current packet status
- policy decisions
- failure summaries
- blocked packets
- failed packets
- pending approvals
- recovery recommendation

## Runtime Visibility Model

Runtime visibility combines:

- scheduler plan
- worker leases
- dead letter queue
- supervisor alerts
- backpressure
- recent telemetry
- replayed packet and approval state

The visibility model reports local status. It does not approve action.

## Operator Interpretation

MAIN CONTROL should treat audit replay as:

- evidence of what happened
- evidence of what is blocked
- evidence of pending approvals
- evidence of failed or retryable work

MAIN CONTROL must not treat audit replay as:

- APPLY approval
- recovery approval
- commit approval
- merge approval
- authorization to bypass DRY_RUN

## Invalid Data Rules

If a telemetry line cannot parse, mark the replay as degraded and label affected conclusions `INVALID DATA`.

If telemetry conflicts with visible files, terminal output, or git status, mark the conflict `MISMATCH`.

## Recovery Recommendation Rule

When audit replay reports blocked packets, failed packets, or pending approvals, the next safe action is human review before resume, retry, APPLY, commit, or push.

## Next Safe Action

Use runtime health and telemetry replay together before approving recovery or packet movement.
