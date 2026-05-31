# Approval Unification Plan

## Purpose

AI_OS currently exposes approval state through Relay approval files, Operation Glue approval inbox records, and the Python Night Supervisor approval queue projection. This plan keeps those stores read-only and adds one canonical projection view for dashboards, validators, and future migration planning.

## Current Stores

| Store | Path / module | Current role | P6 behavior |
| --- | --- | --- | --- |
| Relay approvals | `relay/approvals/**/*.json`, `relay/approvals/**/*.md` | Human-readable and file-routed approval evidence. | Read-only source. No move, delete, overwrite, approve, or reject. |
| Operation Glue | `control/operation_glue/APPROVAL_INBOX.json` | Glue worker/result review queue. | Read-only source. No inbox mutation. |
| Python queue | `services/python_supervisor/approval_queue.py` | Existing Relay approval projection for Night Supervisor views. | Read-only projected source. No source store mutation. |

## Canonical Projection

The canonical item schema is `schemas/aios/approvals/approval_item.schema.json`.

The read-only projector is `services/python_supervisor/approval_projector.py`.

Default mode prints the unified view and writes nothing. `--apply` writes only:

```text
telemetry/approvals/UNIFIED_APPROVALS.json
```

## Deduplication Rule

Stable key:

1. `origin_ref` when present.
2. Otherwise `source_path`.
3. Otherwise `id`.

If duplicate keys collide, the safer status wins in this order:

```text
BLOCKED > WAITING_APPROVAL > APPROVED > REJECTED
```

If status is tied, source priority is:

```text
relay > glue > python_queue
```

## Future Cutover Proposal

1. Keep all three current stores active while dashboards consume `telemetry/approvals/UNIFIED_APPROVALS.json`.
2. Add validators that compare per-store counts against the unified projection.
3. Add explicit origin references to approval records that lack them.
4. Promote one source-of-truth store only after a separate migration packet names the owner, migration direction, rollback path, and human approval authority.

## Rollback

Rollback is delete-or-ignore projection output only:

```text
telemetry/approvals/UNIFIED_APPROVALS.json
```

Do not delete, move, or rewrite any source approval records as part of rollback.

## Non-Goals

- No approval migration.
- No source-store mutation.
- No approval or rejection decision.
- No commit or push.
- No external channel.
- No broker, webhook, live trading, or secret handling.
