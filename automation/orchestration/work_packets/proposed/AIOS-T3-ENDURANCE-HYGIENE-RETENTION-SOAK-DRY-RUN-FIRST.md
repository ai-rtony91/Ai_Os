CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_ENDURANCE_HYGIENE_SOAK

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-T3-ENDURANCE-HYGIENE-RETENTION-SOAK-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West endurance hygiene lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_ENDURANCE_HYGIENE_SOAK

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Derived from the AI_OS endurance hardening roadmap and an inspection of the
hygiene, recovery, watchdog, and self-continuation lanes. Grounded by reading
the rotation script, the disk-space watcher, the orphan reclaimer, and the
endurance roadmap listed in PREFLIGHT below. This packet targets the Tier-3
resource-exhaustion and long-run trust gaps that turn an unattended loop from a
demo into a multi-day, vacation-length survivor.

OBJECTIVE (definition of done):
Make the unattended loop safe for multi-day and vacation-length runs by closing
the resource-exhaustion and long-run trust gaps, then prove it with a soak
ladder. Today only plain log files are rotated, every JSON-lines ledger grows
unbounded, there is no retention or prune anywhere, the disk-space backstop only
works on Windows and only alerts, there are no runaway or cost circuit breakers,
and there is no multi-day soak evidence. This packet is DRY_RUN-FIRST: Phase 1
produces design plus a preview diff plan plus a validator and test plan, then
STOPS for Human Owner APPLY approval. No mutation in Phase 1. No scheduler is
registered in any phase here.

GROUNDED FINDINGS (verified by the operator review lane; reuse, do NOT re-derive
or fork these components):
- Rotate-AiOsLogs.ps1 already rotates plain log files by size and age, archives
  by date folder, compresses aged archives to gzip, and writes a delete manifest.
  It handles only files matching the log filter; JSON-lines ledgers are not in
  scope today. Extend its size-and-age pattern to ledgers; do not rewrite it.
- Watch-AiOsDiskSpace.ps1 measures free space by enumerating drive letters, which
  is Windows-only, and its only action is to send an alert through the
  notification script. Its state file is written in place, not atomically. This is
  the Windows-only, alert-only backstop the mission replaces.
- Reclaim-AiOsOrphans.ps1 already moves stranded task files between relay
  subfolders by age and never deletes content. It exists but is not wired to run
  each cycle, so tasks can sit stranded in the relay running directory. Reuse it
  as the sweeper; only add the per-cycle wiring.
- The atomic-write pattern used elsewhere is write-temp plus Move-Item -Force.
  Every new or changed state write in this lane must follow it. The disk backstop
  state write must be converted to this pattern.

MISSION:
Design, DRY_RUN-first and only after explicit APPLY approval, the endurance
hygiene, retention, backstop, circuit-breaker, and soak-evidence capabilities
that let the unattended loop run for multiple days without exhausting resources
or losing operator trust. Phase 1 of this packet is design plus preview diff plan
plus validator and test plan only, ending in a STOP for Human Owner APPLY
approval. Reuse the existing atomic-write and hygiene patterns before adding
anything new. If a design target is already satisfied by existing code, report
that and skip the addition. Registering the unattended scheduler is explicitly
out of scope here and remains a separate final Human-Owner step that must follow
successful soak evidence.

DESIGN SCOPE (Phase 1 design targets, no mutation):
1. LEDGER ROTATION. Extend the rotation design to JSON-lines ledgers by size and
   by age, covering the work ledger, the cost ledger, the supervisor cycle
   ledger, and the forex journals. Reuse the size-and-age, date-folder archive,
   gzip-on-age, and delete-manifest pattern already proven on plain logs. Rotation
   of an append-only ledger must preserve a clean cut so no in-flight line is
   torn, and the live ledger is re-created empty after the cut.
2. RETENTION AND PRUNE. Add a retention and prune policy for telemetry, relay,
   reports, and checkpoints, expressed as keep-by-age and keep-by-count windows
   with a preview-then-prune flow. Wire the existing orphan reclaimer so tasks
   stranded in the relay running directory are swept each cycle, using its
   existing move-only, never-delete behavior. Prune must default to preview and
   must write a delete manifest before removing anything.
3. CROSS-PLATFORM DISK BACKSTOP. Replace the Windows-only, alert-only backstop
   with a cross-platform one that measures filesystem free space on the path that
   actually holds the repository and acts by pruning or quarantining, not just
   alerting. Its state write must be atomic using write-temp plus Move-Item
   -Force. Keep an alert as a signal, but make the action prune or quarantine
   under a hard free-space floor, defaulting to preview before any prune.
4. CIRCUIT BREAKERS AND BOUNDED SELF-CONTINUATION. Add a runaway breaker and a
   cost breaker plus bounded self-continuation guardrails so an unattended run
   cannot loop without bound or spend without bound. The runaway breaker bounds
   cycles per window and trips to a stop-and-log state on excess. The cost breaker
   reads the cost ledger and trips to stop-and-log when a configured ceiling is
   reached. Self-continuation must remain bounded and must honor the STOP
   kill-switch at control/self_continuation/STOP, exiting immediately if STOP
   exists.
