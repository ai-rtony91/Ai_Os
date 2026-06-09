CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_DISPATCH_CLOSURE

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-T2-DISPATCH-CLOSURE-WORKERSTATE-CITESTS-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West dispatch closure lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_DISPATCH_CLOSURE

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Dispatch-layer closure approved by the Human Owner as the next durability task.
This packet consolidates three disconnected dispatch implementations into one
canonical, tested, closed loop. It reuses existing lanes and components and does
not add a fourth parallel dispatch lane. This packet does not merge, close,
draft, rebase, or comment on any pull request.

OBJECTIVE (definition of done):
Turn the work-execution layer into one durable, tested, closed loop so the system
can advance work unattended for twenty-four hours. The end state has one chosen
canonical dispatch lane, a runtime tick that no longer throws on the first tick,
a seeded runtime state directory under Reports, atomic worker-state writes,
fail-safe worker-state readers, real cross-process file locking enforced inside
the assignment mutator, idempotency keys plus stranded-task recovery in the relay
lane, and a continuous-integration test design recommended as a Human-Owner
manual step. DRY_RUN-first with a STOP before APPLY.

GROUNDED FINDINGS (already verified in this worktree; do NOT re-derive):
- There are three disconnected dispatch implementations today. A Python analyzer
  lane under automation/orchestration/dispatcher/ only previews. A TypeScript
  runtime lane under services/dispatcher/ and services/runtime/ throws a type
  error on the first tick of every run. A PowerShell mutator lane under
  automation/dispatcher/runtime/ has no backing runtime state directory under
  Reports, so its assign and heartbeat scripts cannot run.
- The TypeScript scheduler reads a stale-assigned-packets field at
  services/dispatcher/autonomousScheduler.ts line 58 from its worker-lease input,
  and the resume engine reads an invalid-packet-statuses field at
  services/dispatcher/packetResumeEngine.ts line 55 from its runtime input. Both
  fields are absent from their source types, so the first tick fails the type
  contract.
- The PowerShell worker heartbeat writer at
  automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1 writes
  worker state with a direct, non-atomic Set-Content call near line 59, with no
  temp-then-rename, so a crash mid-write can corrupt worker state.
- The proven atomic pattern already exists as the cycle-marker temp-then-rename
  write used elsewhere in the runtime, and DRY_RUN lock scripts already exist
  under automation/orchestration/locks/ as Claim-AiOsFileLock.DRY_RUN.ps1,
  Release-AiOsFileLock.DRY_RUN.ps1, and Get-AiOsWorkerLockStatus.DRY_RUN.ps1.
- A canonical loop decision document already exists at
  docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md and is the reuse target for
  recording the chosen lane.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, one durable
tested closed dispatch loop by reusing the existing lanes and components named in
the grounded findings. Do not add a fourth parallel dispatch lane. All worker
and lock and relay state writes must be atomic temp-then-rename. Reuse before
adding. Phase 1 produces design plus a preview diff plan plus a validator and
test plan, then STOPS for Human Owner APPLY approval.

DESIGN SCOPE (Phase 1 design targets):
1. Choose ONE canonical dispatch lane and document the decision in
   docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md. Either fix the TypeScript
   dispatcher type contracts so the runtime tick succeeds by adding the
   stale-assigned-packets field to the worker-lease source type that
   autonomousScheduler.ts reads and adding the invalid-packet-statuses field to
   the runtime source type that packetResumeEngine.ts reads, OR formally shelve
   the TypeScript lane so it cannot be launched accidentally. Record the chosen
   option and the rationale.
2. Create and seed the missing dispatcher runtime state directory under
   Reports/dispatcher/ so the PowerShell assign and heartbeat scripts can run at
   all. Seeding is a directory plus a safe-default state file only.
3. Convert the four worker-state table writes to an atomic temp-file-then-rename
   write, mirroring the proven cycle-marker pattern, and make the readers return
   a safe default plus a present-or-corrupt flag instead of throwing on missing
   or corrupt files.
4. Implement real file-lock claim and release by promoting the existing DRY_RUN
   lock scripts under automation/orchestration/locks/ to enforcing scripts, and
   require lock acquisition inside the assignment mutator at
   automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1 to prevent double
   assignment.
5. Add idempotency keys to the PowerShell assignment task and the relay task, and
   add recovery for tasks stranded in the relay running directory past a
   documented time-to-live threshold. The time-to-live must be a named,
   documented value.
