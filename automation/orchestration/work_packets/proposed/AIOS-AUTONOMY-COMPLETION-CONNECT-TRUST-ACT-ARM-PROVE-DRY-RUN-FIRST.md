CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. docs/governance/AI_OS_REPO_MEMORY.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_AUTONOMY_COMPLETION_CONNECT_TRUST_ACT_ARM_PROVE

SUPERVISOR IDENTITY: Codex East

PACKET ID: AIOS-AUTONOMY-COMPLETION-CONNECT-TRUST-ACT-ARM-PROVE-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: East autonomy completion lane

WORKER IDENTITY: EAST_OCC_01

LANE: AI_OS_AUTONOMY_COMPLETION

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Read-only discovery on current main found that the autonomy parts now exist
(control plane, router, discovery gap-to-goal feeder, autonomy loop, packet auto
runner) but almost nothing is connected, armed, or proven. The night cycle runs
none of the autonomy brain, several built components have zero callers, the
dispatcher decision never becomes an assignment, self heal apply is a no operation,
the operator cannot be woken, the loop cannot start itself, and no real cycle has
ever run. The remaining work is not more parts. It is five themes: connect, trust,
act, arm, prove. Codex East runs this on the local machine where the runtime and
PowerShell live.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate; reuse owners):
- Control plane, autonomy_router, autonomy_discovery, autonomy_loop, and
  packet_runner are merged on main. Reuse them. Do not rebuild.
- The night cycle Invoke-AiOsNightCycle.ps1 has zero references to the coordination
  spine or the autonomy control plane. The brain is not wired to the body.
- Zero caller components to connect: Invoke-AiOsImprovementLoopPreview,
  Invoke-AiOsExecutionPipelinePreview, New-AiOsWorkerPacketFromGoal,
  Get-AiOsMissionNextAction, Reclaim-AiOsOrphans. Self heal apply is a no operation.
- The following are already owned by separate queued packets and must be referenced,
  not duplicated here: completion evidence validator
  (AIOS-SELFBUILD-COMPLETION-EVIDENCE-VALIDATOR), dispatcher to assign integration
  (AIOS-T2B-ASSIGNMENT-LOCK-INTEGRATION), SOS arming
  (AIOS-ENDURANCE-SOS-TELEGRAM-ARMING-V2), and the soak harness first run proof
  (AIOS-ENDURANCE-SOAK-HARNESS-FIRST-RUN-PROOF).

OBJECTIVE (definition of done):
The merged autonomy parts are connected into one running loop, the loop can verify
its own work, decisions become actions, the unattended layer is designed and gated,
and a path to the first real proof exists. DRY_RUN-first, additive where possible,
each theme a separate APPLY gate. Scheduler activation, SOS live arming, and the
real run are NOT activated in this packet.

MISSION:
Implement, DRY_RUN-first and only after explicit per-module APPLY approval, the five
completion themes by connecting and gating the existing merged parts. Reuse before
adding. Run a duplicate intent search before creating any file. If a required owner
update to a protected file is discovered, do not edit it silently; record it and
STOP for Human Owner approval. Confirm the working tree is clear of operator local
work in coordination_spine, telemetry, and the proposed packet edits, and STOP on
collision risk.

FIVE THEMES (each DRY_RUN-first, each its own APPLY gate):
THEME 1 CONNECT (keystone, this packet owns it). Add an observe-only night cycle
phase that runs the autonomy control plane and the coordination spine refresh each
cycle, so the loop drives the brain instead of leaving it standalone. Connect the
zero caller components by composing them through the control plane or the loop:
Get-AiOsMissionNextAction for the next action surface, Reclaim-AiOsOrphans for the
hygiene sweep, and the preview generators as read only inputs. This edits the
protected night cycle as an owner update and must be observe only, mutating no
queue, lock, approval, or dispatch state.
THEME 2 TRUST (reference owner, do not duplicate). Wire the completion evidence
validator owned by AIOS-SELFBUILD-COMPLETION-EVIDENCE-VALIDATOR into the control
plane outcome classification once that packet is applied, so a run is marked
complete only when evidence verifies it. If that validator is not yet on main,
record the dependency and stop that sub item.
THEME 3 ACT (gated, mostly reference owners). The dispatcher to assignment write
path is owned by AIOS-T2B and must be applied there, not here. In this packet,
promote self heal apply from a no operation to a real, bounded, gated heal for a
small safe class such as recreating a missing expected directory, and wire the
improvement loop and execution pipeline previews from preview only into a gated
proposal that emits a goal or packet candidate rather than a silent action.
THEME 4 ARM (design only here). Produce the design and the gating for the
unattended layer. SOS live arming is owned by AIOS-ENDURANCE-SOS-TELEGRAM-ARMING-V2
and is referenced, not implemented here. Scheduler or autostart registration is a
final Human Owner step and is DESIGN ONLY in this packet; it is not registered or
activated.
THEME 5 PROVE (design only here). Reference the soak harness first run proof packet
AIOS-ENDURANCE-SOAK-HARNESS-FIRST-RUN-PROOF and document the readiness checklist
that must pass before the first real supervised run. The actual run is a Human Owner
action on the local machine and is not performed in this packet.

