# Top 25 APPLY Lanes

Packet: AIOS-MASTER-RECONCILIATION-ROADMAP-DRYRUN-001
Mode: DRY_RUN report creation only

## Ordering Principle

These are implementation lanes, not new investigations. A DRY_RUN is included only where mutation would otherwise be unsafe without a precise state contract or consumer list.

## Priority Stack

| Order | Lane Name | Purpose | Dependencies | Risk | Expected Gain |
|---:|---|---|---|---|---|
| 1 | `AIOS-CLOSED-LOOP-STATE-CONTRACT-APPLY-001` | Add canonical state vocabulary and mapping table for packet/queue/scheduler/worker/validator/approval/commit states | Existing reports | Medium | Removes unsafe state ambiguity |
| 2 | `AIOS-CANONICAL-QUEUE-PROJECTION-APPLY-001` | Create read-only queue projection from `automation/orchestration/work_packets/` | Lane 1 | Medium | Closes first hard loop break without mutation |
| 3 | `AIOS-QUEUE-PROJECTION-VALIDATOR-APPLY-001` | Add validator for projection schema and status normalization | Lanes 1-2 | Low | Makes queue projection trustworthy |
| 4 | `AIOS-SCHEDULER-PREVIEW-QUEUE-INPUT-APPLY-001` | Feed queue projection into scheduler preview only | Lanes 1-3 | Medium | Makes scheduler reason over real packets |
| 5 | `AIOS-SCHEDULER-TO-WORKER-RESOLVER-PREVIEW-APPLY-001` | Connect scheduler dispatch actions to worker resolver preview | Lane 4 | Medium | Produces assignment plans from queued packets |
| 6 | `AIOS-WORKER-UNKNOWN-OWNER-ESCALATION-APPLY-001` | Change unresolved worker ownership to manual review instead of fallback assignment | Lane 5 | Medium | Prevents unsafe default routing |
| 7 | `AIOS-WORKER-ASSIGNMENT-WRITER-SAFE-LANES-APPLY-001` | Add governed assignment writer for docs/tests/report lanes only | Lanes 5-6 | High | First persistent assignment path |
| 8 | `AIOS-WORKER-INBOX-SCHEMA-GATE-APPLY-001` | Validate worker inbox items before persistence | Lane 7 | Medium | Protects assignment state |
| 9 | `AIOS-PACKET-SCOPED-VALIDATOR-ROUTER-APPLY-001` | Route validators from packet id, changed files, path risk, and classification | Lanes 1-3 | Medium | Reduces manual validator selection |
| 10 | `AIOS-VALIDATOR-EVIDENCE-WRITER-APPLY-001` | Persist packet-scoped validator results to approved evidence path | Lane 9 | Medium | Enables approval and commit package consumption |
| 11 | `AIOS-APPROVAL-INBOX-REPAIR-APPLY-001` | Restore or create canonical active approval inbox file and schema guard | Lane 1 | High | Repairs approval handoff |
| 12 | `AIOS-PACKET-APPROVAL-REQUEST-WRITER-APPLY-001` | Persist approval request items from packet/evidence into active inbox | Lanes 10-11 | High | Closes validation-to-approval break |
| 13 | `AIOS-APPROVAL-RISK-SUMMARY-APPLY-001` | Add risk, affected paths, validators, and unblock value to approval items | Lanes 10-12 | Medium | Reduces operator interpretation work |
| 14 | `AIOS-COMMIT-PACKAGE-EVIDENCE-INPUTS-APPLY-001` | Add packet id, validator evidence path, approval id, and allowed file list inputs to commit package recommender | Lanes 10-13 | Medium | Ties commits to packet evidence |
| 15 | `AIOS-COMMIT-PACKAGE-DEPENDENCY-GROUPING-APPLY-001` | Group changed files by packet/dependency ownership, not raw Git status | Lane 14 | Medium | Reduces manual hunting and backlog mixing |
| 16 | `AIOS-EVENT-LOG-CONTRACT-APPLY-001` | Add append-only orchestration event log contract and minimal writer interface | Lanes 1-3 | High | Creates crash-survivable flight recorder |
| 17 | `AIOS-EVENT-COMPATIBILITY-MAPPER-APPLY-001` | Map runtime/telemetry events into canonical orchestration event shape | Lane 16 | High | Reconciles event families |
| 18 | `AIOS-KNOWLEDGE-GRAPH-SEED-APPLY-001` | Create runtime-loadable graph seed from active authority maps and execution registry | Lane 1 | Medium | Enables ownership and risk queries |
| 19 | `AIOS-KNOWLEDGE-GRAPH-QUERY-HELPER-APPLY-001` | Add read-only helper for "what owns X" and "what breaks if X changes" | Lane 18 | Medium | Supports routing, approval, validator decisions |
| 20 | `AIOS-WINDOW-IDENTITY-REGISTRY-DEMOTION-APPLY-001` | Rename window registry to non-canonical identity binding and update consumers | Existing duplicate report | Medium | Removes worker registry ambiguity |
| 21 | `AIOS-SOS-ESCALATION-POLICY-APPLY-001` | Create canonical SOS-only escalation policy | Lanes 1,16 | Medium | Defines what wakes Anthony |
| 22 | `AIOS-RECOVERY-QUALIFICATION-LEDGER-APPLY-001` | Add recovery drill/qualification ledger and quarantine decision rules | Lanes 16,21 | High | Starts safe recovery maturity |
| 23 | `AIOS-AUTONOMY-SCORECARD-SCHEMA-APPLY-001` | Define metrics for routing, validation, recovery, approval, and human coordination load | Lanes 1,16 | Low | Measures progress objectively |
| 24 | `AIOS-MCP-SAFE-HANDS-DOCS-APPLY-001` | Add MCP Safe Hands doc/checklist and manual stop point | Can run earlier, but not required for loop closure | Low | Prepares safe tool access |
| 25 | `AIOS-NIGHT-BUILDER-READONLY-PILOT-APPLY-001` | Produce read-only overnight/morning brief from queue, event, approval, validator, and scorecard evidence | Lanes 2-4,10-13,16,21,23,24 | High | First safe Night Builder milestone |

## Highest-Leverage 5-Lane Sequence

1. `AIOS-CLOSED-LOOP-STATE-CONTRACT-APPLY-001`
2. `AIOS-CANONICAL-QUEUE-PROJECTION-APPLY-001`
3. `AIOS-QUEUE-PROJECTION-VALIDATOR-APPLY-001`
4. `AIOS-SCHEDULER-PREVIEW-QUEUE-INPUT-APPLY-001`
5. `AIOS-SCHEDULER-TO-WORKER-RESOLVER-PREVIEW-APPLY-001`

Why this sequence:

It attacks the actual first and second loop breaks without launching workers, mutating approval state, touching runtime execution, installing MCP, committing, pushing, merging, deploying, or entering trading paths.

## Exact First APPLY Lane

```text
Packet ID: AIOS-CLOSED-LOOP-STATE-CONTRACT-APPLY-001
Mode: APPLY
Lane: Closed Loop State Contract
Allowed paths:
- schemas/aios/orchestration/
- docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md if explicitly approved
Forbidden:
- automation/
- services/
- runtime/
- telemetry/
- apps/
- scripts/
- trading/
- broker/
- OANDA/
- secrets/
- credentials/
Stop:
- after schema/doc contract and validation only
```

Most important requirement:

Do not make preview scripts mutate state to create motion. Define the state contract first, then connect one handoff at a time.
