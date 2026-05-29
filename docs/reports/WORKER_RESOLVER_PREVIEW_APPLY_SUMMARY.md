# Worker Resolver Preview Apply Summary

Packet: AIOS-CLOSED-LOOP-DISPATCHER-GLUE-COMPOUND-APPLY-001
Mode: APPLY
Branch: phase-night-supervisor-layer2-memory

## Summary

Implemented the next read-only closed-loop handoff:

```text
Packet -> Canonical Queue Projection -> Scheduler Preview -> Worker Resolver Preview
```

The worker resolver preview consumes an in-memory `SchedulerPreviewPlan` and caller-provided worker capability data. It emits preview-only assignment candidates and unmatched actions. It does not read registry files directly, persist assignments, write worker inboxes, dispatch workers, mutate packets, mutate queues, mutate telemetry, approve work, prepare commits, commit, push, merge, deploy, or touch trading paths.

## Files Created

| File | Purpose |
|---|---|
| `schemas/aios/orchestration/worker_resolver_preview.schema.json` | Machine-readable read-only worker resolver preview contract. |
| `services/dispatcher/workerResolverPreview.ts` | Pure TypeScript resolver preview utility for scheduler actions and worker capability data. |
| `tests/dispatcher/workerResolverPreview.test.ts` | Focused tests for matching, exclusions, risk ceilings, ranking, and input mutation safety. |
| `docs/reports/WORKER_RESOLVER_PREVIEW_APPLY_SUMMARY.md` | This implementation summary. |

## Files Modified

No existing dispatcher implementation file required modification. `schedulerPreview.ts` already exports stable plan and action types.

## Resolver Preview Behavior

The preview:

- accepts `SchedulerPreviewPlan`, workers, and optional `now`;
- joins scheduler `recommended_order` with `worker_capability_requirements` by packet id;
- recommends only active, available workers;
- requires at least one capability or lane signal match;
- enforces risk ceilings using `low < medium < high < protected`;
- leaves protected and unknown-risk actions unmatched for human-gated handling;
- ranks candidates by capability match, lane fit, complete match, and risk fit;
- emits `AIOS_WORKER_RESOLVER_PREVIEW.v1` with `preview_mode` set to `read_only_preview`.

## Deliberate Non-Goals

This lane deliberately does not:

- assign workers;
- write assignment state;
- write worker inbox files;
- launch Codex or any worker;
- mutate packet or queue files;
- call runtime, supervisor, or orchestrator services;
- mutate telemetry;
- approve, commit, push, merge, deploy, or touch protected trading, broker, credential, or secret paths.

## Test Results

Required validation commands:

```text
node --test tests/dispatcher/canonicalQueueProjection.test.ts
node --test tests/dispatcher/schedulerPreview.test.ts
node --test tests/dispatcher/workerResolverPreview.test.ts
```

Result: pending final packet validation.

## Known Limitations

- Worker data is passed in by the caller; the resolver core intentionally does not read registries directly.
- Assignment persistence is not implemented.
- Worker inbox writes are not implemented.
- Protected-risk work remains unmatched and human-gated.

## Next Lane

Recommended next APPLY lane:

```text
AIOS-ASSIGNMENT-PREVIEW-PERSISTENCE-DRYRUN-OR-APPLY-001
```

That lane should decide whether and where preview assignment evidence may be persisted without dispatching workers.
