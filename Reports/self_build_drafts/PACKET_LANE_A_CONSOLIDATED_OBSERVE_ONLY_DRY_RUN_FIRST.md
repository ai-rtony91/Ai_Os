CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. README.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_LANE_A_CONSOLIDATED_OBSERVE_ONLY

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-AUTONOMY-LANE-A-CONSOLIDATED-OBSERVE-ONLY-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: autonomy finish line, observe-only consolidation lane

WORKER IDENTITY: Claude Code West

LANE: AI_OS_AUTONOMY_LANE_A_CONSOLIDATED

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

PATH SCOPING STATUS: SCOPED

SOURCE RECOMMENDATION:
Read-only discovery found the autonomy spine is built as fail-closed DRY_RUN proofs and
a 7-cycle observe soak has run with zero mutations. The remaining cloud-safe, no-arming
work is four items that can be consolidated into one observe-only branch: complete the
audit lane, enforce the existing gates at the commit and CI chokepoints, specify the
observe-spine to night-cycle wiring, and surface telemetry timestamp hygiene. None of
these arm APPLY, scheduler, SOS, broker, or live behavior. The two protected chokepoint
files are routed to a separate Human Owner apply step.

OBJECTIVE (definition of done):
One additive observe-only branch exists that: adds the Self-Build Evidence Ledger plus
tests, produces the exact enforcement additions for the pre-commit hook and CI as a
reviewable artifact, adds an observe-only night-cycle wiring planner plus a wiring spec,
and adds a read-only telemetry timestamp hygiene scan. It mutates no protected file,
executes nothing, and stops before commit, push, and merge.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- automation/orchestration/autonomy_reports/aios_self_build_evidence_ledger.py is built
  on the stacked source branch and is the last review-lane extraction not yet on main.
- The pre-commit hook and CI run only aios_governance_validator. The path-guard,
  completion-evidence, and runtime-queue-integrity validators exist but are not enforced.
- automation/orchestration/control_loop/aios_observe_spine_runner.py exists but the night
  cycle Invoke-AiOsNightCycle.ps1 does not call it. Wiring is specified here, not applied.
- The retention proof flags future-timestamped telemetry files; this packet scans, it
  does not delete.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, the four observe-only
work items below plus tests. Phase 1 produces the design, the enforcement artifact, the
wiring spec, and a preview of the timestamp scan, then STOPS for Human Owner approval.
It mutates no protected path and no runtime, queue, approval, or scheduler state.

WORK ITEMS:
A. EVIDENCE LEDGER. Add the Self-Build Evidence Ledger module plus tests inside the
   scoped reports and tests paths. Observe-only; reads cycle evidence, writes a digest.
B. GATE ENFORCEMENT ARTIFACT. Produce, under Reports, the exact additions that wire the
   path-guard, completion-evidence, and runtime-queue-integrity validators into the
   pre-commit hook and the CI workflow. Do not edit the hook or CI files; they are a
   separate Human Owner apply step because they are protected paths.
C. NIGHT-CYCLE WIRING PLANNER. Add one observe-only Python planner that returns which
   observe-spine step the night cycle should call each cycle, plus a wiring spec document.
   It returns a plan only; it executes no PowerShell and starts no loop.
D. TIMESTAMP HYGIENE SCAN. Add one read-only scan that lists future-timestamped telemetry
   files for Human Owner cleanup. It reports paths only; it deletes and edits nothing.

ALLOWED PATHS:
- automation/orchestration/autonomy_reports/
- automation/orchestration/control_loop/
- automation/validators/
- tests/orchestration/
- Reports/autonomy_lane_a/

FORBIDDEN PATHS:
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
- automation/orchestration/coordination_spine/
- automation/orchestration/relay/
- automation/orchestration/runtime/
- automation/orchestration/scheduler/
- telemetry/
- secrets/
- credentials/
- .env
- broker/
- OANDA/
- live_trading/
- webhooks/

HARD LIMITS (a violation fails this packet):
- Additive-only inside the allowed write boundary. Read-only over the rest of the repo,
  including telemetry, the hook, and CI.
- DRY_RUN default. APPLY is a separate explicit approval naming this packet ID.
- The hook and CI enforcement is produced as a reviewable artifact only; a Human Owner
  applies it to the protected paths in a separate step.
- No execution, no enqueue, no dispatch, no runtime start, no scheduler registration.
- No live, no broker, no secrets, no webhook behavior.
- Do not weaken validators, approvals, locks, or Human Owner authority.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is evidence
only. This packet does not state that the Human Owner approves commit, push, or merge. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID. Approval does not transfer between actions.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Confirm the working tree is clear of operator local runtime work

PHASE 1 (this packet, no APPLY): produce the ledger design, the enforcement artifact, the
wiring planner design plus spec, the timestamp scan preview, and the test plan. Then STOP
for Human Owner approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): implement items A, C,
and D plus tests, write the item B artifact under Reports, run the validator chain, and
stop before commit, push, or merge unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input <this packet>
- python automation/validators/aios_path_guard_validator.py --staged --packet <this packet>
- python -m py_compile <new files> in Phase 2
- python -m pytest tests/orchestration in Phase 2
- git diff --check

STOP POINT:
Stop after producing the Phase 1 design, enforcement artifact, wiring spec, and timestamp
scan preview. Stop immediately if preflight state does not match this packet, if a
forbidden path would be touched, if any protected file would be edited, if validation
fails, or if APPLY approval is not explicit.

FORBIDDEN ACTIONS:
- Do not edit the pre-commit hook, the CI workflow, or any telemetry file.
- Do not enqueue, dequeue, dispatch, or execute any item.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not commit, push, or merge without separate explicit approval.
- Do not store secrets, and do not enable broker, live, or webhook behavior.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
ENFORCEMENT ARTIFACT:
WIRING SPEC:
TIMESTAMP SCAN:
VALIDATION:
COLLISION CHECK:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
