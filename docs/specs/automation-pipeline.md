# AI_OS Automation Pipeline

Status: canonical spec
Source: legacy `docs/specs/automation-pipeline.md` + `docs/workflows/APPLY_ROUTING_CHAIN.md`

## Purpose

This document defines the canonical AI_OS automation pipeline. It maps the
journey from human intent to governed packet execution, validator confirmation,
and Human Owner approval.

It does not approve APPLY, commits, pushes, worker launch, broker execution,
live trading, or autonomous action. It is a documentation spec only.

---

## Pipeline Stages

```text
INTENT_RECEIVED
-> PACKET_CREATED
-> ZONE_ASSIGNED
-> DRY_RUN
-> VALIDATOR_CHAIN_RUN
-> DRY_RUN_COMPLETE
-> APPROVAL_REQUESTED
-> HUMAN_OWNER_APPROVES
-> LOCK_CLAIMED
-> APPLY
-> VALIDATOR_CHAIN_RUN (post-apply)
-> COMMIT_PACKAGE_REVIEWED
-> COMMIT
-> PUSH
-> PR_CREATED
-> LOCK_RELEASED
-> DONE
```

---

## Stage Definitions

| Stage | Owner | Outputs | Blocked by |
|---|---|---|---|
| `INTENT_RECEIVED` | Business GPT | Packet draft | Missing required packet fields |
| `PACKET_CREATED` | Business GPT | Tokenized packet with all identity fields | Missing `packet_id`, `mode`, `zone`, `worker_identity`, `stop_point` |
| `ZONE_ASSIGNED` | Business GPT | East or West zone assignment | Path collision with other zone |
| `DRY_RUN` | Assigned worker (EAST/WEST) | Inspection report, no file mutations | Any mutation attempt |
| `VALIDATOR_CHAIN_RUN` | Validator worker | PASS/WARN/FAIL per check | Any FAIL — packet blocks |
| `DRY_RUN_COMPLETE` | Supervisor | Report delivered, ready for approval | Incomplete report, missing stop point |
| `APPROVAL_REQUESTED` | Supervisor → Human Owner | Approval inbox entry | Gate already rejected or expired |
| `HUMAN_OWNER_APPROVES` | Human Owner only | Approval record committed | Nothing — Human Owner is final authority |
| `LOCK_CLAIMED` | Assigned worker | Active lock entry in lock registry | Conflicting active lock on same path |
| `APPLY` | Assigned worker | Exact file edits per allowed paths | Any forbidden path touched |
| `VALIDATOR_CHAIN_RUN` | Validator worker | Post-apply PASS/WARN/FAIL | Any FAIL — blocks commit |
| `COMMIT_PACKAGE_REVIEWED` | Supervisor | Exact-file commit package confirmed | Files outside approved paths in package |
| `COMMIT` | Assigned worker | Commit hash | Hook failures, dirty tree outside scope |
| `PUSH` | Assigned worker | Remote branch | Final Human Owner push approval not recorded |
| `PR_CREATED` | Assigned worker | PR number and URL | Merge not triggered automatically |
| `LOCK_RELEASED` | Assigned worker | Lock status set to RELEASED | Lock record not found |
| `DONE` | Supervisor | Final report | — |

---

## Packet Lifecycle States

```text
PROPOSED -> QUEUED -> ASSIGNED -> DRY_RUN_COMPLETE
         -> APPLY_CANDIDATE -> REVIEW_REQUIRED -> DONE
         -> BLOCKED (at any stage)
```

A blocked packet must report: what failed, why it failed, what needs to
happen next, and the next safe command or prompt.

---

## East / West Routing

| Zone | Worker pattern | Supervisor |
|---|---|---|
| EAST | `EAST_OCC_##` | Codex East |
| WEST | `WEST_OCC_##` | Claude Code West |
| VALIDATOR | `VALIDATOR_##` | Either zone |

East and West must not edit the same file tree at the same time. Cross-zone
work requires a matching packet identity, lock identity, allowed paths,
approval authority, validator chain, and stop point.

---

## Fail-Safe Rules

- No pipeline stage may be skipped.
- Any FAIL at validator chain blocks the pipeline.
- Any missing approval blocks the APPLY stage.
- Any lock conflict blocks the APPLY stage.
- Any forbidden path touched blocks the COMMIT stage.
- Retry logic is controlled by Business GPT only — workers must not
  self-retry without a new packet.
- All pipeline activity is logged per `audit_id`.

---

## Safety Boundaries

The pipeline explicitly excludes:

- broker execution
- OANDA connections
- live order routing
- API key handling
- real webhooks
- startup tasks or scheduled tasks without separate approval
- silent background execution
- autonomous retry without operator authorization

---

## Standardization

- Pipeline stages must follow the defined order — no skipping.
- Each stage must produce a defined output before the next stage begins.
- Any FAIL stops the pipeline immediately — fail-safe behavior.
- Business GPT controls retries — workers must not self-retry.
- Human Owner is the only approval authority for APPLY, COMMIT, and PUSH.
- Validator output is evidence only — it is not approval.
