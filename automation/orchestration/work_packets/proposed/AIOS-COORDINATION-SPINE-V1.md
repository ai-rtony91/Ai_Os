CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. docs/governance/AI_OS_REPO_MEMORY.md
3. assigned lane instructions
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_COORDINATION_SPINE_V1

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-COORDINATION-SPINE-V1

MODE: DRY_RUN-FIRST

ZONE: West coordination spine lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_COORDINATION_SPINE

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Human Owner directive to close the loops between systems that already exist, by
building one additive coordination spine that composes the existing queue,
lock, dispatcher, recovery, and packet-factory systems into one coordinated view.
This is Big Pack Mode per AGENTS.md section 3: one large controlled workload per
objective. The build is additive-only and must not delete, change, duplicate, or
edit any current authority file.

DUPLICATE-INTENT RECON EVIDENCE (read-only, completed before this packet):
Three read-only recon lanes mapped the canonical owners on main. Key results:
- An existing closed-loop spine already exists:
  automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1
  composes worker assignment, ownership lock, validator plan, approval plan,
  commit-package preview, and resume pointer, output-restricted to
  telemetry/auto_loop/reports. This packet EXTENDS that model and must not create
  a second spine.
- The dispatcher plus lock write-path integration is already specified as an
  un-applied proposed packet:
  automation/orchestration/work_packets/proposed/AIOS-T2B-ASSIGNMENT-LOCK-INTEGRATION-DRY-RUN-FIRST.md
  This packet must NOT re-specify that integration. Modules 2 and 3 below are
  read and report composers only and defer the assignment-plus-lock write path to
  that existing T2B packet.
- All readers the spine needs already exist (queue scanner, lock status, work
  packet state, cycle marker, runtime heartbeat, dispatcher decision, glue and
  auto-loop factories, approval inbox helpers). The only missing pieces are thin
  composer, mapping, and reporting seams.
Conclusion: duplicate-intent search is clean for the NEW composer seams below, and
flags two pre-existing owners to reuse, not rebuild (the repo loop spine and the
T2B integration packet).

CANONICAL OWNER MAP (reuse by reading or invoking, never edit here):
- Unified queue projection: services/python_supervisor/queue_scanner.py scan_queue
  over automation/orchestration/work_packets/active. State store folders active,
  blocked, complete. Read helper automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1.
- Worker lock: automation/orchestration/locks with Claim-AiOsFileLock.DRY_RUN.ps1,
  Release-AiOsFileLock.DRY_RUN.ps1, Get-AiOsWorkerLockStatus.DRY_RUN.ps1, and
  FILE_LOCK_REGISTRY.json. Adjacent lanes: packet lock under scripts, worker claim
  under automation/orchestration/claims, instance lock under automation/orchestration/lock.
- Lead dispatcher: brain automation/orchestration/dispatcher/assignment_executor.py
  read-only json decision, hand automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1.
  Canonical lane decision docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md.
- Recovery: in-process resume Resolve-AiOsCrashRecovery inside
  automation/orchestration/Invoke-AiOsNightCycle.ps1, marker control/cycle/last_marker.json,
  heartbeat reader automation/orchestration/Test-AiOsRuntimeHeartbeat.DRY_RUN.ps1.
- Packet factory: Operation Glue automation/orchestration/glue and Auto-Loop
  automation/orchestration/auto_loop. Approval terminus
  automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json with helper
  New-AiOsPacketApprovalRequest.DRY_RUN.ps1.
- Existing spine to extend: automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1.
- Daily snapshot reporting: the canonical daily data snapshot added under
  automation/reporting is reused for the spine report rollup.

OBJECTIVE (definition of done):
A DRY_RUN-first coordination spine exists as thin additive composer seams that
read and aggregate the existing systems into one coordinated spine report, with no
edit to any existing authority file, no scheduler, no live behavior, and a separate
APPLY gate per module. Phase 1 produces design plus preview diff plan plus a
DRY_RUN spine report, then STOPS for Human Owner approval.

