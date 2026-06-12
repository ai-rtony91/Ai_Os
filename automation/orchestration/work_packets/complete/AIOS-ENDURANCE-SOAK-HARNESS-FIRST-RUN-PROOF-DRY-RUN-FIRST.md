CODEX-ONLY PROMPT

CODEX-ONLY PROMPT:

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

IDENTITY MARKER: AI_OS_PACKET_DRAFT_SOAK_HARNESS_FIRST_RUN_PROOF

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-SOAK-HARNESS-FIRST-RUN-PROOF-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance proof lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_SOAK_PROOF

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Pulled forward from the vacation hygiene work because the system has no empirical
proof of even one continuous run. The cycle marker control/cycle/last_marker.json
has never been produced by a real run, and no soak harness exists. No endurance
milestone (12 hours, 24 hours, multi-day) can be proven until the loop actually
runs and produces evidence. This packet builds the evidence-generation capability
and establishes the proof ladder, so every later milestone can be certified by
artifacts rather than asserted.

OBJECTIVE (definition of done):
A manually-launched, observe-only soak harness exists that runs the night-cycle
loop in a bounded, supervised, DRY_RUN mode and records evidence of liveness and
resource behavior, and a first supervised run has produced the first real cycle
marker plus a soak evidence report. No APPLY of real work, no scheduler, no live
sends. The human is present for the first run.

GROUNDED FINDINGS (already verified on main; do NOT re-derive):
- The night-cycle loop, heartbeat emission, atomic cycle marker, and crash-resume
  are live on main, so a real run can produce real evidence today.
- control/cycle/last_marker.json does not yet exist, so no real cycle has ever run.
- No soak harness and no soak evidence report format exist anywhere in the repo.
- A 12-hour paper-lab profile exists at
  automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json and
  can serve as scaffolding for the 12-hour rung, report-only.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, an observe-only
soak harness, a soak evidence report format, a documented soak ladder runbook, and
the execution of one short bounded first supervised run that produces the first
real marker and evidence report. Reuse the existing loop, watchdog, and dashboard
state; do not add a parallel runtime. Phase 1 produces design plus preview diff
plan plus validator and test plan, then STOPS for Human Owner APPLY approval.

WORK ITEMS:
A. SOAK HARNESS. Add a manually-launched harness that runs the night-cycle loop in
   a bounded, observe-only manner (DRY_RUN, time-bounded or cycle-count-bounded),
   and on an interval samples and records: heartbeat freshness measured as the age
   of telemetry/runtime/runtime_heartbeat.json, cycle marker progression read from
   control/cycle/last_marker.json, process resident memory, filesystem free space,
   and per-cycle pass or fail. It honors the STOP kill-switch
   control/self_continuation/STOP, registers no scheduler, sends nothing, and
   writes its evidence atomically.
B. EVIDENCE REPORT FORMAT. Define a soak evidence report artifact capturing the
   sampled series for heartbeat freshness, resident memory, disk free, marker
   progression, per-cycle result, start and end time, and a pass or fail verdict
   against rung criteria. Store under Reports/endurance_soak and the gitignored
   runtime telemetry path.
C. SOAK LADDER RUNBOOK. Document the gated ladder with explicit pass criteria for
   each rung: one supervised cycle, twelve hours, twenty-four hours with at least
   one induced crash, seventy-two hours, and seven days zero-touch. Each rung is
   gated on the prior.
D. FIRST SUPERVISED RUN. Execute one short bounded run, human present, in DRY_RUN
   observe-only mode, to produce the first real cycle marker and the first soak
   evidence report. This is proof rung one only. Do not attempt longer rungs in
   this packet.
E. TESTS. Prove the harness samples correctly, the report schema validates, and a
   bounded run terminates and produces a marker and a report.

ALLOWED PATHS:
- `automation/orchestration/soak/`
- `automation/orchestration/watchdog/`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `Reports/endurance_soak/`
- `telemetry/soak/`
- `docs/runbooks/`
- `tests/`

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
- `automation/orchestration/night_supervisor/`

HARD LIMITS (a violation fails this packet):
- The first supervised run is DRY_RUN and observe-only. No APPLY of real packet
  work, no commit or push by the loop, no live notifications, no broker, no live
  trading.
- The run is bounded in duration or cycle count and requires the human to be
  present. It is not a scheduled or unattended run.
- Never run or register schtasks, Register-ScheduledTask, New-Service, sc.exe,
  cron, or systemd. The harness is manually launched only.
- Honor the STOP kill-switch control/self_continuation/STOP everywhere.
- All evidence-file writes MUST be atomic, temp then rename.
- Reuse the existing loop, watchdog, and dashboard state; no parallel runtime.
- No secrets. Do not store any credential or token value.
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
- Read `automation/orchestration/dashboard/Update-AiOsDashboardState.ps1`
- Read `automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the preview diff plan,
and the validator and test plan, including the first-run procedure and its evidence
schema. Then STOP for Human Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): build the
harness, the report format, and the runbook, execute the one bounded first
supervised run, and stop before commit, push, or merge unless that same approval
explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-SOAK-HARNESS-FIRST-RUN-PROOF-DRY-RUN-FIRST.md`
- PowerShell parse check on every changed .ps1 file in Phase 2
- Repo-native tests for the harness sampler and report schema in Phase 2
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/endurance_soak/soak_harness_design_dry_run.md`
- `Reports/endurance_soak/soak_evidence_report.example.json`

FORBIDDEN ACTIONS:
- Do not register any scheduler, service, cron, or systemd unit.
- Do not run an unattended or unbounded run.
- Do not enable live notifications or auto-approve anything.
- Do not APPLY real packet work during the supervised run.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, and validator result.
Stop immediately if preflight branch or worktree state does not match this packet,
if dirty files overlap the mission unsafely, if a required authority file is
missing, if validation fails, if a secret-like value appears, if any scheduler or
live notification appears in scope, if an unbounded or unattended run appears in
scope, if live trading or broker work appears, or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the bounded run duration or cycle
count, and the validator chain.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
REUSED VS ADDED:
FIRST RUN EVIDENCE SUMMARY:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
