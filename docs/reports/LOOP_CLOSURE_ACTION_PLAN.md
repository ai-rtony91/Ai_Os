# Loop Closure Action Plan

Packet: AIOS-OPERATION-GLUE-FORENSICS-DRYRUN-001
Mode: DRY_RUN report creation only

## Objective

Close operation-glue fractures without weakening AI_OS safety boundaries.

This is not an APPLY packet list. This is the forensic action order for future approved work.

## Design Rule

Do not make preview scripts mutate state just to create motion.

Close the loop by creating one state contract and one event-backed handoff path first. Then connect existing scripts to that path in small approved APPLY lanes.

## Dependency Order

### Step 1: Define One Closed-Loop State Contract

Target handoff chain:

```text
packet_created
queued
assigned
executing
validation_required
validation_passed
approval_requested
approved
commit_package_ready
human_review_required
complete
```

Why it matters:

- Current status names disagree across packet mover, runtime advancement, dispatcher queue, and TypeScript queue.
- A shared state contract prevents unsafe automatic advancement.

Evidence:

- `Move-AiOsPacketState.ps1`
- `Invoke-AiOsRuntimePacketAdvancement.ps1`
- `services/dispatcher/packetQueue.ts`
- `automation/orchestration/queue/DISPATCHER_QUEUE.json`

Risk: high. This touches orchestration semantics in future APPLY, so it must start as DRY_RUN/schema only.

### Step 2: Create Packet-to-Queue Projection

Goal:

Use `automation/orchestration/work_packets/` as packet source and project it into one canonical queue read model.

Why it matters:

- This is the first hard break.
- Work exists as files, but scheduler/worker layers do not consume a single authoritative queue.

Initial safe behavior:

- Read-only projection.
- No packet mutation.
- No worker launch.
- No approval mutation.

Expected output:

- pending/active/blocked/approval-waiting/validated/complete/dead-letter counts.
- normalized status from existing packet files.

### Step 3: Connect Scheduler to Queue Projection

Goal:

Pass packet queue snapshot into the scheduler path.

Why it matters:

- `autonomousScheduler.ts` already supports `packetQueueSnapshot`.
- `runtimeTick.ts` currently does not pass it.

Initial safe behavior:

- Scheduler preview consumes projection and emits planned actions only.
- No dispatch or inbox mutation.

### Step 4: Connect Scheduler Actions to Worker Resolver

Goal:

For each dispatch action, call or model the worker resolver and produce an assignment preview.

Why it matters:

- Scheduler can say "dispatch," and worker resolver can select a worker, but no glue connects them.

Initial safe behavior:

- Assignment preview only.
- Unknown owner becomes `manual_review`, not fallback-to-default.

### Step 5: Create a Governed Worker Assignment Writer

Goal:

Persist assignment only after safe approval gates.

Why it matters:

- Current inbox add script is preview-only by design.
- A separate APPLY-safe writer is needed later, not a mutation added to the DRY_RUN script.

Initial safe behavior:

- Only docs/tests/report lanes.
- No runtime, trading, broker, secrets, protected governance, commit, push, merge, or deploy.

### Step 6: Wire Worker Completion to Validator Routing

Goal:

When worker output exists, determine required validators from changed files, packet risk, and allowed paths.

Why it matters:

- Validator recommender exists but runs against whole repo dirty state.
- It needs packet scope.

Initial safe behavior:

- Validator route recommendation only.
- Packet-specific evidence path.

### Step 7: Persist Validator Evidence

Goal:

Write validator results to a packet-specific evidence record.

Why it matters:

- Approval and commit package layers need stable evidence, not terminal text.

Initial safe behavior:

- Read-only validator execution.
- Evidence file only under approved reports/evidence path.

### Step 8: Restore/Define Active Approval Inbox

Goal:

Resolve the mismatch around `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`.

Why it matters:

- Active-system-map lists it as active.
- Current inspected repo has an archive copy and active gate file, but not active inbox file.

Initial safe behavior:

- DRY_RUN mismatch report first.
- Future APPLY only after explicit approval.

### Step 9: Connect Approval Request to Approval Inbox

Goal:

Approval request preview becomes a durable inbox item through an approved writer.

Why it matters:

- `New-AiOsPacketApprovalRequest.DRY_RUN.ps1` currently previews only.
- Approval processor scans a different approval file family.

Initial safe behavior:

- Human review required.
- No self-approval.

### Step 10: Connect Approved Packet and Validator Evidence to Commit Package Builder

Goal:

Commit package recommendation accepts packet id, validator evidence, approval id, and allowed file list.

Why it matters:

- Current recommender scans Git status and can mix unrelated backlog.

Initial safe behavior:

- Recommendation only.
- No staging, commit, push, PR creation, merge, or deployment.

## Top 10 Easiest Fixes

These are easiest because they can be done as DRY_RUN/schema/report work before runtime mutation.

1. Add a normalized packet state mapping table.
2. Add a read-only packet queue projection report.
3. Make scheduler preview consume the read-only projection.
4. Make worker assignment preview consume scheduler actions.
5. Add packet id to validator recommendation inputs.
6. Add packet-scoped validator evidence output format.
7. Add approval inbox mismatch DRY_RUN verifier.
8. Add approval request persistence design without implementing it.
9. Add commit package parameters for packet id/evidence path in DRY_RUN.
10. Add loop closure score fields to morning brief/report only.

## Highest-Leverage Fix

Build a read-only canonical queue projection from work packets.

Why:

- It closes the first hard break without mutating runtime state.
- It gives scheduler, worker resolver, approval, validator, recovery, Night Supervisor, and scorecard one shared read model.
- It keeps current packet files intact.

## MCP Position

MCP is not the immediate loop closure fix.

MCP should come before agent autonomy as a safe hands layer, but the operation-glue blocker is internal state continuity. A read-only MCP server can help inspect files. It cannot decide which of the current packet, command queue, dispatcher queue, worker inbox, approval, and telemetry surfaces is authoritative.

Recommended MCP posture:

- Continue MCP Safe Hands documentation/checklist.
- Do not install MCP yet.
- Do not use MCP as a substitute for queue/event/state reconciliation.

## Stop Conditions For Future APPLY

Future APPLY work must stop immediately if it attempts to:

- mutate active packet state without explicit packet path and approval.
- write worker inbox assignment without an approved assignment writer.
- write approval inbox without an approved approval lane.
- run worker execution.
- stage, commit, push, merge, deploy, or create PRs.
- touch trading, broker, OANDA, secrets, credentials, live orders, paper order path, or runtime execution.

## Safe First Future Lane

The exact first future lane should be DRY_RUN, not APPLY:

```text
AIOS-CANONICAL-QUEUE-PROJECTION-DRYRUN-001
```

Scope:

- inspect `automation/orchestration/work_packets/`
- inspect queue/status schemas
- produce a normalized read-only queue projection report
- do not mutate packets, queues, worker inbox, approval inbox, runtime, telemetry, Git, or MCP

Reason:

This attacks the first hard break and reduces the most human coordination without crossing safety boundaries.
