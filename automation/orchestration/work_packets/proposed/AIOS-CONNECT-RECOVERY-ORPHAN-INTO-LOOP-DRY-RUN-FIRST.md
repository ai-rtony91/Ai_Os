CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. docs/governance/AI_OS_REPO_MEMORY.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_CONNECT_RECOVERY_ORPHAN

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-CONNECT-RECOVERY-ORPHAN-INTO-LOOP-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West recovery wiring lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_CONNECT_RECOVERY_ORPHAN

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Two built recovery and hygiene components are present but unwired, leaving
recovery signal and relay-task hygiene incomplete. This packet, DRY_RUN-first,
connects the recovery readiness signal so the loop or restart path can read it,
and wires the orphan reclaim into the hygiene phase so each cycle sweeps stranded
relay tasks. It is ELEVATED RISK because orphan reclaim and any hygiene wiring
edit the protected night cycle and may move relay tasks, so it requires DRY_RUN
first and gating before any APPLY.

OBJECTIVE (definition of done):
The recovery readiness signal is consumed as a read-only surfaced view in the loop
log, and the orphan reclaim is wired into the hygiene phase so each cycle reports
stranded relay tasks. DRY_RUN-first with a STOP before APPLY and a separate APPLY
approval. In DRY_RUN the orphan sweep reports stranded tasks only and moves
nothing. Recovery readiness consumption is read-only signal surfacing only and
triggers no restart or resume action.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- The recovery readiness composer
  automation/orchestration/coordination_spine/Invoke-AiOsRecoveryBootstrap.DRY_RUN.ps1
  has zero callers. It produces a recovery readiness view but nothing consumes it.
- Reclaim-AiOsOrphans at automation/orchestration/recovery/Reclaim-AiOsOrphans.ps1
  has zero callers and is not in the night-cycle phase list, so tasks stranded in
  the relay running directory are never swept.
- The standalone automation/recovery/Resume-AiOsCycle.ps1 is dead with zero callers
  and is superseded by the in-process Resolve-AiOsCrashRecovery used inside the
  night cycle. Note it for retirement only. Do not wire it in this packet.
- The night-cycle phase list already contains a hygiene phase, which is the
  intended host for the orphan sweep surfacing.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, a thin connection
of the recovery readiness signal into the loop log and a wiring of the orphan
reclaim into the hygiene phase so each cycle reports stranded relay tasks. Reuse
the existing recovery readiness composer and the existing orphan reclaim script.
Phase 1 produces design plus preview diff plan plus rollback note plus validator
and test plan, then STOPS for Human Owner approval. The orphan sweep in DRY_RUN
reports stranded relay running tasks only and moves nothing until APPLY. Recovery
readiness consumption in this packet is read-only signal surfacing only and does
not trigger a restart or a resume.

DESIGN SCOPE (Phase 1, design only):
- A thin composer or phase that reads the recovery readiness view and surfaces it
  in the loop log as a read-only signal. No restart action. No resume action.
- A DRY_RUN orphan sweep that lists stranded relay running tasks by reading the
  relay running directory and reporting candidates. It moves nothing in DRY_RUN.
- A preview diff plan for the smallest safe edit to wire the orphan sweep into the
  hygiene phase and to surface the recovery readiness signal.
- A rollback note describing how to revert the wiring cleanly.
- A test plan covering the DRY_RUN surfacing, the empty-candidate case, and the
  stranded-candidate report case.

COLLISION WARNING (record and honor):
The Human Owner is working locally near recovery and telemetry. APPLY must confirm
the working tree is clear and STOP on collision risk before any wiring edit.

ALLOWED PATHS (write boundary):
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/coordination_spine/`
- `automation/orchestration/recovery/`
- `tests/orchestration/`
- `Reports/coordination_spine/`

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
- `automation/orchestration/locks/`
- `automation/orchestration/dispatcher/`
- `automation/orchestration/scheduler/`
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
- DRY_RUN default. Phase 1 produces design and a preview diff plan only, no
  mutation. STOP before APPLY.
- Night-cycle and relay edits are owner updates requiring explicit APPLY approval.
- The orphan sweep in DRY_RUN moves nothing. It reports stranded relay running
  tasks only.
- Recovery readiness consumption is read-only surfacing only and triggers no
  restart or resume.
- Do not wire the dead automation/recovery/Resume-AiOsCycle.ps1. Note it for
  retirement only.
- Honor the STOP kill-switch control/self_continuation/STOP.
- Atomic writes only. No scheduler registration. No live sends. No broker. No
  secrets.
- Coordinate with operator local work and STOP on collision risk.
- Do not merge, close, draft, rebase, or comment on other PRs.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, commit, push, or merge. This packet does
not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- Read `automation/orchestration/recovery/Reclaim-AiOsOrphans.ps1`
- Read `automation/orchestration/coordination_spine/Invoke-AiOsRecoveryBootstrap.DRY_RUN.ps1` if present
- Run `git status` to confirm the tree is clear of operator local work

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the preview diff plan,
the rollback note, and the validator and test plan. Then STOP for Human Owner
approval.

PHASE 2 (only after a separate explicit APPLY approval naming this packet ID):
implement the smallest safe wiring, run the validator chain and tests, and stop
before commit, push, or merge unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-CONNECT-RECOVERY-ORPHAN-INTO-LOOP-DRY-RUN-FIRST.md`
- PowerShell parser check on every changed .ps1 file in Phase 2
- `python -m pytest tests/orchestration` for the new surfacing and sweep tests in Phase 2
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/coordination_spine/connect_recovery_orphan_design_dry_run.md`
- `Reports/coordination_spine/connect_recovery_orphan_validator_result.example.json`

FORBIDDEN ACTIONS:
- Do not move any relay task in DRY_RUN.
- Do not trigger a restart or a resume from the recovery readiness surfacing.
- Do not wire the dead Resume-AiOsCycle script.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not commit, push, or merge without separate explicit approval.
- Do not store secrets, and do not enable broker, live, or webhook behavior.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, rollback note, and
validator result. Stop immediately if preflight state does not match this packet,
if the working tree is not clear of operator local work, if a relay-task move
appears in DRY_RUN scope, if a restart or resume action appears in scope, if a
scheduler appears in scope, if validation fails, or if APPLY approval is not
explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the confirmation that the working
tree is clear, the rollback note, and the validator chain.

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
