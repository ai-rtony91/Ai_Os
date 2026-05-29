# Canonical Queue Projection Apply Summary

Packet: AIOS-CANONICAL-QUEUE-PROJECTION-APPLY-001
Mode: APPLY
Branch: phase-night-supervisor-layer2-memory

## Summary

Created the first read-only glue layer for:

```text
Packet -> Canonical Queue
```

This implementation projects existing packet JSON files into an in-memory canonical queue view. It does not write packet files, mutate queue files, dispatch workers, call the scheduler, write telemetry, request approvals, create commit packages, commit, push, merge, deploy, or touch trading paths.

## Files Created

| File | Purpose |
|---|---|
| `schemas/aios/orchestration/canonical_queue_projection.schema.json` | Machine-readable projection contract for the canonical queue read model. |
| `services/dispatcher/canonicalQueueProjection.ts` | Read-only TypeScript projection utility. |
| `tests/dispatcher/canonicalQueueProjection.test.ts` | Focused tests for state normalization, projection behavior, malformed JSON handling, unknown states, and read-only behavior. |
| `docs/reports/CANONICAL_QUEUE_PROJECTION_APPLY_SUMMARY.md` | This implementation summary. |

## Projection Behavior

The projection:

- reads `.json` packet files from a caller-provided `packetRoot`;
- normalizes legacy packet states into the canonical queue vocabulary;
- emits `AIOS_CANONICAL_QUEUE_PROJECTION.v1`;
- marks low/medium risk queued packets with no dependencies or blockers as `ready`;
- blocks packets with blockers or protected risk;
- routes unknown state to manual review by projecting `unknown`;
- records malformed JSON as warnings and skips the malformed packet;
- returns an in-memory object only.

## Safety Boundaries

Read-only guarantees:

- no packet writes;
- no queue writes;
- no telemetry writes;
- no worker dispatch;
- no scheduler call;
- no approval mutation;
- no commit package mutation;
- no trading, broker, OANDA, credential, or secret access.

## Next Lane

Recommended next APPLY lane:

```text
AIOS-SCHEDULER-CONSUMES-CANONICAL-QUEUE-APPLY-001
```

That lane should connect scheduler preview to the projection without assignment persistence or worker dispatch.
