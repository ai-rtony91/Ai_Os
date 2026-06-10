CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. docs/governance/AI_OS_REPO_MEMORY.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_SOS_TELEGRAM_ARMING_V2

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-SOS-TELEGRAM-ARMING-V2-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance SOS arming lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_SOS_TELEGRAM_ARMING

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Arms one live SOS channel so a BLOCKED state or a dead unattended loop actually
pages the operator, closing the silent-death gap that blocks vacation-mode proof.
Read-only recon confirmed there is no SOS arming owner on current main: the prior
SOS packet never merged and its branch is stale, and three SOS branches
(codex sos-only-alert-rule, codex sos-display-vs-wake, lane sos-telegram-tasker-scaffold)
are stale with zero commits ahead of main. This packet supersedes the stale prior
SOS packet and is the single current owner.

ELEVATED RISK NOTICE:
Unlike the additive coordination spine modules, this packet edits an existing
protected runtime file and lifts a deliberate safety block. It changes
services/python_supervisor/notifier.py to allow the Telegram live channel, and it
changes the protected night cycle notifier call. These are owner updates, not
additive new files. They require maximum governance: DRY_RUN-first, operator
supplied credential, no secret committed, the existing enablement gate moved to
approved by the Human Owner, and separate APPLY approval for each phase.

OBJECTIVE (definition of done):
A genuine BLOCKED state delivers an SOS to the operator phone over one live
Telegram channel, a missing credential fails loud instead of silently falling back
to the file channel, and the quiet-by-default severity model is preserved so only
BLOCKED wakes the operator. DRY_RUN-first with a STOP before APPLY and a separate
approval per phase.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- services/python_supervisor/notifier.py is file-channel only. It prints
  LIVE_SEND=BLOCKED for Telegram and returns non-zero for email and push. Severity
  model SOS_WAKE_STATUSES is BLOCKED only.
- notifier.py reads Telegram presence from AIOS_TG_BOT_TOKEN and AIOS_TG_CHAT_ID.
  The PowerShell dispatcher automation/orchestration/notifications/Send-AiOsNotification.ps1
  does not currently expose matching variable names. Reconcile the names so the
  presence check and the sender agree.
- The governed enablement gate already exists at
  relay/approvals/enable-sos-notifier.approval.md with STATUS WAITING. It is the
  canonical enablement mechanism. Do not invent a new gate.
- The android wake helper tools/android/Send-AiosAdbSosWake.ps1 is out of scope and
  must not be armed by this packet.

MISSION:
Implement, DRY_RUN-first and only after explicit per-phase APPLY approval, the
Telegram SOS arming by editing the existing notifier and notification path. Reuse
the existing enablement gate and severity model. Phase 1 produces design plus
preview diff plan plus validator and test plan, then STOPS for Human Owner
approval.

PHASE A MODULE (arm the notifier, gated):
- Reconcile the Telegram environment variable names so notifier presence check and
  the dispatcher sender agree.
- Lift the Telegram hard block in notifier.py for the Telegram channel only, gated
  by both the enablement gate being moved to approved and the credential being
  present in the environment. With no credential present, fail loud and return
  non-zero. Never fall back to the file channel silently for an armed BLOCKED.
- Preserve the severity model so only BLOCKED wakes the operator, and keep dedupe,
  rate-limit, and quiet-hours behavior.
- Add an end to end synthetic BLOCKED test proving the armed path constructs a real
  Telegram send call when the credential is present and fails loud when it is not.

PHASE B MODULE (route the loop, separately gated):
- Change the night cycle so the BLOCKED notifier call routes through the armed
  channel instead of the file channel when arming is enabled, and still uses the
  file channel when arming is not enabled. This is the only night cycle change and
  it must be minimal.

ALLOWED PATHS (write boundary, owner updates require their own approval):
- `services/python_supervisor/notifier.py`
- `automation/orchestration/notifications/`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `tests/orchestration/`
- `Reports/endurance_sos/`

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
- `tools/android/`
- `apps/dashboard/`
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
  mutation. Phase A and Phase B each require a separate explicit APPLY approval.
- The operator supplies the Telegram credential in the environment or an untracked
  local config. Never commit, persist in a tracked file, or embed any token, chat
  id, or secret value. No secret value appears in any committed file.
- The Telegram live path activates only when both the enablement gate is approved
  and the credential is present. Otherwise the path stays blocked and fails loud.
- Do not arm email, push, the android wake helper, or any broker, live order, or
  webhook path. No scheduler registration. No dashboard change.
- Preserve the quiet-by-default severity model where only BLOCKED wakes the
  operator. Do not widen wake statuses.
- Honor the STOP kill-switch control/self_continuation/STOP.
- Do not merge, close, draft, rebase, push, or comment on other PRs or the stale
  SOS branches.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY, separately for Phase A and
Phase B, and must move relay/approvals/enable-sos-notifier.approval.md to approved
before the live path may activate. A validator PASS is evidence only and does not
approve APPLY, commit, push, merge, scheduler registration, live notification, or
secret handling. This packet does not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID and the specific phase.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `services/python_supervisor/notifier.py`
- Read `automation/orchestration/notifications/Send-AiOsNotification.ps1`
- Read `automation/orchestration/notifications/AIOS_ALERT_ROUTING_RULES.example.json`
- Read `relay/approvals/enable-sos-notifier.approval.md`
- Read `automation/orchestration/Invoke-AiOsNightCycle.ps1`

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, a preview diff plan
for Phase A and Phase B, the environment variable reconciliation plan, the loud
fail behavior, and the validator and test plan. Then STOP for Human Owner approval.

PHASE 2A and PHASE 2B (each only after a separate explicit APPLY approval naming
this packet ID and the phase): apply that phase, run the validator chain and tests,
and stop before commit, push, or merge unless that same approval explicitly
authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-SOS-TELEGRAM-ARMING-V2-DRY-RUN-FIRST.md`
- `python -m py_compile services/python_supervisor/notifier.py` in Phase 2
- PowerShell parser check on every changed .ps1 file in Phase 2
- `python -m pytest tests/orchestration` for the new SOS tests in Phase 2
- a targeted scan proving no token, chat id, or secret value is committed
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/endurance_sos/sos_telegram_arming_v2_design_dry_run.md`
- `Reports/endurance_sos/sos_telegram_arming_v2_validator_result.example.json`

FORBIDDEN ACTIONS:
- Do not commit any token, chat id, or secret value.
- Do not arm email, push, android wake, broker, live order, or webhook paths.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not widen the wake severity model.
- Do not change the dashboard.
- Do not commit, push, or merge without separate explicit approval.

STOP POINT:
Stop after producing the Phase 1 design, per-phase preview diff plan, and validator
result. Stop immediately if preflight state does not match this packet, if a
credential or secret value would be committed, if the enablement gate is not yet
approved when a live path is requested, if email push android broker or webhook
arming appears in scope, if a scheduler appears in scope, if validation fails, or
if APPLY approval is not explicit and phase specific.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID and the specific phase, the exact allowed paths, the
credential handling boundary, and the validator chain. The live Telegram path also
requires the enablement gate moved to approved.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
ENV RECONCILIATION:
LOUD FAIL BEHAVIOR:
SECRET HANDLING ASSERTION:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