MISSION:
Implement, DRY_RUN-first and only after explicit per-module APPLY approval, five
thin coordination modules plus one spine orchestrator that extends the existing
repo loop spine model. Each module composes existing readers and tools as child
invocations and emits a new report or index file in the new spine namespace only.
Reuse before adding. Run a duplicate-intent search before creating any file. If a
required owner update to an existing file is discovered, do not edit it; record the
required owner update and STOP for Human Owner approval.

FIVE MODULES (each DRY_RUN-first, each with its own APPLY gate):
MODULE 1 UNIFIED QUEUE INDEX. Read the existing queue projection (queue_scanner
scan_queue, or Get-AiOsWorkPacketState read-only) and emit a NEW unified index file
in the spine namespace that maps existing states to the target set QUEUED, RUNNING,
BLOCKED, WAITING_APPROVAL, COMPLETE, FAILED, ARCHIVED. The mapping layer lives only
in the new file. Do not edit queue_scanner, packet JSONs, or state folders.
MODULE 2 WORKER LOCK STATUS COMPOSER. Read and aggregate the four existing lock
sublanes (file lock, packet lock, worker claim, instance lock) via their existing
read-only status scripts and emit a unified lock view. Mutation stays inside the
existing Claim and Release scripts. The assignment-plus-lock write integration is
owned by the existing proposed packet AIOS-T2B and is out of scope here.
MODULE 3 LEAD DISPATCHER COMPOSER. Invoke the existing dispatcher brain
assignment_executor.py json mode read-only to capture the next-work decision plus
safety verdict, and present it in the spine report. The assign then lock then track
write path is owned by the existing proposed packet AIOS-T2B, named here as the
prerequisite. This module does not mutate assignment or lock state.
MODULE 4 RECOVERY BOOTSTRAP COMPOSER. Aggregate the existing readers for marker,
queue, locks, active packet, and heartbeat into one recovery-bootstrap view, using
the proven compose-by-child-invocation pattern of Invoke-AiOsReadOnlyStatus.DRY_RUN.ps1.
Do not edit the night cycle or the recovery scripts. The restart trigger arming is
out of scope because it would require a scheduler.
MODULE 5 PACKET FACTORY UNIFIER. Read detection evidence (self heal report, queue
BLOCKED and STALE items, autonomy bridge state), generate a goal intake record in
the spine namespace, invoke the existing Operation Glue or Auto-Loop generator, and
emit one unified factory ledger plus a candidate approval recommendation through the
existing approval inbox helper. Do not write the canonical approval inbox file. Add
no third generator.
SPINE ORCHESTRATOR. Extend the existing repo loop spine model by composition: a new
orchestrator that runs modules 1 through 5 in sequence and emits one spine report.
Do not edit Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1 unless a required owner update is
proven and approved separately.

ALLOWED PATHS (write boundary):
- `automation/orchestration/coordination_spine/`
- `tests/orchestration/`
- `Reports/coordination_spine/`
- `telemetry/coordination_spine/`
- `docs/architecture/` for one new additive spine decision record only, no edits to existing files there

