CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_ENDURANCE_TIER1_WEEKEND

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-T1-WEEKEND-CRASH-SURVIVAL-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance hardening lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_TIER1_WEEKEND

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: claude/tier1-resume-atomic-writes (branch FROM this branch, not main, verified before APPLY by preflight)

SOURCE RECOMMENDATION:
Derived from the AI_OS endurance audit after inspection of
`automation/orchestration/Invoke-AiOsNightCycle.ps1`,
`automation/orchestration/watchdog/aios_deadman_watchdog.py`,
`automation/orchestration/watchdog/README.md`,
`automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1`,
`automation/recovery/Resume-AiOsCycle.ps1`,
`automation/recovery/README.md`, and
`automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1`.

OBJECTIVE (definition of done):
The unattended night-cycle loop must survive a single crash over a 2-day weekend
with no human present: if the loop process dies or hangs, it is detected and
restarted, and on restart it RESUMES from the cycle marker instead of re-running
already-completed APPLY phases. No OS scheduler, no live sends, no new APPLY
behavior. Every new action is opt-in behind an explicit flag.

GROUNDED FINDINGS (already verified by the operator review lane; do NOT re-derive,
do NOT duplicate these components):
- PR 447 already added crash-safe RESUME plus an atomic runtime-state write to
  `Invoke-AiOsNightCycle.ps1` via `Resolve-AiOsCrashRecovery`. Build ON it. This
  is why the packet branches from `claude/tier1-resume-atomic-writes`.
- `aios_deadman_watchdog.py` already DETECTS loop death by heartbeat staleness
  (exit code 2 equals BLOCKED). It is detect-only, disabled by default, and does
  not loop or restart anything. Reuse it; do not rewrite detection.
- `Start-AiOsPersistentRuntimeSupervisor.ps1` and the self-heal scripts already
  exist. Reuse their loop and audit-log patterns; do not fork a new supervisor.
- CRITICAL GAP confirmed: `Invoke-AiOsNightCycle.ps1` writes NO heartbeat, yet the
  watchdog reads `telemetry/runtime/runtime_heartbeat.json`. The detect-to-restart
  chain is dead at the source. Closing this is WORK ITEM A and is the keystone.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, three wired
capabilities that compose the existing components into a crash-surviving weekend
loop, plus tests and docs: (A) night-cycle heartbeat emission, (B) an armed but
manually-launched restart supervisor, (C) bounded timeouts on git and network
calls in the hot path, (D) tests and operator docs. Reuse before adding. If an
item is already satisfied by existing code, report that and skip it.

WORK ITEMS:
A. HEARTBEAT EMISSION (keystone). Make the `-Watch` loop in
   `Invoke-AiOsNightCycle.ps1` write `telemetry/runtime/runtime_heartbeat.json`
   atomically (temp plus Move-Item -Force, mirroring Write-CycleMarker) at cycle
   start and cycle end, ideally after each phase. Field set must match what
   `aios_deadman_watchdog.py` parses: an ISO UTC timestamp under heartbeatAt or
   last_beat, plus cycle_id, phase_name, and pid. Confirm the schema by reading
   the watchdog parser first. Reuse `Update-AIOSWorkerHeartbeat.ps1` only if its
   path and schema fit; otherwise add a small Write-AiOsRuntimeHeartbeat helper.
B. ARMED RESTART SUPERVISOR. Add a manually-launched supervisor loop that, on an
   interval, runs `aios_deadman_watchdog.py`; on BLOCKED it restarts the
   night-cycle driver, which then auto-resumes via `Resolve-AiOsCrashRecovery`.
   It MUST: honor the STOP kill-switch and exit immediately if STOP exists; use
   exponential backoff between restarts; enforce a maximum restart count per
   window, then stop and write a local alert; default to DRY_RUN that only logs
   WOULD_RESTART and takes no action; require an explicit -Apply or -ArmRestart
   flag to actually restart. It must NOT register any scheduler.
C. TIMEOUTS. Add one reusable bounded-timeout helper and apply it to the
   git and network calls reached by the night-cycle children (pull-backlog,
   relay-runner, pr-watch, autonomy-bridge). A hung call must time out, be killed,
   and return a logged non-zero result rather than wedging the loop.
D. TESTS AND DOCS. Add or extend tests in the repo-native style proving:
   heartbeat is emitted and atomic; watchdog flips BLOCKED on stale or missing
   heartbeat; supervisor in DRY_RUN logs WOULD_RESTART and does nothing; the
   timeout helper returns non-zero on a hung command. Update the watchdog and
   recovery README files with the MANUAL launch command and an explicit
   not-auto-registered, opt-in note.

ALLOWED PATHS:
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/watchdog/`
- `automation/orchestration/runtime/`
- `automation/runtime/state/`
- `automation/shared/`
- `telemetry/runtime/`
- `telemetry/watchdog/`
- `Reports/endurance_tier1/`

FORBIDDEN PATHS:
- `AGENTS.md`
- `README.md`
- `RISK_POLICY.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `.github/workflows/`
- `.githooks/`
- `.git/`
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
- Never run or register schtasks, Register-ScheduledTask, New-Service, sc.exe,
  cron, or systemd. The restart supervisor is a manually-launched loop only.
- DRY_RUN is the default for every new or changed script. The restart action is
  opt-in behind an explicit flag; default is detect-and-log only.
- Honor the STOP kill-switch `control/self_continuation/STOP` everywhere; never
  restart past STOP.
- All state-file writes MUST be atomic (temp plus Move-Item -Force). No in-place
  Set-Content on state files.
- Do not auto-release locks, reassign packets, stage, or resume APPLY yourself.
  The supervisor only RESTARTS the night-cycle process; the night cycle
  re-resolves its own mode and approval gates. Delegate every APPLY decision to it.
- No live notifications. Alerts are written to local telemetry only.
- No live trading, no broker work, no secret handling.

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, commit, push, merge, hook install,
approval-inbox mutation, worker-queue mutation, Night Supervisor mutation,
scheduler registration, live notification, live trading, or secret handling.
This packet does not state that the Human Owner explicitly approves commit, push,
or merge; those require a separate explicit approval naming this packet ID.

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
- Read `automation/recovery/Resume-AiOsCycle.ps1`
- Read `automation/recovery/README.md`
- Read `automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the proposed diffs as
preview text, and the validator proof. Then STOP for Human Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
diffs, run the validator chain and tests, and stop before commit, push, or merge
unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-T1-WEEKEND-CRASH-SURVIVAL-DRY-RUN-FIRST.md`
- `python automation/orchestration/watchdog/aios_deadman_watchdog.py --threshold-seconds 600`
- PowerShell parse check on every changed .ps1 file (the same syntax gate the CI validate job runs)
- `python -m pytest automation/orchestration/watchdog` if Python tests are added
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/endurance_tier1/weekend_crash_survival_design_dry_run.md`
- `Reports/endurance_tier1/weekend_crash_survival_validator_result.example.json`

FORBIDDEN ACTIONS:
- Do not register any scheduler, service, cron, or systemd unit.
- Do not enable live notifications or auto-approve anything.
- Do not change packet, approval, lock, or worker-queue flow.
- Do not resume APPLY outside the governed night cycle.
- Do not refactor or rename unrelated scripts.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, preview diffs, and validator result. Stop
immediately if preflight branch or worktree state does not match this packet, if
dirty files overlap the mission unsafely, if a required authority file is missing,
if validation fails, if a secret-like value appears, if any scheduler or live
notification appears in scope, if live trading or broker work appears, or if APPLY
approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the heartbeat schema, the restart
arming flag, and the validator chain.

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
