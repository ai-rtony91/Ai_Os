# Disproven Assumptions

Packet: AIOS-MASTER-RECONCILIATION-ROADMAP-DRYRUN-001
Mode: DRY_RUN report creation only

## Purpose

This file records assumptions from the original architecture source material that were corrected by repository evidence and later autonomy reports.

Repository evidence wins.

## Biggest False Assumption

The biggest false assumption was:

```text
AI_OS is missing the major autonomy systems.
```

Corrected finding:

```text
AI_OS has many of the systems. They are not yet operating as one continuous supervised execution loop.
```

The repo problem is operation glue, not blank-slate construction.

## Disproven Assumption Table

| Assumption | Why it was wrong | Evidence | Correct replacement |
|---|---|---|---|
| MCP is the next bottleneck | MCP does not close packet-to-queue, scheduler, approval, validator, or commit handoffs | `OPERATION_GLUE_FORENSICS.md`, `CLOSED_LOOP_BREAKPOINTS.md` | MCP is a safe-hands layer; internal state continuity is first |
| Worker registry duplicate should be deleted | Window identity registry has active consumers and unique display metadata | `DUPLICATE_WORKER_REGISTRY_CLEANUP_PLAN.md` | Keep orchestration registry canonical; demote/rename window registry |
| Queue is absent | Multiple queue stores and packet folders exist | `AUTONOMY_GAP_REPORT.md`, `TOP_50_MICRO_GAPS.md` | Build one canonical projection from existing stores |
| Scheduler is absent | Scheduler code exists but is not fed active packet state | `CLOSED_LOOP_BREAKPOINTS.md` | Feed queue projection into scheduler preview |
| Approval system is absent | Approval model, gate, processor, and scripts exist | `AUTONOMY_GAP_REPORT.md` | Repair active inbox and persistence |
| Commit package builder is absent | Commit package recommender exists | `IMPLEMENTATION_SEQUENCE_REPORT.md` | Add packet/evidence/dependency inputs |
| Recovery must be invented from scratch | Runtime supervisor, rebuilder, remediation, and recovery docs exist | `NIGHT_BUILDER_REPORT.md` | Qualify recovery and bind it to SOS/event log |
| Night Builder can start as execution | Repo doctrine supports read-only/report-first supervision | `NIGHT_BUILDER_REPORT.md` | Start with read-only morning brief |
| More Python is the main missing piece | Python supervisor explicitly does not mutate queues or run as MCP/server/daemon | `MCP_FOUNDATION_REPORT.md`, `TOP_50_MICRO_GAPS.md` | Build state contracts and handoffs first |
| Reports equal runtime authority | Reports are evidence, not consumers or state machines | `TOP_50_MICRO_GAPS.md` | Convert decisions into approved schemas/helpers/APPLY lanes |

## Correct Assumptions Preserved

| Assumption | Status | Why it remains true |
|---|---|---|
| Steel door is permanent | Correct | Trading, broker, secrets, production deploy, protected main, merge, push remain human-gated |
| SOS policy is needed | Correct | Recovery cannot become trusted without escalation boundaries |
| Knowledge graph is foundational | Correct | Routing, approval, validator, conflict, and commit grouping need ownership/dependency facts |
| Event log is foundational | Correct | Recovery, scorecard, scheduler, and approval need durable facts |
| Queue is a foundation layer | Correct | Work must survive process restarts and feed scheduling |
| Human gate remains | Correct | AI_OS prepares decisions; Anthony approves protected actions |
| Autonomy scorecard is needed | Correct | Without metrics, autonomy progress is subjective |
| Night Builder must widen slowly | Correct | Overnight execution remains unsafe until evidence gates pass |

## Main Conflict Reconciliations

### MCP vs Operation Glue

Original source material emphasized MCP as the missing hands layer.

Repo evidence refined that:

- MCP helps inspection and tool access.
- MCP does not choose canonical state.
- MCP does not insert packets into queues.
- MCP does not persist worker assignments.
- MCP does not repair approval inbox.

Decision:

MCP Safe Hands remains important, but the first implementation lane should close internal state vocabulary and queue projection.

### Worker Registry Delete vs Demote

Original source material suspected duplicate worker registries.

Repo evidence showed:

- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` is canonical logical authority.
- `automation/window_identity/AIOS_WORKER_REGISTRY.json` is active display/window support.
- Both have active consumers.

Decision:

Do not delete. Demote/rename the window registry later.

### Queue Missing vs Queue Fragmented

Original source material treated queue/scheduler as likely missing.

Repo evidence showed:

- Work packet folders exist.
- Command queue exists.
- Dispatcher queue exists.
- TypeScript packet queue exists.
- Scheduler exists.

Decision:

The fix is canonical projection and state mapping, not a brand-new queue system.

### Approval Missing vs Approval Disconnected

Original source material described approval intelligence as needed.

Repo evidence showed:

- Approval model and gate exist.
- Approval preview exists.
- Approval processor exists.
- Active approval inbox path is mismatched/missing.

Decision:

Repair persistence and inbox ownership before building intelligence.

## What Should Not Be Preserved

1. The idea that AI_OS needs broad reinvention.
2. The idea that MCP installation should precede internal state repair.
3. The idea that duplicate registries can be solved by deletion.
4. The idea that Night Builder should start by executing code overnight.
5. The idea that commit package readiness can be inferred from raw Git status alone.
6. The idea that validator output is useful enough without packet-scoped evidence.
7. The idea that telemetry visibility equals state authority.

## Final Corrected Model

```text
Existing systems are useful but fragmented.
Fragmented systems need a shared state contract.
The shared state contract feeds canonical queue projection.
Queue projection feeds scheduler.
Scheduler feeds worker assignment preview.
Assignment feeds validation.
Validation feeds approval.
Approval feeds commit package.
Event log and knowledge graph make the loop recoverable and explainable.
MCP reads approved evidence after the safe-hands boundary is proven.
Night Builder starts read-only after the evidence loop is stable.
```
