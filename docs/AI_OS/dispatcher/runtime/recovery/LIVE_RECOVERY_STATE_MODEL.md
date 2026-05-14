# Live Recovery State Model

This document defines the first local recovery-state layer for AI_OS runtime coordination.

The recovery layer reads local packet, worker, heartbeat, and registration state. It does not create automatic recovery behavior.

## Purpose

The live recovery state exists to show whether runtime work is safe to continue.

It tracks:

- interrupted APPLY state
- stale packet state
- stale worker state
- stale lock state
- recovery review state
- next safe operator action

## Source Files

Recovery reads these runtime files:

- `Reports/dispatcher/runtime/packets/packet_runtime_table.json`
- `Reports/dispatcher/runtime/workers/active_worker_table.json`
- `Reports/dispatcher/runtime/workers/worker_heartbeat_table.json`
- `Reports/dispatcher/runtime/workers/worker_registration_status.json`

Recovery writes summary state to:

- `Reports/dispatcher/runtime/recovery/live_recovery_state.json`
- `Reports/dispatcher/runtime/recovery/interrupted_apply_report.json`
- `Reports/dispatcher/runtime/recovery/stale_runtime_report.json`

## Safety Rules

The recovery layer must not:

- resume APPLY automatically
- reassign packets automatically
- release locks automatically
- stage files
- commit
- push
- create startup tasks
- create scheduled tasks
- collect secrets
- enable external execution

Human approval is required before recovery resume, packet reassignment, lock release, APPLY retry, staging, commit, or push.

## Recovery Status

Use `REVIEW_REQUIRED` when any runtime state is missing, stale, contradictory, or incomplete.

Use `BLOCKED` when a validator reports unsafe state.

Use `PASS` only when packet, worker, heartbeat, lock, approval, and validator state are all current and consistent.

## Interrupted APPLY Model

Interrupted APPLY state should include:

- `packet_id`
- `worker_id`
- `apply_started_at`
- `last_heartbeat_at`
- `claimed_paths`
- `lock_ids`
- `changed_files_detected`
- `validation_status`
- `review_status`
- `next_safe_action`

If APPLY started and validation did not complete, the state is `REVIEW_REQUIRED`.

## Stale Packet Model

A packet is stale when it is assigned or running but its worker, heartbeat, lock, or approval state is missing, stale, or contradictory.

Stale packets must not be reassigned automatically.

## Stale Worker Model

A worker is stale when it lacks a current live heartbeat, has incomplete registration, or conflicts with packet or lock state.

Stale workers must not be replaced automatically.

## Stale Lock Model

A lock is stale when it is expired, orphaned, overlapping, tied to missing worker state, tied to missing packet state, or tied to interrupted APPLY.

Stale locks must not be released automatically.

## Operator Check Integration

Operator checks should read `live_recovery_state.json` and report:

- `recovery_status`
- `review_required_count`
- `interrupted_apply_count`
- `stale_packet_count`
- `stale_worker_count`
- `stale_lock_count`
- `next_safe_action`

The operator check should report recovery state only. It should not repair or resume runtime work.

## Current Runtime Reading

Current packet runtime state shows one queued DRY_RUN packet and no assigned packet.

Current worker runtime state shows ten workers requiring registration and heartbeat review before assignment.

Current recovery status is `REVIEW_REQUIRED`.

## Next Safe Action

Human operator should review worker registration and heartbeat state before assigning or resuming runtime work.
