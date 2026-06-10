CODEX-ONLY PROMPT

CODEX-ONLY PROMPT:

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

FORBIDDEN PATHS:
- AGENTS.md
- README.md
- automation/orchestration/approval_inbox/
- automation/orchestration/workers/
- automation/orchestration/night_supervisor/
- services/
- secrets/
- credentials/
- broker/
- OANDA/
- live_trading/

identity marker: AI_OS Packet 3A dispatch lane and worker-state proposal
supervisor identity: Anthony approval authority
packet ID: AIOS-T2A-DISPATCH-LANE-WORKERSTATE-DRY-RUN-FIRST
mode: DRY_RUN
zone: orchestration / dispatch lane decision / worker-state atomic design
worker identity: Codex CLI local executor
lane: packet3a-dispatch-lane-workerstate-dry-run
worktree: C:\Dev\Ai.Os
branch: resolve after preflight

approval authority: Anthony
approval status: DRY_RUN review only. Packet 3A APPLY is not approved. Packet 3B, Packet 3C, Packet 3D, Packet 3E, Packet 2, and Packet 4 are not approved. No worker launch, scheduler, Night Supervisor, SOS, ADB, broker/cloud/live trading, secrets, commit, push, or merge is approved.

title:
AIOS-T2A-DISPATCH-LANE-WORKERSTATE-DRY-RUN-FIRST

purpose:
Narrow DRY_RUN-first packet to decide the canonical dispatch lane and design worker-state atomic read/write hardening.

known state:
Packet 1 approval-authority hardening has landed on main.
Approval chain reports PENDING_HUMAN_REVIEW.
Raw approved_by_human=true is no longer enough for APPLY.
The original Packet 3 was reviewed and classified PACKET3_SPLIT_REQUIRED.
Packet 3A is the first smaller increment split from the original Packet 3.
Existing atomic file-lock persistence must be reused. Do not redo the lock system.
Controlled worker launch remains blocked.

source packet:
Original parked Packet 3 source:
origin/claude/autonomy-closure-packets
automation/orchestration/work_packets/proposed/AIOS-T2-DISPATCH-CLOSURE-WORKERSTATE-CITESTS-DRY-RUN-FIRST.md

mission:
Run a DRY_RUN-only inspection and design pass for Packet 3A. Inventory current dispatch lanes, recommend the canonical dispatch lane, decide whether the TypeScript dispatcher/runtime lane should be repaired, shelved, or left out of T2A, inventory worker-state files and scripts, design atomic worker-state write/read hardening, design fail-safe worker-state read behavior, produce exact future APPLY scope, produce exact tests and validators for later, and stop before APPLY.

preflight:
Run:
pwd
git status --short --branch
git branch --show-current
git remote -v
git fetch origin
git status --short --branch
git log -1 --oneline

Confirm:
- current branch is main or safely state-aligned after preflight
- main is aligned with origin/main before any later APPLY design is finalized
- no tracked dirty files exist
- only known unrelated untracked backlog exists
- approval chain is pending/review-required, not raw approved
- Packet 1 approval hardening is present
- original Packet 3 remains parked
- Packet 3B, Packet 3C, Packet 3D, Packet 2, and Packet 4 remain parked

known unrelated untracked backlog:
Reports/phase_0_to_4_bridge/AIOS_REMOTE_ACCESS_MODEL_NOTE_20260608.md
Reports/phase_0_to_4_bridge/app_service_bridge_v0_remote_overlap_review_20260608.md
automation/orchestration/work_packets/proposed/AIOS-SB-001-APPROVAL-INBOX-SCHEMA-VALIDATOR-DRY-RUN-FIRST.md

read first:
AGENTS.md
README.md
automation/orchestration/README.md
docs/governance/source-of-truth-map.md
docs/audits/active-system-map.md
docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md
automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json
automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1

inspect dispatch lane surfaces:
automation/orchestration/dispatcher/
automation/dispatcher/runtime/
automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1
automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1
services/dispatcher/
services/runtime/
automation/orchestration/workers/
automation/window_identity/ if present
tests/orchestration/
tests/governance/

