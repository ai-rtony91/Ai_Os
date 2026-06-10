CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. docs/governance/AI_OS_REPO_MEMORY.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_JSONL_ROTATION_RETENTION

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-JSONL-ROTATION-RETENTION-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance hygiene lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_JSONL_ROTATION_RETENTION

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Closes the multi-day resource-accumulation blocker that prevents vacation-length
runs, while preserving proof history so Module 5 and later automation keep a
durable memory spine. Read-only recon confirmed the canonical rotation owner
automation/orchestration/hygiene/Rotate-AiOsLogs.ps1 rotates only files matching
star dot log, there is no JSON-lines rotation owner, and there is no general
retention engine for the accumulating telemetry, relay, and reports directories.
Only an approvals cleanup script and retention design drafts exist.

OBJECTIVE (definition of done):
JSON-lines ledgers are bounded by size and age the same way log files already are,
the accumulating generated directories have a bounded retention policy, and proof
history is preserved by compression rather than destroyed. DRY_RUN-first with a
STOP before APPLY and a separate APPLY approval per module.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- Canonical rotation owner Rotate-AiOsLogs.ps1 already implements size threshold,
  age in days, gzip compression at the keep horizon, and delete after. It filters
  only star dot log, so every JSON-lines ledger grows unbounded.
- JSON-lines ledgers that accumulate include the work ledger, the cost ledger, the
  supervisor cycle ledger, productivity ledgers, and forex journals.
- The accumulating generated directories include telemetry subfolders, relay
  subfolders, and Reports subfolders. There is no general prune policy for these.
- Existing approvals cleanup lives in
  automation/orchestration/maintenance/Clear-AiOsStaleApprovals.ps1. Do not
  duplicate it and do not prune approval evidence through this packet.

MISSION:
Implement, DRY_RUN-first and only after explicit per-module APPLY approval, bounded
JSON-lines rotation and a bounded retention policy by extending the canonical
rotation owner and adding one retention engine. Reuse the existing rotation
patterns. Preserve all proof and evidence history. Phase 1 produces design plus
preview diff plan plus validator and test plan, then STOPS for Human Owner
approval.

MODULE 1 JSONL ROTATION (extend the canonical owner, smallest safe edit):
- Extend Rotate-AiOsLogs.ps1 to also rotate JSON-lines ledgers by size and age,
  reusing its existing size, age, gzip, and keep-horizon logic.
- Add an opt-in switch so the current star dot log behavior is the default and
  unchanged, and JSON-lines rotation activates only when the switch is set.
- For ledgers, prefer rotate then gzip so history is preserved in compressed form.
  Do not hard delete an active ledger or its recent rotations inside the keep
  horizon.

MODULE 2 BOUNDED RETENTION ENGINE (new, additive, conservative):
- Add one retention composer that scans the accumulating generated directories and
  reports, in DRY_RUN, what is eligible for compression or prune by age and size.
- Enforce a hard keep list that is never pruned: proof and evidence directories,
  soak evidence, approval records, governance records, the cycle marker, source
  authority, and anything under a protected evidence path.
- DRY_RUN reports candidates only and deletes nothing. APPLY compresses eligible
  items first and only deletes a compressed artifact after it exceeds a long,
  explicit retention horizon. No mass delete. Every action is per file and logged.

ALLOWED PATHS (write boundary):
- `automation/orchestration/hygiene/`
- `automation/orchestration/maintenance/`
- `tests/orchestration/`
- `Reports/endurance_hygiene/`

FORBIDDEN PATHS:
- `AGENTS.md`
- `RISK_POLICY.md`
- `README.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `.github/`
- `.githooks/`
- `.git/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/scheduler/`
- `automation/orchestration/locks/`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `control/cycle/`
- `apps/dashboard/`
- `tools/android/`
- `secrets/`
- `credentials/`
- `.env`
- `.env.*`
- `broker/`
- `OANDA/`
- `live_trading/`
- `webhooks/`

HARD LIMITS (a violation fails this packet):
- DRY_RUN default. Phase 1 produces design and a preview diff plan only, no
  mutation. Module 1 and Module 2 each require a separate explicit APPLY approval.
- Preserve proof history. Proof, evidence, soak, approval, governance, and cycle
  marker artifacts are never deleted by this packet. The retention engine carries a
  hard keep list and fails closed when a target is uncertain.
- No mass delete, no mass move, no mass rename. Every rotation or prune action is
  per file, bounded by explicit size and age thresholds, and logged.
- Rotation prefers compression over deletion. Deletion is allowed only for a
  compressed artifact past a long, explicit retention horizon.
- Do not change the default behavior of the existing rotation owner. JSON-lines
  rotation is opt-in.
- Honor the STOP kill-switch control/self_continuation/STOP.
- No scheduler registration. No dashboard change. No secrets. No broker, live, or
  webhook behavior.
- Do not merge, close, draft, rebase, push, or comment on other PRs.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY, separately for Module 1 and
Module 2. A validator PASS is evidence only and does not approve APPLY, commit,
push, merge, destructive cleanup, scheduler registration, or secret handling. This
packet does not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID and the specific module.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/orchestration/hygiene/Rotate-AiOsLogs.ps1`
- Read `automation/orchestration/maintenance/Clear-AiOsStaleApprovals.ps1`
- Read `docs/AI_OS/compliance/AIOS_TELEMETRY_CONSENT_AND_RETENTION_DRAFT.md`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a preview diff plan
per module, the explicit keep list, the size and age thresholds, and the validator
and test plan. Then STOP for Human Owner approval.

PHASE 2 (only after a separate explicit APPLY approval naming this packet ID and
the module): implement that one module, run the validator chain and tests, and stop
before commit, push, or merge unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-JSONL-ROTATION-RETENTION-DRY-RUN-FIRST.md`
- PowerShell parser check on every changed .ps1 file in Phase 2
- `python -m pytest tests/orchestration` for the new rotation and retention tests in Phase 2
- a DRY_RUN dry-list assertion proving the keep list is never selected for deletion
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/endurance_hygiene/jsonl_rotation_retention_design_dry_run.md`
- `Reports/endurance_hygiene/jsonl_rotation_retention_validator_result.example.json`

FORBIDDEN ACTIONS:
- Do not delete any proof, evidence, soak, approval, governance, or cycle marker
  artifact.
- Do not change the existing star dot log rotation default behavior.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not prune approval evidence; that lane is owned by Clear-AiOsStaleApprovals.
- Do not commit, push, or merge without separate explicit approval.
- Do not store secrets, and do not enable broker, live, or webhook behavior.

STOP POINT:
Stop after producing the Phase 1 design, per-module preview diff plan, keep list,
thresholds, and validator result. Stop immediately if preflight state does not
match this packet, if a delete would touch a keep-list artifact, if a mass delete
or mass move appears in scope, if a scheduler appears in scope, if validation
fails, or if APPLY approval is not explicit and module specific.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID and the specific module, the exact allowed paths, the keep
list, the size and age thresholds, the long retention horizon, and the validator
chain.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
KEEP LIST PRESERVED:
THRESHOLDS AND HORIZON:
PROOF HISTORY PRESERVATION ASSERTION:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