6. Design a continuous-integration test job that runs the existing but currently
   orphaned Python tests under tests/, the night-supervisor harness test, the
   TypeScript typecheck, and the node tests. Editing continuous-integration
   workflow files is forbidden to workers, so this test job is designed and
   recommended as a Human-Owner manual step only and is NOT applied by this
   packet.

ALLOWED PATHS:
- services/dispatcher/
- services/runtime/
- automation/orchestration/dispatcher/
- automation/dispatcher/runtime/
- automation/orchestration/relay/
- automation/orchestration/locks/
- tests/
- Reports/dispatcher/
- docs/architecture/

FORBIDDEN PATHS:
- .github/
- .github/workflows/
- .githooks/
- .git/
- AGENTS.md
- RISK_POLICY.md
- README.md
- secrets/
- credentials/
- .env
- .env.*
- broker/
- OANDA/
- live_trading/
- automation/orchestration/approval_inbox/
- automation/orchestration/night_supervisor/

HARD LIMITS (a violation fails this packet):
- DRY_RUN is the default. Phase 1 produces design plus a preview diff plan plus a
  validator and test plan only. No file mutation in Phase 1.
- STOP before APPLY. APPLY requires a separate explicit Human Owner approval
  naming this packet ID.
- Do NOT edit continuous-integration workflows. The test job is recommended as a
  Human-Owner manual step only. No edits under .github/ of any kind.
- Reuse the existing dispatch lanes and lock and relay components. Do not add a
  fourth parallel dispatch lane.
- All state writes MUST be atomic temp-then-rename. Parent-directory creation
  only where writing is already allowed.
- No scheduler registration. No live sends. No broker work. No secrets.
- Honor the STOP kill-switch control/self_continuation/STOP.
- Preserve all existing safety gates, including the read-only Python executor,
  the approval-gated APPLY, and the blocked broker and live paths.
- Do not merge, close, convert to draft, rebase, or comment on other pull
  requests.
- No live trading.

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, hook install, approval-inbox mutation,
worker-queue mutation, Night Supervisor mutation, scheduler registration, live
sends, live trading, or secret handling. This packet does not request and does
not authorize commit, push, or merge. Any commit, push, or merge happens only if
a separate later approval explicitly approves that specific action and names this
packet ID.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Read README.md
- Read the services/dispatcher/ key files autonomousScheduler.ts,
  packetResumeEngine.ts, workerLeaseEngine.ts, runtimeStateRebuilder.ts, and
  dispatcher.ts
- Read automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1
- Read automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1
- Read automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1
- Read docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md as the canonical loop
  decision

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a preview diff plan
for the six design targets, and a validator and test plan. Then STOP for Human
Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
edits within the allowed paths only, run the validator chain, the PowerShell
parser checks, the Python tests, and the TypeScript typecheck, and STOP. No
commit, push, or merge unless that same approval explicitly approves that
specific action and names this packet ID.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-T2-DISPATCH-CLOSURE-WORKERSTATE-CITESTS-DRY-RUN-FIRST.md
- PowerShell parser checks on every changed .ps1 file in Phase 2
- Python tests for the worker-state and lock and relay changes in Phase 2
- TypeScript typecheck for the dispatcher lane in Phase 2
- git diff --check

EXPECTED OUTPUT FILES (Phase 1):
- Reports/dispatcher/dispatch_closure_design_dry_run.md
- Reports/dispatcher/dispatch_closure_validator_result.example.json

FORBIDDEN ACTIONS:
- Do not edit any continuous-integration workflow or anything under .github/.
- Do not add a fourth parallel dispatch lane.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not enable live sends or auto-approve anything.
- Do not change packet, approval, lock, or worker-queue flow outside the allowed
  paths.
- Do not run live trading or broker work, and do not store secrets.
- Do not merge, close, draft, rebase, or comment on other pull requests.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, and validator result.
Stop immediately if preflight branch or worktree state does not match this
packet, if dirty files overlap the mission unsafely, if a required authority file
is missing, if validation fails, if a secret-like value appears, if any scheduler
or live send appears in scope, if a continuous-integration workflow edit appears
in scope, if a fourth parallel dispatch lane appears in scope, if live trading or
broker work appears, or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the chosen canonical lane, the
stranded-task time-to-live value, and the validator chain.

SAFE NEXT ACTION:
Run the validator chain command on this packet path, then route the Phase 1
design to the Human Owner for explicit APPLY approval. Take no mutating action.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
REUSED VS ADDED:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
