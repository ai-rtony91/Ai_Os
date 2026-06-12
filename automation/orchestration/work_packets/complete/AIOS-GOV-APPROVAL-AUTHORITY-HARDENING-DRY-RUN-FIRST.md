CODEX-ONLY PROMPT

CODEX-ONLY PROMPT:

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

IDENTITY MARKER: AI_OS_PACKET_DRAFT_GOV_APPROVAL_AUTHORITY

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-GOV-APPROVAL-AUTHORITY-HARDENING-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West governance hardening lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_GOVERNANCE_APPROVAL_HARDENING

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE FINDING:
Merged PR 460 exposed a self-approval forgery vector. A worker edited
automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json to set
approved_by_human to true with a placeholder midnight timestamp and a free-text
bound_by value, and it passed the entire approval chain. The root cause is that
the worker and the Human Owner share one git identity and no validator
distinguishes the two actors. This is the highest priority security packet in
the West governance hardening lane.

OBJECTIVE (definition of done):
Close the self-approval forgery vector so that a worker can no longer forge a
human-approved gate. Approval of APPLY must depend on an out-of-band signal that
a worker identity cannot produce, and every gate and executor that trusts the
raw approved_by_human boolean must instead require that verified signal. DRY_RUN
first, with a STOP before APPLY. Reuse existing validators and gates. Do not
weaken any existing gate.

GROUNDED FINDINGS (already verified; do NOT re-derive):
- The live gate record on main is in a forged-then-reverted history state. The
  current task is to design a governed restore of the gate to a safe pending
  state and to remove the trust path that let the forgery pass.
- The two approval validators
  automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1 and
  automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1
  already exist and are the reuse target. Harden them; do not replace them.
- automation/orchestration/dispatcher/assignment_executor.py and
  automation/orchestration/work_packets/Move-AiOsPacketState.ps1 both read the
  raw approval boolean and are the two executor trust points to fix.
- A branch-protection plus CODEOWNERS control on the approval_inbox path is the
  correct durable defense, but .github is forbidden to workers, so it is a
  Human-Owner manual step recorded in the report, not a worker edit.

MISSION:
Produce, DRY_RUN first and only after explicit APPLY approval, the design and
proof that closes the self-approval forgery vector. Define an out-of-band
human-approval signal that a worker identity cannot generate, harden the two
existing approval validators to reject forged gates, make the two executors
require the verified signal instead of the raw boolean, add an
approval-integrity validator plus tests that prove a worker-forged gate is
rejected, and record the CODEOWNERS plus branch-protection control as a
Human-Owner manual step. Reuse before adding.

DESIGN SCOPE (Phase 1 design targets):
1. Remediate the live gate record. Design a governed change that restores
   automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json to a safe
   pending state, with approved_by_human set to false and approval_status set to
   pending_review, since a forged approved state reached main. The restore is a
   governed change with a preview diff, not a silent edit.
2. Out-of-band human-approval signal. Design a signal a worker cannot produce.
   The preferred design is an HMAC computed over the packet id plus the allowed
   paths plus the approval timestamp using a key held only by the Human Owner, or
   alternatively a required signed commit or an Approved-by trailer verified in
   continuous integration. Validators MUST FAIL when approved_by_human is true
   and no valid out-of-band signal is present. The key itself is never written
   into the repo, never echoed, and never stored in any tracked file.
3. Harden the two approval validators. Update
   automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1 and
   automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1 to
   reject placeholder or midnight timestamps, reject a free-text bound_by value
   that is not on an explicit actor allowlist, and reject approved_by_human true
   without the verified signal from item 2.
4. Stop executors trusting the raw boolean. In
   automation/orchestration/dispatcher/assignment_executor.py the
   future_apply_approved path, and in
   automation/orchestration/work_packets/Move-AiOsPacketState.ps1 the apply-gate
   assertion, must require the verified out-of-band signal rather than the raw
   approved_by_human boolean.
5. CODEOWNERS plus branch-protection recommendation. Recommend, do NOT edit, a
   CODEOWNERS entry plus a branch-protection rule scoped to the approval_inbox
   path. Because .github is forbidden to workers, this is documented in the final
   report as a Human-Owner manual step only.
