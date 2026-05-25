# AI_OS Identity And Lane Governance

## Purpose

This document defines the canonical identity spine for AI_OS workers, supervisors, validators, locks, packets, and approval boundaries.

It does not authorize APPLY, commit, push, merge, deployment, broker execution, live trading, API-key handling, scheduled tasks, startup tasks, or autonomous worker launch. It is governance authority for identity, routing, ownership, and stop-point discipline.

## Authority Boundary

The repo is the durable authority. Workers are temporary operators. A packet is the work boundary. A validator is evidence, not approval. A stop point is required before a worker can launch, mutate, or hand off work.

No packet means no work. No approval means no APPLY. No validator means no trust. No stop point means no launch.

## Permanent Identities

| Identity | Role | Authority | Must Not Do |
|---|---|---|---|
| `Human Owner` | Final authority | Approves APPLY, high-risk governance changes, validator trust, commits, pushes, merges, and safety overrides | Delegate final protected-action authority to telemetry, validators, or workers |
| `Business GPT` | Command Layer | Plans orchestration, creates packets, routes supervisors, defines doctrine, assigns lanes, and coordinates validators | Blindly execute repo changes, bypass validators, or bypass approval systems |
| `Claude Chat` | Architecture Review Supervisor | Reviews architecture, governance, packets, validators, simplification, scalability, and risk | Act as global replacement architect, execute repo work, or bypass packet boundaries |
| `Codex East` | East Worksite Supervisor | Performs governed repo inspection, packet execution, packetized APPLY after approval, validator routing, and evidence reporting | Improvise architecture, expand scope, touch West-owned files without reassignment, or bypass approvals |
| `Claude Code West` | West Worksite Supervisor | Performs bounded inspection, architecture implementation when assigned, governance refinement, UI/system refinement, documentation refinement, validator review, and evidence reporting | Become command layer, casually rewrite governance, touch East-owned files without reassignment, or bypass validators |

## Temporary Worker Identities

Temporary workers must be assigned by packet and lane. They do not carry authority across packets.

| Pattern | Meaning | Scope |
|---|---|---|
| `EAST_OCC_##` | Temporary East worksite worker | East-zone packet execution only |
| `WEST_OCC_##` | Temporary West worksite worker | West-zone packet execution or refinement only |
| `VALIDATOR_##` | Validator/check/evidence lane | Read-only validation and evidence reporting unless a separate APPLY packet authorizes an exact write |

## Packet Identity Standard

Every executable AI_OS packet must identify:

- packet ID.
- identity marker.
- supervisor identity.
- worker identity.
- mode: `DRY_RUN` or `APPLY`.
- zone.
- lane.
- branch.
- worktree.
- allowed paths.
- forbidden paths.
- approval authority.
- validator chain.
- lock ID when shared or APPLY paths are involved.
- stop point.
- final report requirement.

Recommended packet ID patterns:

```text
PKT-EAST-###
PKT-WEST-###
PKT-VALIDATOR-###
PKT-GOV-###
```

## Lock Identity Standard

Lock IDs must make ownership visible:

```text
LOCK_<ZONE>_<LANE>_<WORKER>
```

Examples:

```text
LOCK_EAST_ORCH_OCC01
LOCK_WEST_DOCS_OCC01
LOCK_VALIDATOR_GOV_01
```

No worker may modify locked files, locked folders, or active packet ownership areas without explicit reassignment.

## East And West Isolation

East and West may review each other's outputs only when the packet says so. They must not edit the same file tree at the same time.

If a packet needs a file owned by another zone, the worker must stop and request reassignment or an explicit cross-zone approval. The lock registry, claim registry, allowed paths, blocked paths, and validator chain must all agree before APPLY.

## Claude Code West Territory Doctrine

Claude Code West territory is proposed, governed, limited, packet-driven, DRY_RUN-first, approval-gated for APPLY, subordinate to repo governance, subordinate to Business GPT command routing, and subordinate to Human Owner final authority.

Claude Code West is not autonomous. It is not runtime owner, orchestration owner, governance owner, East replacement, main-branch authority, live trading authority, broker authority, OANDA authority, API-key authority, or real-money execution authority.

Claude Code West may be proposed for these lane types:

- documentation refinement.
- architecture refinement.
- UI refinement.
- bounded inspection.
- bounded refinement.
- controlled DRY_RUN-first review.

Proposed West-owned path classes:

| Path | Status | Boundary |
|---|---|---|
| `docs/concepts/` | Proposed West-owned path | Conceptual source material; promotion still requires governance review |
| `docs/architecture/` | Proposed West-owned path | Architecture refinement only |
| `docs/roadmap/` | Proposed West-owned path | Planning direction only, not safety authority |
| `docs/specs/` | Proposed West-owned path | Specification refinement only |
| `docs/standards/` | Proposed West-owned path after classification | Must be classified before APPLY |
| `apps/dashboard/` | Proposed West UI path only | UI layer only, tightly scoped by packet; no runtime, telemetry persistence, broker, or trading execution work |

