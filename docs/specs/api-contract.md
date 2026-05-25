# AI_OS API Contract

Status: canonical spec
Source: legacy `docs/specs/api-contract.md` + `schemas/aios/orchestration/`

## Purpose

This document defines the canonical AI_OS API contract for packet routing,
worker communication, validator response, and approval gate interaction.

It does not approve APPLY, commits, pushes, broker execution, live trading,
or autonomous action. It is a documentation spec only.

---

## Canonical Packet Contract

The primary API unit in AI_OS is the orchestration packet.

Schema: `schemas/aios/orchestration/packet.schema.json`
Schema ID: `AIOS_ORCHESTRATION_PACKET.v1`

Required fields for every executable packet:

| Field | Type | Purpose |
|---|---|---|
| `schema` | string | Must be `AIOS_ORCHESTRATION_PACKET.v1` |
| `schema_version` | string | Semantic version of schema contract |
| `packet_id` | string | Stable unique packet identifier |
| `title` | string | Short human-readable packet title |
| `objective` | string | Plain-language goal |
| `mode` | enum | `DRY_RUN` or `APPLY` |
| `status` | string | Lifecycle status |
| `scope` | object | Allowed and blocked paths/actions |
| `safety` | object | Approval, commit, push, and trading boundaries |
| `validators` | array | Validator contracts required |
| `next_safe_action` | string | Exact next operator-safe action |

---

## Orchestration Service Contract

The runtime orchestration service operates at `services/orchestrator/` on port 5050.

### Packet Routing Request

```json
{
  "packet_id": "PKT-EAST-001",
  "mode": "DRY_RUN",
  "zone": "EAST",
  "worker_identity": "EAST_OCC_01",
  "supervisor_identity": "Codex East",
  "lane": "orchestration",
  "intent": "string",
  "allowed_paths": [],
  "forbidden_paths": [],
  "approval_authority": "Human Owner",
  "validator_chain": [],
  "lock_id": "",
  "stop_point": "string"
}
```

### Packet Routing Response

```json
{
  "packet_id": "string",
  "status": "QUEUED | ASSIGNED | DRY_RUN_COMPLETE | APPLY_CANDIDATE | BLOCKED | REVIEW_REQUIRED | DONE",
  "result": "object",
  "validator_results": [],
  "audit_id": "string",
  "next_safe_action": "string"
}
```

---

## Approval Gate Contract

Schema: `schemas/aios/orchestration/packet-approval.schema.json`
Schema ID: `AIOS_PACKET_APPROVAL.v1`

Approval states:

| State | Meaning |
|---|---|
| `NOT_REQUESTED` | No approval issued yet |
| `PENDING` | Awaiting Human Owner review |
| `APPROVED` | Human Owner has approved |
| `REJECTED` | Human Owner has rejected |
| `EXPIRED` | Approval window elapsed |
| `BLOCKED` | Cannot proceed to approval |

Approval is required for: `APPLY`, `COMMIT`, `PUSH`, `PROTECTED_PATH`,
`LOCK_RELEASE`.

Validator output is evidence only. Validator PASS does not grant approval.

---

## Validator Response Contract

Schema: `schemas/aios/orchestration/packet-validator.schema.json`
Schema ID: `AIOS_PACKET_VALIDATOR.v1`

Validator states:

| State | Meaning |
|---|---|
| `NOT_RUN` | Validator has not executed |
| `PASS` | Check passed |
| `WARNING` | Caution — operator review recommended |
| `FAIL` | Check failed — packet blocked |
| `BLOCKED` | Validator cannot run |
| `REVIEW_REQUIRED` | Human review required before advancing |

---

## Lock Contract

Schema: `schemas/aios/orchestration/packet-lock.schema.json`
Schema ID: `AIOS_PACKET_LOCK.v1`

Lock naming standard: `LOCK_<ZONE>_<LANE>_<WORKER>`

Examples:
- `LOCK_EAST_ORCH_OCC01`
- `LOCK_WEST_DOCS_OCC01`

Lock statuses: `ACTIVE`, `RELEASED`, `EXPIRED`, `BLOCKED`, `REVIEW_REQUIRED`

No two workers may hold an active lock on the same claimed path simultaneously.

---

## Safety Boundaries

The API contract explicitly blocks:

- live broker connections
- OANDA execution
- real webhooks
- real orders
- API keys or secrets in request/response payloads
- live trading execution paths
- startup tasks or scheduled tasks without separate approval
- silent background execution

---

## Standardization

- All packets must reference `AIOS_ORCHESTRATION_PACKET.v1`
- All requests must include `mode`, `zone`, `worker_identity`, `approval_authority`,
  `validator_chain`, and `stop_point`
- All responses must include `status`, `validator_results`, `audit_id`,
  and `next_safe_action`
- No worker executes without a tokenized packet
- No APPLY executes without Human Owner approval
- Validator output is evidence; it is not approval
