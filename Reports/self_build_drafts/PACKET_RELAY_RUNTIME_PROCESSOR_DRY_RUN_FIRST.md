CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. README.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_RELAY_RUNTIME_PROCESSOR

SUPERVISOR IDENTITY: Codex East

PACKET ID: AIOS-LOOPCLOSE-RELAY-RUNTIME-PROCESSOR-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: relay/runtime execute lane (local C:\Dev\Ai.Os)

WORKER IDENTITY: EAST_OCC_01

LANE: AI_OS_LOOPCLOSE_RELAY_RUNTIME

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Read-only discovery on current main found the single open arrow in the EXECUTE half
of the loop: approved packets are re-queued only. Invoke-AiOsApprovedActionResume.ps1
moves an approval to relay/inbox and states cardinal limit re-queues only; approved
actions are never executed. Nothing consumes relay/inbox, so approved work sits and
dies. This packet builds the missing consumer in DRY_RUN preview first, then an
approval-gated APPLY twin, so an approved packet can actually advance under the gate.

OBJECTIVE (definition of done):
A relay/runtime processor exists that reads one approved packet from relay/inbox,
verifies it against the governance validator, the completion path-guard, and the
approval record, and produces a DRY_RUN execution PREVIEW (what it WOULD run, the
exact file set, the validator chain). An approval-gated APPLY twin performs the
preview's planned additive work ONLY after a separate explicit Human Owner approval
naming this packet ID. Additive-only, no mutation in DRY_RUN, STOP before APPLY.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1 already classifies goals
  into tiers and routes TIER_2 to relay/approvals. Reuse it; do not rewrite it.
- automation/orchestration/approval_runner/Invoke-AiOsApprovedActionResume.ps1
  re-queues approvals to relay/inbox and executes nothing. This packet adds the
  consumer it hands off to, it does not weaken that re-queue boundary.
- automation/validators/aios_path_guard_validator.py (new on the loop-closure branch)
  returns PASS or BLOCK for a change set against allowed and forbidden paths. The
  processor MUST call it before any APPLY work.
- automation/orchestration/autonomy_review/aios_packet_completeness_review.py returns
  the promotion verdict. The processor MUST require READY_FOR_HUMAN_REVIEW first.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, one relay/runtime
processor plus an approval-gated APPLY twin plus tests. Phase 1 produces the DRY_RUN
preview model and a preview diff plan, then STOPS for Human Owner approval. No live,
no broker, no secrets, no scheduler registration.

WORK ITEMS:
A. RELAY PROCESSOR (DRY_RUN). Add a processor that reads ONE approved packet from
   relay/inbox, runs the governance validator, the path-guard validator, and the
   completeness review, confirms a matching approval record exists, and emits a
   PREVIEW record describing the exact planned file set and validator chain. It
   mutates nothing in DRY_RUN.
B. APPLY TWIN (gated). Add an APPLY counterpart that performs the preview's planned
   additive work ONLY when a separate explicit Human Owner approval names this packet
   ID, the path-guard returns PASS, and the completeness verdict is
   READY_FOR_HUMAN_REVIEW. It stops before commit, push, and merge.
C. TESTS. Prove: missing approval blocks; path-guard BLOCK blocks; incomplete packet
   blocks; a clean approved packet yields a PREVIEW in DRY_RUN and performs no write.

ALLOWED PATHS:
- automation/orchestration/relay/
- automation/orchestration/runtime/
- tests/orchestration/
- Reports/loopclose/

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
- automation/orchestration/scheduler/
- secrets/
- credentials/
- .env
- broker/
- OANDA/
- live_trading/
- webhooks/

HARD LIMITS (a violation fails this packet):
- Additive-only inside the allowed write boundary. Read-only over the rest of the repo.
- DRY_RUN default. The APPLY twin runs ONLY under a separate explicit approval naming
  this packet ID. Approval does not transfer between actions.
- No live, no broker, no secrets, no scheduler registration, no webhook behavior.
- Do not weaken validators, approvals, locks, or Human Owner authority.
- Do not commit, push, or merge. Each needs its own separate explicit approval.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is evidence
only. This packet does not state that the Human Owner approves commit, push, or merge.
Each of commit, push, and merge requires a separate explicit Human Owner approval
naming this packet ID. Approval does not transfer between actions.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Confirm relay/inbox and relay/approvals state, and that no operator local run is mid-cycle

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input <this packet>
- python automation/validators/aios_path_guard_validator.py --staged --packet <this packet>
- python -m py_compile <new files> in Phase 2
- python -m pytest tests/orchestration in Phase 2
- git diff --check

STOP POINT:
Stop after producing the Phase 1 DRY_RUN preview model and preview diff plan. Stop
immediately if preflight state does not match this packet, if path-guard returns
BLOCK, if completeness is not READY_FOR_HUMAN_REVIEW, if a forbidden path would be
touched, if validation fails, or if APPLY approval is not explicit.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
COLLISION CHECK:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