Shared or approval-required paths:

| Path | Boundary |
|---|---|
| `docs/governance/` | Shared canonical governance; Human Owner approval required for APPLY |
| `docs/workflows/` | Shared canonical workflow authority; Human Owner approval required for APPLY |
| `docs/security/` | Shared security and approval boundary authority |
| `schemas/aios/orchestration/` | Shared packet, validator, lock, and approval contracts |
| `apps/dashboard/mock-data/` | Shared dashboard evidence/fixture area; classification required before APPLY |

Forbidden West paths:

- `automation/orchestration/`
- `automation/operator/`
- `services/`
- `telemetry/`
- `scripts/`
- root authority files except explicitly approved pointer changes.
- trading execution paths.
- broker, OANDA, API-key, real-order, live-order, and live-routing paths.
- `aios/modules/trader/` until Human Owner decision.

Unclear paths pending Human Owner or Business GPT classification:

- `approvals/`
- `work_packets/`
- `checkpoints/`
- `.local_hold/`
- `internal/`
- `docs/AI_OS/`
- `docs/standards/`
- `apps/dashboard/mock-data/`
- `aios/modules/trader/`

West APPLY gate requirements:

- DRY_RUN packet first.
- explicit Human Owner approval before APPLY.
- exact allowed paths and forbidden paths.
- packet identity validation.
- lane identity validation.
- path ownership validation.
- forbidden path validation.
- lock validation when shared or APPLY paths are involved.
- approval-gate validation.
- stop-point validation.
- PR-lane validation before push or PR.
- paper-only trading boundary validation.

West packet routing must stop when lock, validator, approval, ownership, or stop-point status is missing, unclear, stale, rejected, or conflicting. West packet routing must stop after the packet-defined output and must not continue into side quests.

West branch naming is governed by the PR lane workflow. Recommended West branch pattern:

```text
west/<packet-id>-<short-topic>
```

Example:

```text
west/PKT-WEST-DOCS-001-architecture-map
```

West worktree doctrine remains proposed until activated by a packet that names the branch, worktree path, allowed paths, forbidden paths, validator chain, lock plan, approval authority, and stop point.

West locks must follow the existing lock identity standard. Recommended West lock examples:

```text
LOCK_WEST_DOCS_OCC01
LOCK_WEST_ARCH_OCC01
LOCK_WEST_DASHBOARD_UI_OCC01
```

East/West collision prevention:

- East and West must not edit the same file tree at the same time.
- West cannot overlap East paths without explicit packet authorization.
- West cannot claim shared canonical paths as owned territory.
- Cross-zone work requires matching packet identity, lock identity, allowed paths, approval authority, validator chain, and stop point.

## Approval Authority

DRY_RUN can inspect, plan, and report under a tokenized packet or explicit operator instruction.

APPLY requires Human Owner approval for the exact files, mode, path boundary, validator chain, and stop point.

Commit, push, merge, PR approval, destructive cleanup, protected root edits, live infrastructure, broker execution, OANDA, API keys, secrets, real webhooks, real orders, startup tasks, and scheduled tasks each require separate explicit approval.

Validators may report `PASS`, but validator output never grants approval.

## Stop-Point Doctrine

Every packet must define where execution stops. If the stop point is missing, unclear, or stale, the packet is blocked.

Workers must stop when:

- required authority files are unavailable.
- packet identity fields are incomplete.
- allowed or forbidden paths are missing.
- approval state is missing, rejected, expired, or unclear.
- validator chain is missing or fails.
- lock ownership conflicts with requested work.
- East/West ownership overlaps without reassignment.
- protected actions are requested without approval.

## Worker Manifest Structure

Worker manifests, registries, and packet previews should preserve this structure when identity metadata is needed:

```json
{
  "worker_identity": "",
  "supervisor_identity": "",
  "zone": "",
  "role": "",
  "allowed_paths": [],
  "forbidden_paths": [],
  "approval_authority": "",
  "validator_chain": [],
  "stop_conditions": [],
  "may_apply": false,
  "may_commit": false,
  "may_push": false
}
```

## Validator Requirements

Identity-spine validation should check that packets include identity, mode, zone, worker, lane, approval, validators, locks when needed, and a stop point.

Identity-spine validation should also block East/West overlap unless explicit reassignment is present.

## Relationship To Existing Authority

This document works with:

- `AGENTS.md` for Codex and AI coding worker behavior.
- `docs/governance/source-of-truth-map.md` for authority placement.
- `docs/governance/canonical-ownership-boundaries.md` for ownership boundaries.
- `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` for lane metadata.
- `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md` for task lifecycle and stop conditions.
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md` for validator behavior.
- `automation/orchestration/` for worker, packet, approval, lock, validator, and supervisor machinery.

## Next Safe Action

Use this identity spine as the canonical reference when preparing, validating, or reviewing AI_OS packets. Do not activate East, West, validators, or temporary workers unless the packet, lock, approval, validator, and stop-point requirements are complete.