FORBIDDEN PATHS (no create, edit, or delete here; read-only invocation of existing scripts is allowed and required):
- `AGENTS.md`
- `RISK_POLICY.md`
- `README.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `.github/`
- `.githooks/`
- `.git/`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `control/cycle/`
- `automation/orchestration/work_packets/`
- `services/python_supervisor/queue_scanner.py`
- `automation/orchestration/queue/`
- `automation/orchestration/command_queue/`
- `automation/orchestration/dispatcher/`
- `automation/dispatcher/`
- `services/dispatcher/`
- `services/runtime/`
- `automation/orchestration/locks/`
- `automation/orchestration/lock/`
- `automation/orchestration/claims/`
- `automation/locks/`
- `automation/orchestration/recovery/`
- `automation/recovery/`
- `automation/orchestration/self_heal/`
- `automation/orchestration/approval_inbox/`
- `control/operation_glue/`
- `automation/orchestration/glue/`
- `automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1`
- `apps/dashboard/`
- `tools/android/`
- `automation/orchestration/scheduler/`
- `secrets/`
- `credentials/`
- `.env`
- `.env.*`
- `broker/`
- `OANDA/`
- `live_trading/`
- `webhooks/`

HARD LIMITS (a violation fails this packet):
- Additive-only. Create files only in the allowed write boundary. Read or invoke
  existing scripts as child processes; never edit, delete, rename, or move them.
- No edits to existing runtime, queue, lock, dispatcher, recovery, or approval
  authority files. If a required owner update is discovered, record it and STOP for
  Human Owner approval instead of editing.
- DRY_RUN report first. Phase 1 produces design and a DRY_RUN report with no
  mutation. Each module gets its own separate APPLY approval later.
- No scheduler, service, cron, or systemd registration of any kind.
- No ADB or SOS activation. No dashboard changes. No broker, no live order path, no
  webhook behavior. No secrets.
- Do not run an unbounded or unattended run.
- No commit, no push, no merge by the worker.
- Honor the STOP kill-switch control/self_continuation/STOP.
- All new index and report writes must be atomic, temp then rename.
- Run a duplicate-intent search before creating any file; if an existing owner is
  found, STOP and report instead of creating a parallel spine or a duplicate file.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY, separately for each module.
A validator PASS is evidence only and does not approve APPLY, commit, push, merge,
hook install, approval-inbox mutation, scheduler registration, live notification,
live trading, or secret handling. This packet does not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID and the exact module.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1`
- Read `automation/orchestration/Invoke-AiOsReadOnlyStatus.DRY_RUN.ps1`
- Read `services/python_supervisor/queue_scanner.py`
- Read `automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1`
- Read `automation/orchestration/dispatcher/assignment_executor.py`
- Read `automation/orchestration/work_packets/proposed/AIOS-T2B-ASSIGNMENT-LOCK-INTEGRATION-DRY-RUN-FIRST.md`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a preview diff plan per
module, a duplicate-intent search evidence list, and one DRY_RUN spine report that
reads the existing systems and shows the composed view. Then STOP for Human Owner
approval.

PHASE 2 (only after a separate explicit APPLY approval naming this packet ID and the
specific module): implement that one module as additive new files, run the validator
chain and tests, and stop before commit, push, or merge unless that same approval
explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-COORDINATION-SPINE-V1.md`
- duplicate-intent search evidence using `rg` over the proposed names, folders, and lanes before any file creation
- PowerShell parser check on every new .ps1 file in Phase 2
- `python -m py_compile` on every new .py file in Phase 2
- JSON parse validation on every new index, ledger, or schema file
- read-only invocation of the existing validator router for evidence
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/coordination_spine/coordination_spine_v1_design_dry_run.md`
- `Reports/coordination_spine/coordination_spine_v1_dry_run_report.example.json`
- `Reports/coordination_spine/coordination_spine_v1_duplicate_intent_evidence.md`

FORBIDDEN ACTIONS:
- Do not create a second or parallel spine.
- Do not edit any existing queue, lock, dispatcher, recovery, approval, runtime, or
  spine file.
- Do not re-specify the dispatcher plus lock write integration owned by AIOS-T2B.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not activate ADB or SOS, do not change the dashboard.
- Do not enable broker work, live order paths, or webhook behavior, and do not store
  secrets.
- Do not commit, push, or merge.

STOP POINT:
Stop after producing the Phase 1 design, per-module preview diff plan, duplicate
intent evidence, and the DRY_RUN spine report. Stop immediately if preflight branch
or worktree state does not match this packet, if a duplicate owner is found for a
proposed file, if a required edit to a forbidden path is discovered, if any
scheduler, ADB, SOS, dashboard, broker, or secret scope appears, if validation
fails, or if APPLY approval is not explicit and module-specific.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID and the specific module, the exact allowed paths, and the
validator chain. Approval of one module does not approve another module.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
DUPLICATE-INTENT EVIDENCE:
CANONICAL OWNERS REUSED:
PER-MODULE STATUS:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
