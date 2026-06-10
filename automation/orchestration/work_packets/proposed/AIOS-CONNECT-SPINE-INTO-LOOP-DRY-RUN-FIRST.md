CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. README.md
4. docs/context/AI_OS_CURRENT_STATE_FOR_CLAUDE.md
5. assigned lane instructions
6. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_CONNECT_SPINE_INTO_LOOP

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-CONNECT-SPINE-INTO-LOOP-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West spine-loop wiring lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_CONNECT_SPINE_INTO_LOOP

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Human Owner directive to close the keystone connection gap M1. The coordination
spine is BUILT and on main but it is standalone observation with no engine. It has
ZERO callers and ZERO references inside the night cycle phase list. This packet
designs the wiring that runs the spine refresh each cycle, DRY_RUN-first and
observe-only, so the spine stops being a parked artifact and becomes a live but
read-only telemetry refresh step in the loop.

KEYSTONE GAP EVIDENCE (read-only recon, completed before this packet):
- The spine orchestrator exists on main at
  automation/orchestration/coordination_spine/Invoke-AiOsCoordinationSpine.DRY_RUN.ps1
  alongside its composer scripts for the unified queue index, unified lock status,
  lead dispatch view, recovery bootstrap view, and packet factory view.
- A repo-wide search for Invoke-AiOsCoordinationSpine finds references only in
  tests, Reports, and telemetry, never inside
  automation/orchestration/Invoke-AiOsNightCycle.ps1.
- A search inside the night cycle file for CoordinationSpine, coordination_spine,
  and RepoLoopSpine returns no matches. The night cycle phase list named
  AiOsPhaseNames contains hygiene, clear-stale-approvals, pull-backlog,
  relay-runner, approval-resume, relay-runner-resume-drain, self-continuation,
  night-supervisor, autonomy-bridge, morning-brief, sos-file-notifier, pr-watch,
  and has no spine phase.
Conclusion: the spine is built and parked. The connection seam into the loop is the
only missing piece. There is no second spine to build here.

ONE-SPINE RECONCILIATION NOTE (reuse, do not duplicate):
A second related spine exists at
automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1.
This packet must reconcile naming toward one spine and must not create a third
spine. The night cycle phase invokes the existing coordination spine orchestrator
only. If the two spine names overlap in responsibility, record the reconciliation
in the design output and propose one canonical spine name; do not silently fork.

COLLISION WARNING (must be recorded and re-checked at APPLY):
The Human Owner is concurrently working locally in the coordination_spine area and
in night-cycle telemetry. APPLY must confirm the working tree is clear of that work
before editing the night cycle, and STOP if a collision risk is detected.

OBJECTIVE (definition of done for Phase 1):
A DRY_RUN-first design that wires one new OBSERVE-ONLY night-cycle phase which
invokes the existing coordination spine orchestrator to refresh the spine telemetry
views each cycle, with a preview diff plan, a clean rollback note, and a test plan.
Phase 1 produces design only and STOPS for Human Owner approval. No mutation of the
night cycle occurs in Phase 1.

MISSION:
The coordination spine, consisting of the unified queue index, the unified lock
status, the lead dispatch view, the recovery bootstrap composers, and the
orchestrator Invoke-AiOsCoordinationSpine, is BUILT and on main but has zero callers
and zero references in the night cycle phase list. It is standalone observation with
no engine. This packet wires the spine INTO the loop so the loop runs the spine
refresh each cycle. This is ELEVATED RISK because it edits the protected night cycle
as an owner update, not an additive new file, so it requires DRY_RUN-first and
maximum gating. The new spine phase must be OBSERVE-ONLY first. It only runs the
spine orchestrator to refresh the spine telemetry views. It does NOT act on those
views. It does NOT mutate queue, lock, dispatch, approval, or recovery state. The
loop does not yet act on the views.

DESIGN SCOPE (Phase 1, design only, no mutation):
- Design one new night-cycle phase that invokes
  automation/orchestration/coordination_spine/Invoke-AiOsCoordinationSpine.DRY_RUN.ps1
  in its default DRY_RUN observe-only behavior to refresh the spine views each cycle.
  Run it without the Apply switch so it stays read-only and only refreshes telemetry
  views and reports. The loop does not act on the refreshed views in this phase.
- Place the new phase so it runs the spine refresh once per cycle and follows the
  existing Invoke-AiOsStep and Complete-AiOsSkippedPhase patterns already used in the
  night cycle, including the day-observer skip behavior and the cycle marker plus
  heartbeat updates, so the phase is consistent with the existing phase list named
  AiOsPhaseNames.
