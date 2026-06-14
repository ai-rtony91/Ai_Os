# AIOS Active Mission Cycle

## Purpose

Active Mission Cycle v1 is the first active operator-reporting layer for the
AI_OS autonomy chain. It reads existing closed-loop, packet-drafter,
queue-preview, queue-to-dispatch gate, repo-state, governor, validator,
autonomy-status, and runtime evidence, then writes one short SOS report for
Anthony.

The report answers:

- what AI_OS checked
- what AI_OS selected
- why it selected it
- what is blocked
- what Anthony needs to do
- what the next safe action is

## What It Does Not Do

It does not run workers, enqueue packets, mutate the real queue, start a
scheduler or background loop, execute webhooks, use credentials, trade, connect
to a broker, stage, commit, push, merge, reset, checkout, or delete files.

The active mission cycle is one-cycle reporting only. It stops after writing:

- `Reports/sandbox/active_mission_cycle/AIOS_ACTIVE_MISSION_CYCLE_LATEST.json`
- `Reports/sandbox/active_mission_cycle/AIOS_ACTIVE_MISSION_SOS_LATEST.md`

## Relationship To The Existing Chain

The Closed Autonomy Loop decides the next safe action. The Packet Drafter turns
that recommendation into a Codex packet preview. Queue Injection Preview shows
how the packet would enter queue shape. Queue To Dispatch Gates judge the
preview-only admission, approval, dispatch, and real queue-injection gates.

Active Mission Cycle does not replace any of those owners. It composes their
latest evidence into an operator-readable status and SOS note.

## Safety Boundary

The output always keeps:

- `queue_mutation_authorized: false`
- `dispatch_authorized: false`
- `live_trading: blocked`
- `broker_execution: blocked`
- `continuous_loop: blocked`

Missing evidence produces a blocked or partial SOS instead of failing silently.
Dirty repo evidence reports `requires_cleanup`. Blocked upstream preview
evidence is surfaced as the current blocker.

## Future Step

The next safe future step is a manual command surface or run wrapper that invokes
this one-cycle reporter on demand. Start/Pause/Resume/Stop controls and any
controlled scheduler belong after explicit approval, after the preview chain and
operator command surface remain stable.