DRY_RUN requirements:
1. Inventory current dispatch lanes.
2. Identify the canonical dispatch lane recommendation.
3. Decide whether the TypeScript dispatcher/runtime lane should be repaired, shelved, or left out of T2A.
4. Inventory worker-state files and scripts.
5. Design atomic worker-state write/read hardening.
6. Design fail-safe worker-state read behavior for missing, malformed, or partially written state.
7. Identify exact future APPLY scope and exact files to edit, based on repo evidence.
8. Identify exact tests and validators for later APPLY.
9. Confirm no worker launch, scheduler, Night Supervisor, SOS, ADB, broker/live trading, webhook, secret, or production action is introduced.
10. Stop before APPLY.

later APPLY candidate scope:
The later APPLY packet must be generated only after this DRY_RUN confirms exact files. Likely files may include:
- docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md
- automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1
- worker-state read/write helper paths discovered during DRY_RUN
- focused tests under tests/orchestration/ and/or tests/governance/

explicit exclusions:
- assignment lock integration
- relay idempotency
- stranded-task recovery
- CI workflow edits
- .github edits
- CODEOWNERS edits
- Reports seeding except read-only evidence only
- worker launch
- scheduler
- Night Supervisor
- SOS or ADB
- broker, OANDA, cloud, live trading, webhooks
- secrets, credentials, .env
- Packet 3B, Packet 3C, Packet 3D, Packet 3E, Packet 2, or Packet 4 release

allowed paths:
READ ONLY:
AGENTS.md
README.md
docs/governance/
docs/audits/
docs/architecture/
automation/orchestration/
automation/dispatcher/runtime/
automation/validators/
services/dispatcher/
services/runtime/
tests/orchestration/
tests/governance/
.github/workflows/ only for read-only CI context if needed

FOR FUTURE APPLY DESIGN ONLY:
docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md
automation/dispatcher/runtime/workers/
worker-state read/write helper paths discovered during DRY_RUN
tests/orchestration/
tests/governance/

forbidden paths and actions:
Do not edit files in this DRY_RUN.
Do not apply Packet 3A.
Do not activate or move this packet.
Do not edit approval_inbox/.
Do not edit locks/.
Do not edit relay scripts.
Do not edit assignment lock integration.
Do not edit .github/.
Do not edit CODEOWNERS.
Do not edit Reports/.
Do not release Packet 3B.
Do not release Packet 3C.
Do not release Packet 3D.
Do not release Packet 3E.
Do not release Packet 2.
Do not release Packet 4.
Do not launch workers.
Do not start scheduler.
Do not start Night Supervisor.
Do not run full night cycle.
Do not arm/send SOS.
Do not call ADB.
Do not send notifications.
Do not touch broker, cloud, live trading, OANDA, webhooks, secrets, credentials, or .env.
Do not stage files.
Do not commit.
Do not push.
Do not merge.
Do not stash.
Do not clean.

STOP-before-APPLY:
This packet is DRY_RUN-first. Stop after producing the Packet 3A design report. APPLY requires a separate explicit Anthony approval naming this packet ID, exact allowed paths, exact files, validator chain, and stop point.

reuse requirements:
Reuse Packet 1 approval hardening.
Reuse existing atomic file-lock persistence.
Do not create duplicate approval authority.
Do not create a fourth dispatch lane.
Do not redo the lock system.

validator chain:
Run safe read-only validation:
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1
python automation/orchestration/dispatcher/assignment_executor.py --sample-check --json
python automation/validators/aios_worker_dispatcher_assignment_executor_validator.py --sample-check --json
python -m pytest tests/orchestration/test_worker_dispatcher_assignment_executor.py tests/orchestration/test_worker_dispatcher_control_plane.py tests/governance/test_aios_worker_dispatcher_validator.py
git diff --check
git status --short --branch

If a governance validator exists for proposed work packets, run it against this file:
python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-T2A-DISPATCH-LANE-WORKERSTATE-DRY-RUN-FIRST.md

final report format:
SUMMARY:
CURRENT REPO STATE:
DISPATCH LANE INVENTORY:
CANONICAL LANE RECOMMENDATION:
TYPESCRIPT LANE DECISION:
WORKER-STATE INVENTORY:
ATOMIC WORKER-STATE DESIGN:
FAIL-SAFE READ DESIGN:
FUTURE APPLY SCOPE:
TESTS / VALIDATORS:
EXCLUSIONS CONFIRMED:
RUNTIME SAFETY REVIEW:
DRY_RUN DECISION:
SAFE NEXT ACTION:
STATUS: DRY_RUN COMPLETE, NO FILES CHANGED

stop point:
Stop after Packet 3A DRY_RUN design report. Do not APPLY, edit, stage, commit, push, merge, activate packets, or launch anything.
