CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_WEEKEND_RESTART_TIMEOUTS

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-WEEKEND-RESTART-SUPERVISOR-TIMEOUTS-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance weekend lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_WEEKEND_RESTART_TIMEOUTS

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Completes the unfinished items B and C of the merged authority packet
AIOS-ENDURANCE-T1-WEEKEND-CRASH-SURVIVAL. PR 458 delivered the heartbeat
emission and restart-marker hardening (item A) as minimum APPLY scope but did NOT
deliver the armed restart supervisor (item B) or the bounded git and network
timeouts (item C). This packet executes exactly those two items so the
semi-autonomous weekend milestone can close.

OBJECTIVE (definition of done):
The unattended night-cycle loop survives a single crash over a weekend with no
human present: a dead or hung loop is detected and restarted, and a hung git or
network call cannot wedge the loop. Builds on the now-live loop heartbeat and
crash-resume already on main. No OS scheduler, no live sends, no new APPLY
behavior. Every new action is opt-in behind an explicit flag.

GROUNDED FINDINGS (already verified; do NOT re-derive, do NOT duplicate):
- The loop now emits a heartbeat to telemetry/runtime/runtime_heartbeat.json and
  resumes from the cycle marker on restart. The detection signal the watchdog
  reads is therefore live.
- aios_deadman_watchdog.py already DETECTS loop death by heartbeat staleness
  (exit code 2 equals BLOCKED). It is detect-only and has no caller. Reuse it.
- Start-AiOsPersistentRuntimeSupervisor.ps1 is a fixed-count loop, not a
  death-restart supervisor. Reuse its loop and audit-log patterns; do not fork a
  new paradigm.
- night_supervisor_harness.py runs about ten git subprocess calls with no
  per-call timeout; only one JSON-parse subprocess has a timeout. A hung git call
  blocks the live loop indefinitely.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, the armed
restart supervisor and the bounded timeouts, plus tests and docs, by composing
the existing components. Reuse before adding. Phase 1 produces design plus
preview diff plan plus validator and test plan, then STOPS for Human Owner APPLY
approval.

WORK ITEMS:
B. ARMED RESTART SUPERVISOR. Add a manually-launched supervisor loop that, on an
   interval, runs aios_deadman_watchdog.py; on BLOCKED it restarts the night-cycle
   driver, which then auto-resumes from the marker. It MUST: honor the STOP
   kill-switch control/self_continuation/STOP and exit immediately if STOP exists;
   use exponential backoff between restarts; enforce a maximum restart count per
   window, then stop and write a local alert; default to a DRY_RUN that only logs
   a would-restart line and takes no action; require an explicit -ArmRestart or
   -Apply flag to actually restart. It must NOT register any scheduler.
C. BOUNDED TIMEOUTS. Add one reusable bounded-timeout helper and apply it to the
   git and network subprocess calls in night_supervisor_harness.py and any other
   hot-path git calls reached by the night-cycle children. A hung call must time
   out, be killed, and return a logged non-zero result rather than wedging the
   loop. Catch the timeout exception explicitly.
D. RESILIENCE PLUMBING. Add a try-and-catch error boundary around the per-cycle
   work so a transient phase failure does not kill the loop, and wire the existing
   Reclaim-AiOsOrphans recovery so tasks stranded in the relay running directory
   are swept each cycle.
E. TESTS AND DOCS. Prove in the repo-native style: the supervisor in DRY_RUN logs
   a would-restart line and takes no action; the timeout helper returns non-zero
   on a hung command; the error boundary keeps the loop alive on a transient
   failure. Update the watchdog README with the manual launch command and an
   explicit not-auto-registered, opt-in note.

ALLOWED PATHS:
- `automation/orchestration/watchdog/`
- `automation/orchestration/runtime/`
- `automation/orchestration/night_supervisor/`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/recovery/`
- `automation/shared/`
- `tests/`
- `Reports/endurance_weekend/`

FORBIDDEN PATHS:
- `.github/`
- `.github/workflows/`
- `.githooks/`
- `.git/`
- `AGENTS.md`
- `RISK_POLICY.md`
- `README.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `secrets/`
- `credentials/`
- `.env`
- `.env.*`
- `broker/`
- `OANDA/`
- `live_trading/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/locks/`

HARD LIMITS (a violation fails this packet):
- Never run or register schtasks, Register-ScheduledTask, New-Service, sc.exe,
  cron, or systemd. The restart supervisor is a manually-launched loop only.
- DRY_RUN is the default. The restart action is opt-in behind an explicit flag;
  default is detect-and-log only.
- Honor the STOP kill-switch control/self_continuation/STOP everywhere; never
  restart past STOP.
- All state-file writes MUST be atomic, temp then rename.
- Reuse the existing watchdog and supervisor and recovery components; no new
  parallel runtime.
- No live notifications. No broker work. No secrets. No live trading.
- Do not merge, close, draft, rebase, push, or comment on other PRs.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, commit, push, merge, hook install,
approval-inbox mutation, scheduler registration, live notification, live trading,
or secret handling. This packet does not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- Read `automation/orchestration/watchdog/aios_deadman_watchdog.py`
- Read `automation/orchestration/watchdog/README.md`
- Read `automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1`
- Read `automation/orchestration/night_supervisor/night_supervisor_harness.py`
- Read `automation/orchestration/recovery/Reclaim-AiOsOrphans.ps1`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the preview diff
plan, and the validator and test plan. Then STOP for Human Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
edits and tests, run the validator chain and tests, and stop before commit, push,
or merge unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-WEEKEND-RESTART-SUPERVISOR-TIMEOUTS-DRY-RUN-FIRST.md`
- `python automation/orchestration/watchdog/aios_deadman_watchdog.py --threshold-seconds 600`
- PowerShell parse check on every changed .ps1 file in Phase 2
- Repo-native tests for the supervisor, timeout helper, and error boundary in Phase 2
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/endurance_weekend/restart_supervisor_timeouts_design_dry_run.md`
- `Reports/endurance_weekend/restart_supervisor_timeouts_validator_result.example.json`

FORBIDDEN ACTIONS:
- Do not register any scheduler, service, cron, or systemd unit.
- Do not add a parallel runtime; reuse the existing watchdog and supervisor.
- Do not enable live notifications or auto-approve anything.
- Do not change packet, approval, lock, or worker-queue flow.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, and validator result.
Stop immediately if preflight branch or worktree state does not match this packet,
if dirty files overlap the mission unsafely, if a required authority file is
missing, if validation fails, if a secret-like value appears, if any scheduler or
live notification appears in scope, if a parallel runtime appears in scope, if
live trading or broker work appears, or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the restart arming flag, the
backoff and max-restart values, and the validator chain.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
REUSED VS ADDED:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
WEEKEND SOAK INSTRUCTIONS:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
