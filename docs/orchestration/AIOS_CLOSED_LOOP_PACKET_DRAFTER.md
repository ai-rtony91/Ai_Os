# AIOS Closed Loop Packet Drafter

## Purpose

The Closed Loop Packet Drafter consumes a Closed Autonomy Loop recommendation
and renders a complete Codex packet preview for human review.

It bridges:

```text
Closed Loop Recommendation -> Codex Packet Preview
```

## What It Does

- reads the latest closed-loop report when present
- generates a closed-loop report in memory when the report file is missing
- normalizes the proposed action, gate result, and dispatch recommendation
- builds a packet blueprint with required AGENTS.md fields
- renders a `CODEX-ONLY PROMPT` packet preview
- writes preview output only under `Reports/sandbox/closed_loop_packet_drafter/`

## What It Does Not Do

The drafter does not execute the preview. It does not call Codex, mutate queues,
create worker inbox items, dispatch workers, start schedulers, touch credentials,
access broker systems, enable live trading, run real webhooks, commit, push, or
merge.

## Relationship To Closed Autonomy Loop

Closed Autonomy Loop owns the one-cycle recommendation:

```text
Observe -> Decide -> Plan -> Validate Gate -> Recommend Dispatch -> Report -> Stop
```

The packet drafter consumes that recommendation and turns it into a reviewable
packet preview. It does not rerank governor candidates and does not replace the
governor or the closed loop.

## Why Dispatch Stays Blocked

Dispatch requires approval evidence, queue semantics, lock ownership, worker
state, validators, and stop controls. This v1 is only a preview bridge, so its
output always keeps:

- `dispatch_authorized: false`
- `queue_mutation_authorized: false`
- worker dispatch blocked
- continuous loop blocked

## Why Human Approval Remains Required

Generated packets can still contain APPLY scope, protected paths, or safety
impact. The drafter marks APPLY-shaped recommendations as
`REQUIRES_ANTHONY_APPROVAL` and never treats validator output as approval.

## Malformed Packet Prevention

The drafter validates the packet blueprint against the required AGENTS.md fields
before writing the preview. It also checks the rendered text for required
markers and placeholder-style strings such as unresolved example paths.

Anthony should receive a complete preview or a blocked preview, not a packet
that needs manual structural repair.

## Autonomy Advancement

This adds the next bridge in the autonomy chain:

```text
Evidence -> Governor Decision -> Closed Loop Recommendation -> Packet Preview
```

AI_OS can now turn its own recommended next action into a full packet preview
while keeping execution human-controlled.

## Future Steps

The next safe future steps are:

1. queue injection preview
2. worker dispatch gate
3. Start, Pause, Resume, and Stop controls

Those steps must stay separately packeted and approval-gated.