5. SOAK HARNESS AND LADDER. Build a soak harness and a soak ladder of
   progressively longer unattended runs, capturing heartbeat freshness, memory
   growth, disk growth, and cycle-marker progression as evidence written under
   the soak reports directory. The ladder steps from a short run, to a one-day
   run, to a multi-day run, each gated on the prior step passing its evidence
   thresholds. The harness only observes and records; it does not approve APPLY.
6. ALERT RESILIENCE AND DEDUPE PROOF. Add off-local-network alert resilience and
   a multi-day dedupe behavior proof so a repeated condition over many days does
   not flood the operator while still surfacing a genuine new event. Preserve the
   quiet-by-default severity model; alerts remain local in this lane and no live
   send is performed. Registering the unattended scheduler remains a separate
   final Human-Owner step that must follow successful soak evidence and is out of
   scope here.

ALLOWED PATHS:
- automation/orchestration/hygiene/
- automation/orchestration/recovery/
- automation/orchestration/self_continuation/
- automation/orchestration/watchdog/
- telemetry/
- tests/
- Reports/endurance_soak/

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
- automation/orchestration/night_supervisor/

HARD LIMITS (a violation fails this packet):
- DRY_RUN is the default. Phase 1 is design only, with no mutation. STOP before
  any APPLY.
- Do NOT register any scheduler, service, cron, or systemd unit. The scheduler is
  a separate final Human-Owner step that must follow successful soak evidence.
- All state-file writes MUST be atomic using write-temp plus Move-Item -Force. No
  in-place writes on state files.
- No live notifications and no live sends. Alerts are written to local telemetry
  only and preserve the quiet-by-default severity model.
- No live trading, no broker work, no secret handling.
- Honor the STOP kill-switch at control/self_continuation/STOP everywhere; never
  continue past STOP.
- Prune and quarantine default to preview; a delete manifest is written before
  anything is removed.
- Do not modify, close, comment on, or otherwise act on any other pull request or
  packet.

APPROVAL AUTHORITY:
Anthony Meza, the Human Owner, must approve before APPLY. A validator PASS is
evidence only and does not approve APPLY, scheduler registration, live
notification, live trading, secret handling, approval-inbox mutation, or lock
mutation. This packet does not state that the Human Owner explicitly approves
commit, push, or merge; those would each require a separate explicit approval
naming this packet ID.

PREFLIGHT (read-only, before any APPLY work):
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- Read AGENTS.md
- Read RISK_POLICY.md
- Read README.md
- Read automation/orchestration/hygiene/Rotate-AiOsLogs.ps1
- Read automation/orchestration/hygiene/Watch-AiOsDiskSpace.ps1
- Read automation/orchestration/recovery/Reclaim-AiOsOrphans.ps1
- Read docs/roadmap/AIOS_ENDURANCE_HARDENING_ROADMAP.md

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the proposed diffs as
preview text, and the validator and test plan, plus the validator proof on this
packet path. Then STOP for Human Owner APPLY approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): apply the
diffs, run the validator chain and the PowerShell parser checks and Python tests,
and stop before commit, push, or merge unless that same approval explicitly
authorizes them.

VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-T3-ENDURANCE-HYGIENE-RETENTION-SOAK-DRY-RUN-FIRST.md
- PowerShell parser checks on every changed .ps1 file in Phase 2, matching the
  syntax gate the validate job runs
- Python tests in Phase 2 for the rotation, retention, backstop, breaker, and
  soak-evidence logic
- git diff --check

EXPECTED OUTPUT FILES (Phase 1):
- Reports/endurance_soak/hygiene_retention_soak_design_dry_run.md
- Reports/endurance_soak/hygiene_retention_soak_validator_result.example.json

FORBIDDEN ACTIONS:
- Do not register any scheduler, service, cron, or systemd unit.
- Do not enable live notifications, live sends, or auto-approve anything.
- Do not change packet, approval, lock, or worker-queue flow.
- Do not delete content outside a previewed, manifested prune.
- Do not refactor or rename unrelated scripts.
- Do not commit, push, or merge without a separate explicit approval.
- Do not run live trading or broker work, and do not store secrets.

STOP POINT:
Stop after producing the Phase 1 design, preview diffs, and validator result. Stop
immediately if preflight branch or worktree state does not match this packet, if
dirty files overlap the mission unsafely, if a required authority file is missing,
if validation fails, if a secret-like value appears, if any scheduler or live
notification appears in scope, if live trading or broker work appears, or if APPLY
approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the ledger rotation cut behavior,
the retention and prune windows, the disk free-space floor, the breaker
thresholds, and the validator chain.

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
