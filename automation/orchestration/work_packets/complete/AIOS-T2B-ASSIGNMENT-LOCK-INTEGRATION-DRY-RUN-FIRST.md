CODEX-ONLY PROMPT

CODEX-ONLY PROMPT:

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

IDENTITY MARKER: AI_OS_PACKET_DRAFT_T2B_ASSIGNMENT_LOCK_INTEGRATION

SUPERVISOR IDENTITY: Anthony approval authority

PACKET ID: AIOS-T2B-ASSIGNMENT-LOCK-INTEGRATION-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: orchestration / Packet 3B assignment lock integration

WORKER IDENTITY: Codex CLI local executor

LANE: packet3b-assignment-lock-integration

WORKTREE: C:\Dev\Ai.Os

BRANCH: main, verified by read-only preflight before any future APPLY

ALLOWED PATHS:
- automation/orchestration/coordination_spine/
- automation/orchestration/locks/
- automation/orchestration/work_packets/proposed/
- automation/orchestration/work_packets/active/
- automation/orchestration/work_packets/deferred/
- tests/orchestration/
- tests/guardrails/

FORBIDDEN PATHS:
- AGENTS.md
- README.md
- docs/
- automation/orchestration/approval_inbox/
- automation/orchestration/workers/
- automation/orchestration/night_supervisor/
- services/
- broker/
- webhooks/
- secrets/
- .env
- .env.*

APPROVAL AUTHORITY:
Anthony is the Human Owner and approval authority. This proposed packet is not
APPLY approval. Validator PASS is evidence only. Commit, push, merge, packet
activation, worker launch, scheduler start, Night Supervisor start, SOS, ADB,
notification send, broker work, live trading, cloud deployment, and secret
handling each remain blocked unless separately and explicitly approved.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-T2B-ASSIGNMENT-LOCK-INTEGRATION-DRY-RUN-FIRST.md

STOP POINT:
- Do not modify packet mission/scope, do not touch runtime heartbeat, lock semantics, queue policy, worker launch, live dispatch, T2B execution, Operation Glue, Auto-Loop, secrets, broker, webhook, or authority.

FINAL REPORT FORMAT:
SUMMARY
WHAT CHANGED
FILES CHANGED
VALIDATION
SAFE NEXT COMMAND

PURPOSE:
Narrow DRY_RUN-first packet to design assignment lock integration using existing
atomic lock persistence. Packet 3B must reuse the current approval hardening from
Packet 1, reuse the Packet 3A canonical lane decision and worker-state hardening,
and reuse the existing lock persistence under automation/orchestration/locks/.
It must not redo the lock system.

MISSION:
Perform a DRY_RUN design for integrating file-lock claims into packet assignment.
The design must inspect the current assignment mutation path, inspect existing
lock persistence helpers, define the later APPLY scope, define exact tests and
validators, and stop before APPLY. No assignment mutation, lock mutation, worker
launch, scheduler, Night Supervisor, SOS, ADB, notification, broker/live trading,
secret handling, or packet activation is approved by this proposal.

READ-ONLY PREFLIGHT:
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- git fetch origin
- git status --short --branch
- git log -1 --oneline
- Confirm current branch is main and aligned with origin/main.
- Confirm no tracked dirty files exist.
- Confirm only known unrelated untracked backlog remains, or stop and report.
- Confirm approval chain remains PENDING_HUMAN_REVIEW or equivalent safe non-APPLY state.
- Confirm Packet 1 approval-authority hardening has landed.
- Confirm Packet 3A worker-state lane hardening has landed.
- Confirm no active APPLY approval exists.

DRY_RUN INSPECTION SCOPE:
- AGENTS.md
- automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1
- automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1
- automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1
- automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1
- automation/orchestration/locks/FILE_LOCK_REGISTRY.json
- automation/orchestration/dispatcher/
- automation/orchestration/work_packets/
- tests/orchestration/test_file_lock_persistence.py
- tests/orchestration/test_packet3a_worker_state_atomicity.py
- tests/governance/test_packet3a_dispatch_lane_decision.py
- docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md

ALLOWED PATHS:
- automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1
- tests/orchestration/test_packet3b_assignment_lock_integration.py
- tests/orchestration/test_file_lock_persistence.py
- tests/orchestration/test_packet3a_worker_state_atomicity.py
- tests/governance/test_packet3a_dispatch_lane_decision.py
- docs/architecture/AIOS_CANONICAL_LOOP_DECISION.md only if the DRY_RUN proves an existing canonical note needs a small update.

DRY_RUN DESIGN REQUIREMENTS:
1. Inspect the current assignment mutation path in automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1.
2. Inspect existing lock persistence scripts:
   - automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1
   - automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1
   - automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1
