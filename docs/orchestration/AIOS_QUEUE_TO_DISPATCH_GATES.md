# AIOS Queue To Dispatch Gates

## Purpose

Queue To Dispatch Gates v1 consumes the Closed Loop Queue Injection Preview and
emits one consolidated preview report covering:

- queue admission preview
- worker dispatch preview
- human approval preview
- real queue injection gate preview

It is a consolidation layer for review and evidence. It is not the real queue
owner and it is not a dispatcher.

## What It Does

- reads `Reports/sandbox/closed_loop_queue_injection_preview/AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json`
- validates the proposed queue item shape
- blocks queue mutation, worker dispatch, live trading, broker, credential,
  webhook, scheduler, background-loop, and protected Git scope
- marks APPLY-like queue items as requiring Anthony approval
- writes one sandbox report under `Reports/sandbox/queue_to_dispatch_gates/`

## What It Does Not Do

It does not enqueue work, mutate `automation/orchestration/work_packets/`, write
worker inbox state, dispatch workers, call Codex, start schedulers, execute
webhooks, touch credentials, enable broker or live trading behavior, stage,
commit, push, reset, checkout, merge, or delete files.

## Relationship To Existing Queue Owners

The active real queue and packet lifecycle remain under
`automation/orchestration/work_packets/`. The existing queue mutation gate
remains the canonical real-write gate for its scope.

This module consolidates preview evidence from the closed-loop queue preview
path. It does not replace the queue mutation gate, approval inbox, worker
registry, worker inbox, dispatcher, or runtime packet state.

## Gate Meanings

`queue_admission_preview` checks whether the proposed queue item is structurally
safe as preview evidence.

`worker_dispatch_preview` shows whether dispatch could be considered later, but
always keeps `dispatch_authorized: false`.

`human_approval_preview` records whether Anthony approval is required.

`real_queue_injection_gate_preview` shows the real queue injection boundary, but
always keeps `queue_mutation_authorized: false`.

## Safety Boundary

The consolidated report is evidence only. It cannot approve APPLY, mutate the
real queue, launch a worker, start a loop, create a scheduler, call a provider,
use credentials, execute webhooks, or run broker/live-trading paths.

## Future Step

The next safe future step is a worker dispatch gate preview that consumes only
admitted preview evidence while still keeping dispatch disabled.