- Reconcile spine naming so there is one spine. Record any overlap between the
  coordination spine orchestrator and the repo loop spine and propose one canonical
  name. Do not create a second or third spine.
- Provide a preview diff plan describing the exact lines to add to the phase list and
  the exact step invocation block to add, with no curly-brace literals and no edits
  applied in Phase 1.
- Provide a rollback note showing the phase can be removed cleanly by deleting the
  added phase-list entry and the added step block, returning the night cycle to its
  prior state with no residue.
- Provide a test plan covering a PowerShell parser check on the changed night cycle,
  a dry-run cycle that confirms the spine phase refreshes views without mutating
  queue, lock, dispatch, approval, or recovery state, and a confirmation that the
  spine phase honors the day-observer skip and the STOP kill-switch.

ALLOWED PATHS (write boundary):
- automation/orchestration/Invoke-AiOsNightCycle.ps1 (owner update, Phase 2 only, separate explicit APPLY)
- automation/orchestration/coordination_spine/
- tests/orchestration/
- Reports/coordination_spine/

FORBIDDEN PATHS (no create, edit, or delete; read-only invocation of existing scripts is allowed):
- AGENTS.md
- RISK_POLICY.md
- README.md
- WHITEPAPER.md
- ARCHITECTURE.md
- .github/
- .githooks/
- .git/
- automation/orchestration/approval_inbox/
- automation/orchestration/work_packets/
- automation/orchestration/queue/
- automation/orchestration/dispatcher/
- automation/dispatcher/
- automation/orchestration/locks/
- automation/orchestration/scheduler/
- control/cycle/
- apps/dashboard/
- tools/android/
- secrets/
- credentials/
- .env
- .env.*
- broker/
- OANDA/
- live_trading/
- webhooks/

HARD LIMITS (a violation fails this packet):
- DRY_RUN default. Phase 1 is design only with no mutation. STOP before APPLY.
- The night-cycle edit is an owner update requiring its own explicit APPLY approval.
- The spine phase is OBSERVE-ONLY and must not act on or mutate any queue, lock,
  dispatch, approval, or recovery state. It only refreshes spine telemetry views.
- Do not create a second spine. Reconcile toward one spine.
- Honor the STOP kill-switch control/self_continuation/STOP.
- All writes in any later phase must be atomic, temp then rename.
- No scheduler, service, cron, or systemd registration.
- No live sends and no live notification behavior change.
- No broker work and no live order path.
- No secrets handling.
- Coordinate with the operator local work and STOP on collision risk.
- Do not merge, close, or comment on other PRs.
- No commit, no push, no merge by the worker.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is evidence
only and does not approve APPLY, the night-cycle owner update, scheduler
registration, live notification, live trading, or secret handling. This packet does
not state that the Human Owner explicitly approves commit, push, or merge here. Each
of commit, push, and merge requires a separate explicit Human Owner approval naming
this packet ID.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-CONNECT-SPINE-INTO-LOOP-DRY-RUN-FIRST.md
- PowerShell parser check on the changed night cycle in Phase 2
- pytest in Phase 2 over tests/orchestration/
- git diff --check

PREFLIGHT (read-only, before any APPLY work):
- Read AGENTS.md
- Read RISK_POLICY.md
- Read README.md
- Read automation/orchestration/Invoke-AiOsNightCycle.ps1
- Read automation/orchestration/coordination_spine/Invoke-AiOsCoordinationSpine.DRY_RUN.ps1 if present
- Read automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1
- Run git status to confirm the working tree is clear of operator local spine work

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design for the new
OBSERVE-ONLY spine phase, the preview diff plan, the rollback note, the test plan,
the one-spine reconciliation note, and the collision check. Then STOP for Human
Owner approval.

PHASE 2 (only after a separate explicit APPLY approval naming this packet ID): apply
the owner update that adds the OBSERVE-ONLY spine phase to the night cycle, run the
PowerShell parser check and pytest and git diff --check, and stop before commit,
push, or merge unless that same approval explicitly authorizes them.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, rollback note, test
plan, one-spine reconciliation note, and collision check. Stop immediately if
preflight branch or worktree state does not match this packet, if git status shows
operator local spine or night-cycle telemetry work that could collide, if a second
spine would be created, if a required edit to a forbidden path is discovered, if any
scheduler, dashboard, broker, live notification, or secret scope appears, if
validation fails, or if APPLY approval is not explicit for the night-cycle owner
update.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
COLLISION CHECK:
REUSED VS ADDED:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH

SAFE NEXT ACTION: run the validator on this packet path, then STOP and present the Phase 1 design for Human Owner APPLY approval of the night-cycle owner update; do not edit the night cycle until that approval is explicit.
