# Assignment Preview Persistence Apply Summary

Packet: AIOS-ASSIGNMENT-PREVIEW-PERSISTENCE-APPLY-001
Mode: APPLY
Branch: phase-night-supervisor-layer2-memory

## Summary

Implemented the next read-only closed-loop handoff:

```text
Packet -> Canonical Queue Projection -> Scheduler Preview -> Worker Resolver Preview -> Assignment Preview Persistence
```

Assignment preview persistence consumes an in-memory `WorkerResolverPreviewPlan` and returns a durable, schema-shaped preview record. It preserves worker recommendations, unmatched actions, warnings, safety flags, and the human-required next step.

## Files Created

| File | Purpose |
|---|---|
| `schemas/aios/orchestration/assignment_preview_persistence.schema.json` | Machine-readable contract for preview-only assignment records. |
| `services/dispatcher/assignmentPreviewPersistence.ts` | Pure transform module for building, validating, and serializing assignment preview records. |
| `tests/dispatcher/assignmentPreviewPersistence.test.ts` | Focused tests for record shape, safety flags, validation, serialization, and mutation safety. |
| `docs/reports/ASSIGNMENT_PREVIEW_PERSISTENCE_APPLY_SUMMARY.md` | This implementation summary. |

## Files Modified

No existing dispatcher implementation file required modification.

## What It Does

- Converts resolver preview output into `AIOS_ASSIGNMENT_PREVIEW_PERSISTENCE.v1`.
- Marks the record as `preview_record_only`.
- Preserves assignment packet IDs, worker recommendations, match evidence, and unmatched actions.
- Forces dispatch, inbox mutation, and runtime mutation authorization flags to `false`.
- Forces human approval required to `true`.
- Provides validation warnings for tampered unsafe record fields.
- Serializes the record as pretty JSON with a trailing newline.

## What It Deliberately Does Not Do

- Does not read or write files.
- Does not write worker inbox state.
- Does not dispatch or launch workers.
- Does not mutate packets, queues, telemetry, approvals, runtime state, or commit packages.
- Does not authorize approval, commit, push, merge, deployment, trading execution, broker execution, secret access, or credential access.

## Exact Human Step Removed

Operator no longer has to manually translate worker resolver preview output into a durable preview-record shape.

## Human Gate Preserved

Human still approves assignment persistence into operational inbox/state in a future lane.

## Validation Results

Required validation commands:

```text
git diff --check
git diff --name-only
powershell -NoProfile -Command "Get-Content -Raw -LiteralPath 'schemas/aios/orchestration/AIOS_CLOSED_LOOP_STATE_CONTRACT_V1.schema.json' | ConvertFrom-Json | Out-Null; 'STATE_CONTRACT_JSON_PARSE_OK'"
powershell -NoProfile -Command "Get-Content -Raw -LiteralPath 'schemas/aios/orchestration/canonical_queue_projection.schema.json' | ConvertFrom-Json | Out-Null; 'CANONICAL_QUEUE_SCHEMA_JSON_PARSE_OK'"
powershell -NoProfile -Command "Get-Content -Raw -LiteralPath 'schemas/aios/orchestration/worker_resolver_preview.schema.json' | ConvertFrom-Json | Out-Null; 'WORKER_RESOLVER_SCHEMA_JSON_PARSE_OK'"
powershell -NoProfile -Command "Get-Content -Raw -LiteralPath 'schemas/aios/orchestration/assignment_preview_persistence.schema.json' | ConvertFrom-Json | Out-Null; 'ASSIGNMENT_PREVIEW_SCHEMA_JSON_PARSE_OK'"
```

Result: pending final packet validation.

## Test Results

Required tests:

```text
node --test tests/dispatcher/canonicalQueueProjection.test.ts
node --test tests/dispatcher/schedulerPreview.test.ts
node --test tests/dispatcher/workerResolverPreview.test.ts
node --test tests/dispatcher/assignmentPreviewPersistence.test.ts
```

Result: pending final packet validation.

## Known Limitations

- This layer returns a record shape only; it does not choose where records should be stored.
- No operational assignment state is written.
- Worker inbox writes remain blocked until a future human-approved lane.

## Next Lane

Recommended next APPLY lane:

```text
AIOS-VALIDATOR-EVIDENCE-ATTACHMENT-APPLY-001
```

Do not start it from this packet.
