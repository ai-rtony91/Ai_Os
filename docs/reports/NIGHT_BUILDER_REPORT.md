# Night Builder Report

Packet: AIOS-AUTONOMY-DOCS-SYNTHESIS-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Current Safety Answer

Supervised overnight development is not currently safe.

Supervised overnight read-only inspection is closer, but still provisional. The repo has an Overnight Supervisor workflow, schemas, Python supervisor skeleton, qualification gates, and report artifacts. It does not yet have a qualified queue/event/recovery foundation, safe MCP hands, or real multi-night evidence.

Allowed now: report-only, human-triggered DRY_RUN architecture and readiness reports.
Not allowed now: unattended worker execution, queue mutation, approval mutation, packet movement, commits, pushes, PR creation, deployment, scheduler persistence, daemon behavior, or MCP server installation.

## Existing Night Builder Assets

| Asset | Status | Evidence |
|---|---|---|
| Overnight workflow | EXISTS | `docs/workflows/AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md` |
| Autonomy levels | EXISTS | `docs/governance/AI_OS_AUTONOMY_LEVELS.md` |
| Qualification gates | EXISTS | `docs/governance/AIOS_NIGHT_SUPERVISOR_QUALIFICATION_GATES.md` |
| Overnight report schema | EXISTS | `schemas/aios/orchestration/overnight_supervisor.schema.json` |
| Python supervisor skeleton | PARTIAL | `services/python_supervisor/README.md`, supervisor modules |
| Morning brief artifacts | PARTIAL | `telemetry/night_supervisor/` untracked local backlog |
| Runtime supervisor code | PARTIAL | `services/supervisor/runtimeSupervisor.ts` |
| Scheduler code | PARTIAL | `services/dispatcher/autonomousScheduler.ts` |
| Recovery/remediation planning | PARTIAL | `services/runtime/autonomousRemediation.ts`, `docs/workflows/SAFE_REPAIR_AND_RECOVERY_STANDARD.md` |

## Blockers

1. No active MCP read-only hands.
2. No runtime-loadable knowledge graph.
3. No single canonical durable queue projection.
4. No append-only orchestration event log that all layers consume.
5. Worker registry and window identity registry still overlap.
6. Approval inbox active file is missing from the expected active path.
7. Validator routing is rules-plus-scripts, not a closed autonomous selection loop.
8. Recovery is awareness-first and not qualified for automatic repair.
9. SOS-only policy is not a canonical file yet.
10. Autonomy scorecard does not exist.
11. Night Supervisor qualification gates are not completed or promoted.
12. Untracked local backlog exists under `telemetry/night_supervisor/` and `docs/reports/`, so overnight state must not assume clean repo.

## Steel Door Rules

The steel door is the set of irreversible or money-critical actions AI_OS must never let an agent reach automatically.

Steel door actions:

- live trading
- paper or real order path mutation
- broker or OANDA integration
- real webhooks or real orders
- secrets, credentials, API keys, OAuth secrets
- production deployment
- protected main push
- merge
- destructive cleanup
- startup tasks, scheduled tasks, daemons, uncontrolled background loops
- approval mutation without human approval
- queue/packet/lock mutation without approved APPLY

Everything else is a wooden door only when it is reversible, scoped, validated, and isolated to an approved branch or generated evidence path.

## SOS-Only Definition

The repo does not yet have a canonical `docs/security/sos-escalation-policy.md`. Because this packet is report-only, this report defines the needed policy but does not create it.

Recommended SOS triggers:

1. State corruption that cannot be safely rebuilt from append-only evidence.
2. Conflict arbitration cannot resolve by approved rules.
3. Same packet fails validation beyond retry ceiling.
4. Any task requires crossing the steel door.
5. Spend, time, or execution budget ceiling hit with critical work pending.
6. Self-audit finding is outside the narrow auto-remediable set.
7. Recovery supervisor or event log fails.
8. Unknown ownership on a file required for APPLY.
9. Approval mismatch or missing approval for protected work.
10. Evidence conflict between repo state and generated reports.

Everything else should eventually be handled silently by detection, bounded retry, queue state, and morning reporting. AI_OS is not there yet.

## What Can Run Unattended Later

Only after Phase 0-6 foundation gates:

- read-only repo and evidence inspection
- stale packet detection
- worker heartbeat review
- validator recommendation
- approval queue summary
- commit package candidate detection without staging
- packet draft preview
- morning brief generation
- autonomy scorecard update
- report writing to approved generated evidence paths

These may run unattended only when the event log, queue projection, MCP path, validator path, and stop controls are proven.

## What Must Remain Human-Gated Forever

- APPLY to protected paths
- staging exact files
- commit
- push
- PR creation until explicitly separately approved
- merge
- deployment
- credentials and secrets
- broker, OANDA, webhook, order path, live trading
- destructive file or Git operations
- governance authority changes
- promotion from TESTED to TRUSTED or QUALIFIED

## Night Builder Readiness By Phase

| Phase | Readiness | Reason |
|---|---|---|
| Read-only morning brief | YELLOW | Workflow and schemas exist; MCP and evidence gates missing. |
| Packet draft preview | YELLOW | Intake and proposal helpers exist; graph and approval integration incomplete. |
| Validator routing | YELLOW | Chain and router rules exist; no closed trigger loop. |
| Commit package preparation | YELLOW | Commit package recommender exists; not dependency-aware. |
| Recovery awareness | YELLOW | Supervisor code exists; auto-recovery not qualified. |
| Overnight execution | RED | Worker launch, queue mutation, PR creation, scheduler persistence remain blocked. |
| SOS-only operation | RED | Requires event log, queue, recovery, self-audit, scorecard, and qualification ledger. |

## Safe Night Builder Architecture Model

```text
MCP Safe Hands (read-only evidence)
-> Knowledge Graph (what exists, owns, depends, protects)
-> Event Log (facts emitted by systems)
-> Queue Projection (what work exists now)
-> Worker Registry (who can safely handle what)
-> Validator Router (what evidence is needed)
-> Recovery Supervisor (what can be retried, quarantined, or escalated)
-> Approval Intelligence (what Anthony should decide)
-> Commit Package Builder (what is ready for exact-file review)
-> Morning Brief and Scorecard (what happened and what still needs humans)
```

## Final Night Builder Verdict

AI_OS should not attempt "work while Anthony sleeps" as code execution yet.

The safe first Night Builder milestone is:

```text
Night Builder Read-Only:
one manually approved run that reads approved evidence,
produces a morning brief,
drafts packet previews,
flags SOS items,
and writes no queue, approval, worker, Git, runtime, trading, broker, or secret state.
```
