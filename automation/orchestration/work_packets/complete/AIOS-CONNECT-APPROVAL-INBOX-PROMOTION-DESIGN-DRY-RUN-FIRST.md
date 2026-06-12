CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_CONNECT_APPROVAL_PROMOTION

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-CONNECT-APPROVAL-INBOX-PROMOTION-DESIGN-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West approval promotion design lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_CONNECT_APPROVAL_PROMOTION

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE FINDING (connection gap M6):
The operation glue local approval inbox at
control/operation_glue/APPROVAL_INBOX.json is never promoted to the canonical
approval inbox at
automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json. The helper
automation/orchestration/glue/Update-AiOsApprovalInbox.DRY_RUN.ps1 has zero
callers in the repository. As a result, factory-generated approval candidates
never reach the canonical inbox surface. This is a connection gap, not a request
to wire the two surfaces together autonomously.

CRITICAL SAFETY CONTEXT (do NOT re-derive):
The canonical approval inbox is the single human-approval authority surface and
was the target of a prior self-approval forgery that was hardened by the
approval-authority integrity work. The integrity validator
automation/validators/aios_approval_authority_integrity_validator.py exists and
already protects this surface. Any auto-promotion that wrote approved_by_human or
set an approval state would re-open exactly the forgery class that the integrity
work closed. Therefore this packet is DESIGN AND RECOMMENDATION ONLY.

OBJECTIVE (definition of done):
Produce a design report plus a recommendation that documents the
local-to-canonical promotion gap and proposes a Human-Owner-gated promotion flow.
The deliverable is a design report, not an executable promoter. No code that
mutates the canonical approval inbox, and no code that mutates the local approval
inbox, is in scope. DRY_RUN first, with a STOP before APPLY.

GROUNDED FINDINGS (already verified; do NOT re-derive):
- The canonical inbox file
  automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json exists and
  carries authority_status active_authority with approval authority held by the
  Human Owner.
- The helper Update-AiOsApprovalInbox.DRY_RUN.ps1 exists under
  automation/orchestration/glue/ and has zero callers, so the promotion path is
  unbuilt by design rather than broken.
- The approval-authority integrity validator
  automation/validators/aios_approval_authority_integrity_validator.py exists and
  is the out-of-band human signal source that any future promotion must depend
  on.

MISSION:
Document the current local-to-canonical approval promotion gap, state the safety
requirement that any future promotion must carry the out-of-band human signal
from the approval-authority integrity validator and must never set
approved_by_human autonomously, and propose a gated promotion flow in which a
worker may only stage a candidate for human review while the Human Owner performs
the actual canonical write. Output is a design report only. Do not implement an
executable promoter. Do not write or mutate any approval inbox file, canonical or
local.

DESIGN SCOPE (Phase 1, design and recommendation only):
1. Document the gap. Describe the current state in which the local glue approval
   inbox at control/operation_glue/APPROVAL_INBOX.json is never carried to the
   canonical inbox at
   automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json, and in which
   the Update-AiOsApprovalInbox helper has zero callers. Describe the resulting
   effect that factory-generated approval candidates never reach the canonical
   surface.
2. State the safety requirement. Any future promotion must carry the out-of-band
   human signal verified by
   automation/validators/aios_approval_authority_integrity_validator.py and must
   never set approved_by_human autonomously. The promotion step must remain a
   Human-Owner-gated step. A validator PASS is evidence only and does not stand in
   for the human signal.
3. Propose a gated promotion flow. Design a flow in which a worker may only stage
   a candidate record into a review-only holding area for human inspection, and in
   which the Human Owner alone performs the actual canonical write into
   automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json. The worker
   path is staging only and is forbidden from touching either inbox file. The
   design must show where the out-of-band human signal is checked before any
   canonical write, and must show that approved_by_human is never set by any
   automated step.

ALLOWED PATHS:
- Reports/governance_promotion/
- docs/architecture/
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
- automation/orchestration/approval_inbox/
- control/operation_glue/
- automation/orchestration/Invoke-AiOsNightCycle.ps1
- automation/orchestration/scheduler/
- apps/dashboard/
- tools/android/
- secrets/
- credentials/
- .env
- .env.*
- broker/
- OANDA/
- live_trading/
- webhooks/

HARD LIMITS (a violation fails this packet):
- DRY_RUN is the default. This packet is DESIGN AND RECOMMENDATION ONLY.
- Do not write or mutate any approval inbox file, canonical or local.
- Do not implement an executable promoter.
- Any future promotion must require the out-of-band human signal and must never
  set approved_by_human autonomously.
- STOP before APPLY. APPLY requires a separate explicit Human Owner approval
  naming this packet ID.
- Honor the STOP kill-switch control/self_continuation/STOP.
- No scheduler registration. No live sends. No broker work. No secrets. No live
  trading.
- Do not merge, close, convert to draft, rebase, or comment on any other PR.

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, commit, push, merge, approval-inbox
mutation, local glue mutation, scheduler registration, live send, live trading,
or secret handling. This packet does not state that the Human Owner explicitly approves commit, push, or merge; those require a separate explicit approval naming this packet ID.

PREFLIGHT (read-only, before any work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Read README.md
- Read automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json
- Read automation/validators/aios_approval_authority_integrity_validator.py if present
- Read automation/orchestration/glue/Update-AiOsApprovalInbox.DRY_RUN.ps1 if present

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design report and the gated
promotion flow recommendation under the allowed paths only. Then STOP for Human
Owner APPLY approval.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-CONNECT-APPROVAL-INBOX-PROMOTION-DESIGN-DRY-RUN-FIRST.md
- git diff --check
- a scan proving no approval inbox file is written, canonical or local, by
  confirming git status shows no change under
  automation/orchestration/approval_inbox/ and no change under
  control/operation_glue/

EXPECTED OUTPUT FILES (Phase 1):
- Reports/governance_promotion/approval_inbox_promotion_design_dry_run.md
- docs/architecture/approval_inbox_promotion_gated_flow.md

FORBIDDEN ACTIONS:
- Do not write or mutate any approval inbox file, canonical or local.
- Do not implement an executable promoter or wire the helper to any caller.
- Do not set approved_by_human or any approval state in any file.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not enable live sends or auto-approve anything.
- Do not write any secret or token into a tracked file, and do not echo any
  secret value.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.
- Do not merge, close, draft, rebase, or comment on any other PR.

STOP POINT:
Stop after producing the Phase 1 design report and gated promotion flow
recommendation. Stop immediately if preflight branch or worktree state does not
match this packet, if dirty files overlap the mission unsafely, if a required
authority file is missing, if validation fails, if a secret-like value appears,
if any scheduler or live send appears in scope, if any approval inbox mutation
appears in scope, if live trading or broker work appears, or if APPLY approval is
not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID and the exact allowed paths. The design itself recommends
that the canonical promotion write always remains a Human-Owner-gated step.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
SAFETY REQUIREMENT:
RECOMMENDATION:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