3. Design lock claim before assignment mutation.
4. Design fail-closed behavior when lock claim is BLOCKED or REVIEW_REQUIRED.
5. Design exact lock ID recording behavior only after successful lock claim.
6. Design double-assignment prevention using assigned-worker checks plus active lock overlap.
7. Design release requirement using exact worker_id plus lock_id.
8. Design stale-lock handling as REVIEW_REQUIRED only, never auto-clear.
9. Produce exact later APPLY scope.
10. Produce exact tests and validators.
11. Stop before APPLY.

EXPECTED DESIGN ANSWERS:
- Exact current assignment mutation path.
- Exact existing lock persistence functions and scripts to reuse.
- Exact future APPLY files.
- Exact future tests and validators.
- Whether future APPLY needs splitting.
- How double-assignment is prevented.
- How lock collision fails closed.
- How lock release is handled.
- How stale locks are reported without auto-clearing.
- How Packet 3B avoids worker launch.

LIKELY FUTURE APPLY FILES:
- automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1
- tests/orchestration/test_packet3b_assignment_lock_integration.py
- Possible small docs update only if an existing canonical doc needs a note.

FUTURE APPLY BOUNDARY:
Future APPLY must be separately approved after DRY_RUN confirms exact files. The
later APPLY scope should be limited to integrating lock claim preview/claim into
assignment, recording successful lock IDs in assignment evidence, and adding
focused tests. Do not expand into queue movement, runtime launch, stale-lock
cleanup, relay recovery, scheduler behavior, notification behavior, or governance
authority changes.

REUSE REQUIREMENTS:
- Reuse Packet 1 approval-authority hardening.
- Reuse Packet 3A canonical lane decision and worker-state hardening.
- Reuse automation/orchestration/locks/ atomic lock persistence.
- Reuse Claim-AiOsFileLock.DRY_RUN.ps1 collision and policy-block behavior.
- Reuse Release-AiOsFileLock.DRY_RUN.ps1 exact worker_id plus lock_id release behavior.
- Reuse Get-AiOsWorkerLockStatus.DRY_RUN.ps1 stale/collision reporting.
- Do not redo lock persistence.
- Do not create a parallel lock registry.
- Do not create any new governance authority source.

HARD EXCLUSIONS:
- No worker launch.
- No scheduler.
- No Night Supervisor.
- No SOS or ADB.
- No notifications.
- No Telegram.
- No broker or live trading.
- No secrets, credentials, .env, webhooks, or cloud deployment.
- No .github edit.
- No CODEOWNERS edit.
- No Reports seeding.
- No relay idempotency work.
- No stranded-task recovery work.
- No stale-lock cleanup.
- No stale-lock auto-clear.
- No packet auto-reassignment.
- No TypeScript runtime repair.
- No Packet 2 work.
- No Packet B+C work.
- No Packet 4 work.
- No packet activation or state movement.

FORBIDDEN PATHS FOR FUTURE APPLY:
- .github/
- .github/workflows/
- .githooks/
- .git/
- CODEOWNERS
- AGENTS.md
- README.md
- RISK_POLICY.md
- Reports/
- automation/orchestration/approval_inbox/
- automation/orchestration/relay/
- automation/orchestration/workers/
- automation/orchestration/night_supervisor/
- automation/orchestration/notifications/
- automation/orchestration/recovery/
- services/python_supervisor/
- secrets/
- credentials/
- .env
- .env.*
- broker/
- OANDA/
- live_trading/
- webhooks/

VALIDATOR CHAIN FOR THIS DRY_RUN PACKET:
- powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1
- python automation/orchestration/dispatcher/assignment_executor.py --sample-check --json
- python automation/validators/aios_worker_dispatcher_assignment_executor_validator.py --sample-check --json
- python -m pytest tests/orchestration/test_packet3a_worker_state_atomicity.py tests/governance/test_packet3a_dispatch_lane_decision.py
- git diff --check
- git status --short --branch
- If a proposed-work-packet governance validator exists, run it against this file.

VALIDATOR CHAIN FOR FUTURE APPLY:
- PowerShell parser check for every changed .ps1 file.
- Focused pytest coverage for Packet 3B assignment lock integration.
- Existing lock persistence tests.
- Existing Packet 3A worker-state and dispatch-lane tests.
- Assignment executor sample-check.
- Assignment executor validator sample-check.
- Approval chain DRY_RUN.
- git diff --check.
- git status --short --branch.

STOP POINT:
Stop after DRY_RUN design and validator report. Do not APPLY, activate, move
packet state, stage, commit, push, merge, launch workers, start scheduler, start
Night Supervisor, arm/send SOS, call ADB, send notifications, touch secrets, or
continue automatically.

FINAL REPORT FORMAT:
SUMMARY:
PACKET3B_DESIGN:
PACKET3B_FILES_LIKELY_TO_CHANGE:
PACKET3B_TESTS_NEEDED:
PACKET3B_SPLIT_DECISION:
RUNTIME SAFETY REVIEW:
VALIDATION:
SAFE NEXT ACTION:
STATUS: DRY_RUN COMPLETE, NO APPLY, NO COMMIT, NO PUSH