ALLOWED PATHS (write boundary; owner updates require their own approval):
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/autonomy_control_plane/`
- `automation/orchestration/autonomy_router/`
- `automation/orchestration/autonomy_discovery/`
- `automation/orchestration/coordination_spine/`
- `automation/orchestration/improvement_loop/`
- `automation/orchestration/execution_pipeline/`
- `automation/orchestration/self_heal/`
- `automation/orchestration/recovery/`
- `tests/orchestration/`
- `Reports/autonomy_control_plane/`
- `Reports/autonomy_completion/`
- `telemetry/autonomy_control_plane/`

FORBIDDEN PATHS:
- `AGENTS.md`
- `RISK_POLICY.md`
- `README.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `.github/`
- `.githooks/`
- `.git/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/work_packets/`
- `automation/orchestration/scheduler/`
- `automation/dispatcher/`
- `automation/orchestration/dispatcher/`
- `automation/orchestration/locks/`
- `services/python_supervisor/notifier.py`
- `control/cycle/`
- `apps/dashboard/`
- `tools/android/`
- `secrets/`
- `credentials/`
- `.env`
- `.env.*`
- `broker/`
- `OANDA/`
- `live_trading/`
- `webhooks/`

HARD LIMITS (a violation fails this packet):
- DRY_RUN default. Phase 1 produces design and a preview diff plan only. Each theme
  is a separate explicit APPLY approval.
- The CONNECT night cycle phase is observe only. It must not mutate queue, lock,
  approval, dispatch, or recovery state. It only runs the brain to refresh views and
  surface the next action.
- Do not implement the dispatcher to assignment write path here. It is owned by
  AIOS-T2B. Do not arm SOS here. It is owned by the SOS packet. Do not register or
  activate a scheduler. Do not perform the real run. Those are referenced only.
- Reuse the merged control plane, router, discovery, loop, and packet runner. No new
  parallel brain. Run a duplicate intent search before any file creation.
- Self heal real apply, if implemented, must be bounded to a small safe class, must
  be opt in behind an explicit flag, and must never delete user work or mutate
  protected state.
- Confirm the working tree is clear of operator local work and STOP on collision
  risk. Honor the STOP kill switch control/self_continuation/STOP.
- No live sends. No broker. No secrets. No live trading.
- Do not merge, close, draft, rebase, push, or comment on other PRs.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY, separately for each theme. A
validator PASS is evidence only and does not approve APPLY, commit, push, merge,
scheduler registration, live notification, live trading, or secret handling. This
packet does not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID and the specific theme.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- Read `automation/orchestration/autonomy_control_plane/Invoke-AiOsAutonomyControlPlane.DRY_RUN.ps1`
- Read `automation/orchestration/autonomy_router/Get-AiOsAutonomyNextAction.DRY_RUN.ps1`
- Read `automation/orchestration/self_heal/Invoke-AiOsSelfHeal.DRY_RUN.ps1`
- Confirm the working tree is clear of operator local self-build work

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a per-theme preview
diff plan, the owner dependency list for the referenced packets, the collision
check, and the validator and test plan. Then STOP for Human Owner approval.

PHASE 2 (only after a separate explicit APPLY approval naming this packet ID and the
specific theme): implement that one theme, run the validator chain and tests, and
stop before commit, push, or merge unless that same approval explicitly authorizes
them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-AUTONOMY-COMPLETION-CONNECT-TRUST-ACT-ARM-PROVE-DRY-RUN-FIRST.md`
- PowerShell parser check on every changed .ps1 file in Phase 2
- `python -m pytest tests/orchestration` for the new and affected tests in Phase 2
- `python -m pytest tests` full suite before any commit
- a collision and forbidden path assertion proving the diff stays in allowed paths
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/autonomy_completion/autonomy_completion_design_dry_run.md`
- `Reports/autonomy_completion/autonomy_completion_owner_dependency_map.md`

FORBIDDEN ACTIONS:
- Do not register or activate any scheduler, service, cron, or systemd unit.
- Do not arm SOS, email, push, android, broker, live order, or webhook behavior.
- Do not implement the dispatcher to assignment write path here.
- Do not perform the first real run here.
- Do not commit, push, or merge without separate explicit approval.
- Do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, per theme preview diff plan, owner
dependency map, collision check, and validator result. Stop immediately if preflight
state does not match this packet, if a collision with operator local work is
detected, if a forbidden path or owner duplication would occur, if scheduler, SOS,
real run, or dispatcher write path appears in scope for execution, if validation
fails, or if APPLY approval is not explicit and theme specific.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID and the specific theme, the exact allowed paths, the observe
only constraint for the night cycle phase, and the validator chain.

FINAL REPORT FORMAT:
SUMMARY:
EXISTING PARTS REUSED:
PER-THEME STATUS:
OWNER DEPENDENCY MAP:
FILES CREATED:
FILES MODIFIED:
COLLISION CHECK:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
