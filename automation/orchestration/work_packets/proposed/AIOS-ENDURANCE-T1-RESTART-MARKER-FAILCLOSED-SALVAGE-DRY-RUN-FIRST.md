CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_ENDURANCE_T1_RESTART_SALVAGE

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-T1-RESTART-MARKER-FAILCLOSED-SALVAGE-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance hardening lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_TIER1_RESTART_SALVAGE

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main after PR 447 and PR 456 are merged, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Salvage extraction approved by the Human Owner from held PR 449
(feature/tier1-crash-safe-restart-v1), classified PRE-PACKET OVERLAP / SALVAGE
CANDIDATE. This packet extracts only the high-value restart and atomic-write
hardening ideas from PR 449 into the governed authority lane established by
merged PR 456. PR 449 is read for ideas only. This packet does NOT merge,
close, draft, rebase, push, or comment on PR 449 or PR 451.

OBJECTIVE (definition of done):
Harden the already-merged Tier 1 crash-safe restart path (from PR 447) so the
night-cycle loop fails closed on unsafe restart markers and writes runtime state
with a collision-safe atomic temp path, reusing the existing PowerShell
night-cycle and runtime-state files already on main. No new parallel restart
runtime. No CI workflow edits. DRY_RUN-first with a STOP before APPLY.

GROUNDED FINDINGS (already verified; do NOT re-derive, do NOT duplicate):
- Merged PR 447 added `Resolve-AiOsCrashRecovery` plus a temp-then-rename atomic
  write. Build ON it; do not replace it.
- Held PR 449 demonstrated stronger fail-closed restart handling and a
  collision-safe temp path. Those IDEAS are the salvage scope below. Its parallel
  Python restart runtime and its CI workflow edit are explicitly out of scope.
- The existing watchdog and supervisor on main remain the reuse target; this
  packet does not add a parallel architecture.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, the five salvage
items below by editing only the existing PowerShell night-cycle and runtime-state
files on main, plus validator-only or test-only proof. No parallel Python restart
runtime is permitted; a restart-safety check may exist only as validator-only or
test-only code. Reuse before adding.

SALVAGE SCOPE (Phase 1 design targets):
1. Fail closed on corrupt restart marker. In
   `automation/orchestration/Invoke-AiOsNightCycle.ps1`, a cycle marker that
   cannot be parsed must block automatic restart and resume and must surface an
   explicit blocked reason such as BLOCKED_RESTART_MARKER_CORRUPT rather than
   silently continuing.
2. Fail closed on WAITING_FOR_APPROVAL restart marker. If the prior marker phase
   state indicates waiting for approval, `Resolve-AiOsCrashRecovery` must stop and
   must not auto-resume through the approval gate; surface
   BLOCKED_RESTART_WAITING_FOR_APPROVAL.
3. Fail closed on stale restart marker. A marker older than an explicit,
   documented bounded threshold (proposed default 86400 seconds, which is 24
   hours) must block auto-resume and surface BLOCKED_RESTART_MARKER_STALE. The
   threshold must be a named, documented value.
4. Preserve cycle_id on restart. When adopting an in-progress marker, the prior
   cycle_id must be preserved even when completed phases are zero, so completed
   phase evidence keeps matching and APPLY phases are not replayed.
5. Strengthen atomic state write. In
   `automation/runtime/state/Write-AiOsRuntimeState.ps1`, use a collision-safe
   temp path (GUID-suffixed or equivalent) for the temp-then-rename write,
   preserve temp-then-rename behavior, and ensure the parent directory exists only
   where writing is already allowed.
6. Add validator-only or test-only proof for items 1 through 5 in the repo-native
   style. No parallel runtime module.

ALLOWED PATHS:
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/runtime/state/Write-AiOsRuntimeState.ps1`
- `automation/validators/`
- `tests/`
- `Reports/endurance_tier1/`

FORBIDDEN PATHS:
- `AGENTS.md`
- `README.md`
- `RISK_POLICY.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `.github/`
- `.github/workflows/`
- `.githooks/`
- `.git/`
- `automation/orchestration/restart_safety/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/workers/`
- `automation/orchestration/work_packets/active/`
- `automation/orchestration/work_packets/blocked/`
- `automation/orchestration/work_packets/complete/`
- `automation/orchestration/night_supervisor/`
- `automation/orchestration/locks/`
- `telemetry/night_supervisor/`
- `.env`
- `.env.*`
- `secrets/`
- `credentials/`
- `broker/`
- `OANDA/`
- `live_trading/`

HARD LIMITS (a violation fails this packet):
- DRY_RUN is the default. Phase 1 produces design plus a preview diff plan plus a
  validator and test plan only. No file mutation in Phase 1.
- STOP before APPLY. APPLY requires a separate explicit Human Owner approval
  naming this packet ID.
- No CI workflow edits. No edits under `.github/` of any kind.
- Reuse the existing PowerShell night-cycle and runtime-state path on main. No new
  parallel Python restart runtime; restart-safety code may exist only as
  validator-only or test-only.
- All state-file writes MUST stay atomic (temp then rename). Parent-directory
  creation only where writing is already allowed.
- Honor the STOP kill-switch `control/self_continuation/STOP`.
- Do not merge, close, convert to draft, rebase, push, or comment on PR 449 or
  PR 451.
- No scheduler registration. No live notifications. No broker work. No secrets.
- No live trading.

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, commit, push, merge, hook install,
approval-inbox mutation, worker-queue mutation, Night Supervisor mutation,
scheduler registration, live notification, live trading, or secret handling. This
packet does not state that the Human Owner explicitly approves commit, push, or
merge; those require a separate explicit approval naming this packet ID.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- Read `automation/runtime/state/Write-AiOsRuntimeState.ps1`
- Read `automation/orchestration/watchdog/README.md`
- Read `automation/recovery/Resume-AiOsCycle.ps1`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a preview diff plan
for the five salvage items, and a validator and test plan. Then STOP for Human
Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
edits to the two existing PowerShell files plus validator-only or test-only proof,
run the validator chain and tests, and stop before commit, push, or merge unless
that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-T1-RESTART-MARKER-FAILCLOSED-SALVAGE-DRY-RUN-FIRST.md`
- PowerShell parse check on every changed .ps1 file (the same syntax gate the CI validate job runs) in Phase 2
- Repo-native validator-only or test-only run for the five salvage items in Phase 2
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/endurance_tier1/restart_marker_failclosed_salvage_design_dry_run.md`
- `Reports/endurance_tier1/restart_marker_failclosed_salvage_validator_result.example.json`

FORBIDDEN ACTIONS:
- Do not edit any CI workflow or anything under `.github/`.
- Do not add a parallel Python restart runtime module.
- Do not merge, close, draft, rebase, push, or comment on PR 449 or PR 451.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not enable live notifications or auto-approve anything.
- Do not change packet, approval, lock, or worker-queue flow.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, and validator result.
Stop immediately if preflight branch or worktree state does not match this packet,
if dirty files overlap the mission unsafely, if a required authority file is
missing, if validation fails, if a secret-like value appears, if any scheduler or
live notification appears in scope, if a CI workflow edit appears in scope, if a
parallel restart runtime appears in scope, if live trading or broker work appears,
or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the stale-marker threshold value,
and the validator chain.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
REUSED VS ADDED:
SALVAGE COVERAGE CHECKLIST:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
