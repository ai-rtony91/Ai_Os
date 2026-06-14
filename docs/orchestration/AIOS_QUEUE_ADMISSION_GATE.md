# AIOS Queue Admission Gate

## Purpose

Queue Admission Gate v1 consumes the Closed Loop Queue Injection Preview and
decides whether the proposed queue item is admissible as preview-only evidence,
blocked, or waiting for Anthony approval.

It bridges:

```text
Proposed Queue Item Preview -> Admission Decision Preview
```

## What It Does

- reads `Reports/sandbox/closed_loop_queue_injection_preview/AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json`
- validates required proposed queue item fields
- blocks weakened safety flags
- blocks live trading, broker, credential, webhook, scheduler, background-loop,
  and protected Git action scope
- emits an admission result under `Reports/sandbox/queue_admission_gate/`

## What It Does Not Do

The gate does not enqueue anything, mutate real queue files, write worker inbox
state, dispatch workers, execute packet text, create schedulers, touch
credentials, call providers, run webhooks, commit, push, merge, reset, or
checkout.

## Relationship To Queue Injection Preview

Queue Injection Preview builds the proposed queue item. Queue Admission Gate
evaluates that proposed item and says whether it is structurally admissible as a
preview-only artifact. It does not replace the existing queue mutation gate or
the canonical runtime packet state under `automation/orchestration/work_packets/`.

## Why Real Queue Mutation Remains Blocked

Admission is not mutation. Real queue writes require a separate approved queue
mutation gate with exact scope, approval evidence, duplicate checks, locks,
validators, and stop conditions. This gate always emits:

- `queue_mutation_authorized: false`
- `real_queue_mutation: blocked`

## Why Worker Dispatch Remains Blocked

Dispatch depends on queue admission, worker state, lock ownership, validator
evidence, and future Start/Pause/Resume/Stop controls. This v1 only evaluates
admission readiness, so `dispatch_authorized` remains `false`.

## Autonomy Advancement

This adds the next controlled bridge:

```text
Evidence -> Closed Loop Recommendation -> Packet Preview -> Queue Item Preview -> Admission Decision Preview
```

AI_OS can now judge whether its generated queue preview is safe enough for a
future gate, while keeping real execution disabled.

## Future Steps

The next future steps are:

1. worker dispatch gate preview
2. Start, Pause, Resume, and Stop controls

Those steps must remain separately packeted, approval-gated, and validation
backed.
