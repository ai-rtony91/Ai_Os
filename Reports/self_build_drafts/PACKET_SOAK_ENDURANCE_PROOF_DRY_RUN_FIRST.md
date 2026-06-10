CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. README.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_SOAK_ENDURANCE_PROOF

SUPERVISOR IDENTITY: Codex East

PACKET ID: AIOS-LOOPCLOSE-SOAK-ENDURANCE-PROOF-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: endurance soak proof lane (local C:\Dev\Ai.Os)

WORKER IDENTITY: EAST_OCC_01

LANE: AI_OS_LOOPCLOSE_SOAK_ENDURANCE

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
The scheduler approval gate requires one clean unattended endurance window before it
may be registered. Today the soak harness is a DRY_RUN design only and no real soak
evidence exists. This packet runs a bounded observe-only endurance window of the
night cycle in watch mode, on the local machine that owns the runtime, and emits soak
evidence that the soak evidence validator accepts. It proves the loop can run for a
12 to 24 hour window without drift, which is a precondition for stage 10.

OBJECTIVE (definition of done):
A real bounded endurance window of the night cycle runs in observe-only watch mode on
the local machine, refreshing the heartbeat and cycle marker each cycle, honoring the
STOP kill-switch, and emitting soak evidence whose status is PASS or STOPPED and which
the soak evidence validator accepts. No mutation beyond evidence and telemetry writes.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- automation/orchestration/Invoke-AiOsNightCycle.ps1 supports watch mode with a max
  cycle count and an interval, refreshes telemetry/runtime/runtime_heartbeat.json and
  control/cycle/last_marker.json, and exits on control/self_continuation/STOP.
- automation/orchestration/watchdog/aios_deadman_watchdog.py already classifies a stale
  or missing heartbeat as BLOCKED. Run it against the soak heartbeat as the liveness check.
- automation/validators/aios_soak_evidence_validator.py defines the soak evidence
  schema and accepted statuses. The soak run MUST emit evidence in that schema.

MISSION:
Run, DRY_RUN-first and observe-only, a bounded endurance window of the night cycle and
emit accepted soak evidence. Phase 1 produces the soak plan, the evidence schema fill,
and a short proof window, then STOPS for Human Owner review. No live, no broker, no
secrets, no scheduler registration during this packet.

WORK ITEMS:
A. SOAK RUN. Start the night cycle in observe-only watch mode for a bounded window
   with a fixed interval and max cycles. Refresh heartbeat and cycle marker each cycle.
B. LIVENESS CHECK. Run the dead-man watchdog against the soak heartbeat at intervals
   and record OK versus BLOCKED. A single BLOCKED classification fails the soak.
C. STOP DRILL. Mid-window, create control/self_continuation/STOP and confirm the loop
   exits cleanly and the evidence status becomes STOPPED, then remove STOP and resume.
D. EVIDENCE. Emit soak evidence in the soak evidence validator schema and run the
   validator. Status must be PASS or STOPPED with no contradictions.

ALLOWED PATHS:
- Reports/endurance_soak/
- telemetry/soak/
- telemetry/runtime/
- control/cycle/
- tests/orchestration/

FORBIDDEN PATHS:
- AGENTS.md
- RISK_POLICY.md
- README.md
- WHITEPAPER.md
- ARCHITECTURE.md
- .github/
- .githooks/
- .git/
- automation/orchestration/work_packets/
- automation/orchestration/scheduler/
- secrets/
- credentials/
- .env
- broker/
- OANDA/
- live_trading/
- webhooks/

HARD LIMITS (a violation fails this packet):
- Observe-only. The night cycle runs in observe-only watch mode. No APPLY phases.
- No scheduler registration, service install, or autostart entry of any kind here.
- No live, no broker, no secrets, no webhook behavior.
- Honor the STOP kill-switch at control/self_continuation/STOP at all times.
- Do not commit, push, or merge. Each needs its own separate explicit approval.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A soak PASS is evidence only
and does not approve scheduler registration. This packet does not state that the Human
Owner approves commit, push, or merge. Each of commit, push, and merge requires a
separate explicit Human Owner approval naming this packet ID.
Approval does not transfer between actions.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- Read AGENTS.md
- Read RISK_POLICY.md
- Confirm the STOP kill-switch path is writable and the heartbeat path is present

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input <this packet>
- python automation/orchestration/watchdog/aios_deadman_watchdog.py against the soak heartbeat
- python automation/validators/aios_soak_evidence_validator.py against the emitted evidence
- git diff --check

STOP POINT:
Stop after the bounded proof window and the emitted soak evidence. Stop immediately if
the watchdog returns BLOCKED, if the STOP drill does not exit cleanly, if evidence does
not validate, if a forbidden path would be touched, or if APPLY approval is not explicit.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
SOAK STATUS:
WATCHDOG RESULT:
STOP DRILL RESULT:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
