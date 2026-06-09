CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_SOS_LASTMILE

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-ENDURANCE-SOS-LASTMILE-ARMING-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance SOS lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_SOS_ARMING

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

ALLOWED PATHS:
- services/python_supervisor/
- automation/orchestration/notifications/
- automation/orchestration/Invoke-AiOsNightCycle.ps1
- tests/
- Reports/endurance_sos/

FORBIDDEN PATHS:
- .github/
- .github/workflows/
- .githooks/
- .git/
- AGENTS.md
- RISK_POLICY.md
- README.md
- secrets/
- credentials/
- .env
- .env.*
- broker/
- OANDA/
- live_trading/
- automation/orchestration/approval_inbox/
- automation/orchestration/locks/

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, hook install, approval-inbox mutation,
lock mutation, scheduler registration, secret handling, or any live send beyond
the single approved channel. This packet does not state that the Human Owner
explicitly approves commit, push, or merge; each of those requires a separate
explicit approval naming this packet ID.

MISSION:
Arm exactly ONE live SOS channel end to end so that a BLOCKED state or a dead
unattended loop actually pages the operator, closing the silent-death gap. Today
the night cycle calls the notifier with the file channel only, and
services/python_supervisor/notifier.py hard-blocks email, push, and live
telegram, so a 2 AM BLOCKED writes a local file and reaches nobody. This packet
lifts a deliberate safety block and therefore must be DRY_RUN-FIRST and
APPLY-gated, with credentials supplied by the operator and never committed.
Phase 1 produces design plus a preview diff plan plus a validator and test plan,
then STOPS for Human Owner APPLY approval. The armed restart supervisor and the
git timeouts are tracked separately under packet
AIOS-ENDURANCE-T1-WEEKEND-CRASH-SURVIVAL items B and C and are out of scope here.

DESIGN SCOPE (Phase 1 design targets, no mutation in this phase):
1. Provision ONE channel, Telegram, using an operator-supplied credential stored
   only in an untracked local config file, never committed. The design must name
   the untracked config path, show the gitignore expectation, and prove the value
   itself never appears in any tracked file or report.
2. Reconcile the environment-variable name mismatch. The notifier presence check
   in services/python_supervisor/notifier.py reads one set of names while the
   dispatcher Send-AiOsNotification in
   automation/orchestration/notifications/Send-AiOsNotification.ps1 looks up a
   different set. The design must list both name sets side by side and make them
   agree on a single canonical pair, with a documented mapping for any legacy
   alias.
3. Lift the telegram hard block in services/python_supervisor/notifier.py for the
   telegram channel only, under APPLY governance, preserving the severity model
   where only a genuine BLOCKED wakes the human. Email and push stay blocked.
4. Route the night-cycle BLOCKED notifier call in
   automation/orchestration/Invoke-AiOsNightCycle.ps1 through the armed channel
   instead of the file channel, keeping the file channel as a parallel local
   record rather than the only sink.
5. Make a missing credential a LOUD failure, not a silent fall back to the file
   channel, so a misconfiguration cannot look healthy while paging nobody. The
   design must define the explicit non-zero failure path and the operator-facing
   error text.
6. Add an end to end synthetic BLOCKED test that proves a real phone is reached,
   plus dedupe, rate-limit, and quiet-hours behavior preserved. The test must be
   runnable on demand by the operator with the operator credential present, and
   must skip cleanly with a clear SKIPPED reason when no credential is present.

GROUNDED FINDINGS (verified by the operator review lane; do not re-derive):
- services/python_supervisor/notifier.py defaults to a file-only channel and
  carries an intentional disable on email, push, and live telegram. The wake
  model is quiet by default; only BLOCKED is an SOS wake. Preserve that model.
- The presence check and the dispatcher lookup disagree on credential variable
  names; that mismatch alone can make an armed channel silently no-op. Fixing the
  names is a precondition for any reliable page.
- The night-cycle BLOCKED path currently invokes the notifier with the file
  channel, which is why a local file is the only artifact a 2 AM BLOCKED produces.

HARD LIMITS (a violation fails this packet):
- DRY_RUN is the default. Phase 1 is design only, with no file mutation outside
  the single report directory artifacts described below. STOP before APPLY.
- The operator supplies credentials in an untracked local config. Never write,
  echo, log, or store any secret or token value in any tracked file, report,
  diff preview, or test fixture. A targeted scan must confirm this before STOP.
- Lift the block for the telegram channel ONLY. Email and push remain disabled.
- No scheduler registration of any kind. No service install, no schtasks, no
  cron, no systemd. No broker work. No live trading.
- Honor the STOP kill-switch control/self_continuation/STOP everywhere; exit
  immediately if it exists.
- All state-file or config writes proposed in the design must be atomic, temp
  plus replace, never an in-place rewrite of a live file.
- Preserve the quiet-by-default severity model where only a genuine BLOCKED wakes
  the human. Do not widen the wake set.
- Do not merge, close, or comment on any other pull request.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-ENDURANCE-SOS-LASTMILE-ARMING-DRY-RUN-FIRST.md
- PowerShell parser checks on every changed .ps1 file in Phase 2, the same syntax
  gate the CI validate job runs
- python tests in Phase 2 covering the synthetic BLOCKED page, dedupe,
  rate-limit, and quiet-hours preservation
- git diff --check
- a targeted scan confirming no credential or token value is committed in any
  tracked file, report, or diff preview

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Read README.md
- Read services/python_supervisor/notifier.py
- Read automation/orchestration/notifications/Send-AiOsNotification.ps1
- Read automation/orchestration/notifications/AIOS_ALERT_ROUTING_RULES.example.json
- Read docs/workflows/AIOS_SOS_ARMING_RUNBOOK.md if present

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the proposed diffs as
preview text, the variable-name reconciliation table, the loud-failure path, the
test plan, and the validator proof. Then STOP for Human Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
diffs, run the validator chain and the tests, and stop before commit, push, or
merge unless that same approval explicitly authorizes them.

EXPECTED OUTPUT FILES (Phase 1):
- Reports/endurance_sos/sos_lastmile_arming_design_dry_run.md
- Reports/endurance_sos/sos_lastmile_arming_validator_result.example.json

FORBIDDEN ACTIONS:
- Do not register any scheduler, service, cron, or systemd unit.
- Do not arm email or push; only the single telegram channel is in scope.
- Do not write, log, or commit any credential or token value.
- Do not widen the wake set beyond BLOCKED.
- Do not change packet, approval, lock, or worker-queue flow.
- Do not refactor or rename unrelated scripts.
- Do not commit, push, or merge without separate explicit approval.
- Do not run live trading or broker work.

STOP POINT:
Stop after producing the Phase 1 design, the preview diffs, the reconciliation
table, the test plan, and the validator result. Stop immediately if preflight
branch or worktree state does not match this packet, if dirty files overlap the
mission unsafely, if a required authority file is missing, if validation fails,
if a secret-like value appears in any tracked artifact, if any scheduler or any
second live channel appears in scope, if live trading or broker work appears, or
if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the single telegram channel, the
canonical credential variable names, the untracked config path, and the validator
and test chain.

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
