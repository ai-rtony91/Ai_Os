CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. README.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_P1_CANONICAL_RUNTIME_EXECUTION_QUEUE

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-RUNTIME-EXECUTION-LANE-P1-CANONICAL-QUEUE-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: runtime execution lane keystone

WORKER IDENTITY: Claude Code West

LANE: AI_OS_RUNTIME_EXECUTION_QUEUE_CANON

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

PATH SCOPING STATUS: SCOPED

SOURCE RECOMMENDATION:
Read-only discovery on current main found that there is no single runtime execution
queue. Work is fragmented across at least fifteen queue authorities, including
relay inbox task files, AIOS command queue, dispatcher queue, worker task queue,
unified queue index, agent runtime queue, and several Python queue readers. The relay
worker can already move a task from inbox to running to done, and the persistent
runtime supervisor already has a restart loop, but they have no one canonical queue to
read. Without a single execution queue authority the loop cannot drain approved work
deterministically and vacation mode cannot close. This packet builds that keystone as
a read-only normalizer first, so the migration that follows has one target.

OBJECTIVE (definition of done):
A canonical runtime execution queue contract exists, plus a read-only adapter that
normalizes the existing fragmented queue sources into one queue view, plus an
integrity validator. It is observe-only: it reads sources, emits one normalized queue
view and a report, and mutates no source queue and executes nothing. Additive-only,
DRY_RUN-first, no mutation, with a STOP before APPLY.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1 already drains relay inbox
  to running to done. Reuse it later; this packet does not change it.
- automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1 already
  has a restart loop. Reuse it later; this packet does not change it.
- Multiple queue files exist on main and disagree. This packet reads them, it does not
  delete or rewrite them. Migration to the canonical queue is a separate later packet.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, one canonical runtime
execution queue contract, one read-only adapter that normalizes the fragmented sources
into a single queue view, one integrity validator, and tests. Phase 1 produces the
contract, the adapter design, the validator rules, and a preview of the normalized
queue from real sources, then STOPS for Human Owner approval. It mutates nothing.

WORK ITEMS:
A. QUEUE CONTRACT. Add a canonical schema named AIOS_RUNTIME_EXECUTION_QUEUE.v1 that
   defines one queue item: id, source, kind, state, allowed_paths, protected_action,
   created_utc, and a single normalized state set such as QUEUED, RUNNING, DONE, ERROR,
   BLOCKED, DEFERRED.
B. READ-ONLY ADAPTER. Add a Python adapter that reads the existing fragmented sources,
   normalizes each into a queue item, deduplicates by id, and emits one queue view plus
   a source map showing which fragment each item came from. It mutates no source.
C. INTEGRITY VALIDATOR. Add a validator that checks the normalized queue for duplicate
   ids across sources, unknown states, and any item carrying a protected or forbidden
   execution flag. It returns PASS or BLOCK with a reason list.
D. TESTS. Prove normalization from sample fragments, dedupe across sources, BLOCK on a
   protected item, and that no source file is modified.

ALLOWED PATHS:
- automation/orchestration/runtime_queue/
- automation/validators/
- tests/orchestration/
- Reports/runtime_queue/

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
- secrets/
- credentials/
- .env
- broker/
- OANDA/
- live_trading/
- webhooks/

HARD LIMITS (a violation fails this packet):
- Additive-only inside the allowed write boundary. Read-only over every existing queue
  source. The adapter and validator mutate no source queue and execute nothing.
- DRY_RUN default. APPLY is a separate explicit approval naming this packet ID.
- No execution, no enqueue, no dequeue, no worker dispatch, no relay or runtime change.
- No live, no broker, no secrets, no scheduler registration, no webhook behavior.
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

PHASE 1 (this packet, no APPLY): produce the queue contract, the adapter design, the
validator rules, the normalized queue preview from real sources, and the test plan.
Then STOP for Human Owner approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): implement the
contract, adapter, validator, and tests, run the validator chain, and stop before
commit, push, or merge unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input <this packet>
- python automation/validators/aios_path_guard_validator.py --staged --packet <this packet>
- python -m py_compile <new files> in Phase 2
- python -m pytest tests/orchestration in Phase 2
- git diff --check

STOP POINT:
Stop after producing the Phase 1 contract, adapter design, validator rules, and the
normalized queue preview. Stop immediately if preflight state does not match this
packet, if a forbidden path would be touched, if any source queue would be modified,
if validation fails, or if APPLY approval is not explicit.

FORBIDDEN ACTIONS:
- Do not modify, delete, or rewrite any existing queue source.
- Do not enqueue, dequeue, dispatch, or execute any item.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not commit, push, or merge without separate explicit approval.
- Do not store secrets, and do not enable broker, live, or webhook behavior.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
QUEUE CONTRACT:
NORMALIZED SOURCES:
VALIDATION:
COLLISION CHECK:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