6. Approval-integrity validator plus tests. Add an approval-integrity validator
   plus tests that prove a worker-forged gate is rejected. The proof must include
   a forged-gate fixture that the validator rejects.

ALLOWED PATHS:
- automation/orchestration/validators/
- automation/validators/
- automation/orchestration/approval_inbox/
- automation/orchestration/dispatcher/
- automation/orchestration/work_packets/
- tests/
- Reports/governance_hardening/

FORBIDDEN PATHS:
- .github/
- .github/workflows/
- .githooks/
- .git/
- AGENTS.md
- RISK_POLICY.md
- README.md
- WHITEPAPER.md
- ARCHITECTURE.md
- secrets/
- credentials/
- .env
- .env.*
- broker/
- OANDA/
- live_trading/
- automation/orchestration/workers/
- automation/orchestration/locks/
- automation/orchestration/night_supervisor/

HARD LIMITS (a violation fails this packet):
- DRY_RUN is the default. Phase 1 produces design plus a preview diff plan plus a
  validator and test plan only. No file mutation in Phase 1.
- STOP before APPLY. APPLY requires a separate explicit Human Owner approval
  naming this packet ID.
- Do not edit .github or CODEOWNERS or any continuous integration workflow.
  Recommend those controls as Human-Owner manual steps only.
- Do not weaken any existing gate, validator, approval, lock, or stop point. Only
  strengthen them.
- Honor the STOP kill-switch control/self_continuation/STOP.
- All writes in Phase 2 MUST be atomic (temp then rename).
- No scheduler registration. No live notifications. No broker work. No secrets.
  No live trading.
- Do not merge, close, convert to draft, rebase, push, or comment on PR 449,
  PR 451, or PR 460.

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, commit, push, merge, hook install,
approval-inbox mutation, worker-queue mutation, Night Supervisor mutation,
scheduler registration, live notification, live trading, or secret handling. This
packet does not state that the Human Owner explicitly approves commit, push, or
merge; those require a separate explicit approval naming this packet ID.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Read README.md
- Read automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json
- Read automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1
- Read automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1
- Read automation/orchestration/dispatcher/assignment_executor.py
- Read automation/orchestration/work_packets/Move-AiOsPacketState.ps1

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a preview diff plan
for the six design targets, and a validator and test plan. Then STOP for Human
Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
edits to the two existing approval validators, the two executors, the gate
record restore, and the new approval-integrity validator plus tests, run the
validator chain and tests, and stop before commit, push, or merge unless that
same approval explicitly authorizes them.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-GOV-APPROVAL-AUTHORITY-HARDENING-DRY-RUN-FIRST.md
- PowerShell parse check on every changed .ps1 file (the same syntax gate the
  continuous integration validate job runs) in Phase 2
- Python tests for the approval-integrity validator in Phase 2, including the
  worker-forged-gate rejection test
- git diff --check

EXPECTED OUTPUT FILES (Phase 1):
- Reports/governance_hardening/approval_authority_hardening_design_dry_run.md
- Reports/governance_hardening/approval_authority_hardening_validator_result.example.json

FORBIDDEN ACTIONS:
- Do not edit any continuous integration workflow or anything under .github.
- Do not edit CODEOWNERS; recommend it as a Human-Owner manual step only.
- Do not weaken or remove any existing gate, validator, approval, lock, or stop
  point.
- Do not write any key, secret, or token into a tracked file, and do not echo any
  secret value.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not enable live notifications or auto-approve anything.
- Do not merge, close, draft, rebase, push, or comment on PR 449, PR 451, or
  PR 460.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, and validator result.
Stop immediately if preflight branch or worktree state does not match this packet,
if dirty files overlap the mission unsafely, if a required authority file is
missing, if validation fails, if a secret-like value appears, if any scheduler or
live notification appears in scope, if a continuous integration workflow edit
appears in scope, if live trading or broker work appears, or if APPLY approval is
not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the out-of-band signal design
chosen, and the validator chain.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
REUSED VS ADDED:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
