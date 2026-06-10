CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. RISK_POLICY.md
3. docs/governance/AI_OS_REPO_MEMORY.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

IDENTITY MARKER: AI_OS_PACKET_DRAFT_SELFBUILD_COMPLETION_EVIDENCE_VALIDATOR

SUPERVISOR IDENTITY: Codex West

PACKET ID: AIOS-SELFBUILD-COMPLETION-EVIDENCE-VALIDATOR-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: West self-build trust lane

WORKER IDENTITY: WEST_OCC_01

LANE: AI_OS_SELFBUILD_COMPLETION_EVIDENCE

WORKTREE: C:\Dev\Ai.Os (verified by preflight)

BRANCH: branch FROM main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Read-only discovery of the self-building loop found two open arrows. This packet
closes the most important one: there is no completion evidence validator on main.
AI_OS can generate a goal, generate a packet, validate the packet shape, and run a
packet, but it has nothing that proves a mission actually completed in reality. The
risk pattern is a worker reporting complete, the governance validator reporting
PASS on packet shape, and the real repo state being unchanged or broken. Without a
completion evidence validator every AI_OS build needs a human to verify it, so
AI_OS cannot safely build onto itself. This validator is the trust gate that makes
every other autonomy component dependable.

OBJECTIVE (definition of done):
A new read-only completion evidence validator exists that takes a claimed-complete
packet plus its evidence and returns a verdict of COMPLETION_VERIFIED,
COMPLETION_UNPROVEN, or COMPLETION_CONTRADICTED based on real repo evidence, not on
the worker's own assertion. DRY_RUN-first, additive-only, no mutation, with a STOP
before APPLY.

GROUNDED FINDINGS (verified on main; do NOT re-derive, do NOT duplicate):
- The governance validator automation/validators/aios_governance_validator.py
  validates packet SHAPE only. It does not verify that the claimed work happened.
- The approval authority integrity validator exists and gates approvals; reuse its
  evidence-not-approval posture, do not duplicate it.
- No file on main verifies mission completion against real artifacts. The self-build
  loop arrow run to completion proof is open.

MISSION:
Implement, DRY_RUN-first and only after explicit APPLY approval, one additive
completion evidence validator plus tests. It reuses the evidence-only posture of
the existing validators and adds the missing completion proof. It mutates nothing.
Phase 1 produces design plus preview diff plan plus validator and test plan, then
STOPS for Human Owner approval.

WORK ITEMS:
A. COMPLETION EVIDENCE VALIDATOR. Add automation/validators/aios_completion_evidence_validator.py.
   Given a packet path, a claimed deliverable list, and an evidence report, it must
   verify against real repo evidence, read-only:
   - that each claimed created or changed file actually exists and is non-empty.
   - that the change set stays inside the packet allowed paths and touches no
     forbidden path.
   - that the claimed validation evidence is present, such as a test result summary
     and a diff-scope assertion, rather than a bare claim.
   - that no forbidden hazard appears, such as a secret value, a live trading or
     broker path, or a scheduler registration.
   - that the claimed COMPLETE state is backed by the above, not by the worker word
     alone.
   It returns one verdict: COMPLETION_VERIFIED, COMPLETION_UNPROVEN, or
   COMPLETION_CONTRADICTED, with a reason list and an evidence list. It writes a
   result file only when an explicit output path is given. It mutates no repo state.
B. TESTS. Prove the three verdicts on fixtures: a genuinely complete sample yields
   VERIFIED, a missing-deliverable sample yields UNPROVEN, and a forbidden-path or
   missing-file sample yields CONTRADICTED.

ALLOWED PATHS:
- `automation/validators/`
- `tests/orchestration/`
- `Reports/selfbuild/`
- `telemetry/selfbuild/`

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
- `automation/orchestration/work_packets/`
- `automation/orchestration/coordination_spine/`
- `automation/orchestration/autonomy_loop/`
- `automation/orchestration/packet_runner/`
- `automation/orchestration/Invoke-AiOsNightCycle.ps1`
- `automation/orchestration/scheduler/`
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
- Additive-only. Create files only in the allowed write boundary. The validator is
  read-only over the repo and mutates no state.
- DRY_RUN default. Phase 1 produces design and a preview diff plan only. APPLY is a
  separate explicit approval.
- The validator is evidence only. A VERIFIED verdict does not approve commit, push,
  merge, or any protected action. It only reports whether the claimed work is real.
- Do not weaken or edit the existing governance or approval validators.
- Do not collide with the operator local work in coordination_spine, autonomy_loop,
  or packet_runner. Confirm the working tree is clear of that work and STOP on
  collision risk.
- Honor the STOP kill-switch control/self_continuation/STOP. No scheduler. No live
  sends. No broker. No secrets.
- Do not merge, close, draft, rebase, push, or comment on other PRs.

APPROVAL AUTHORITY:
Anthony Meza the Human Owner must approve before APPLY. A validator PASS is evidence
only and does not approve APPLY, commit, push, merge, scheduler registration, live
notification, live trading, or secret handling. This packet does not state that the Human Owner explicitly approves commit, push, or merge here. Each of commit, push, and merge requires a separate explicit Human Owner approval naming this packet ID.

PREFLIGHT (read-only, before any APPLY work):
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `RISK_POLICY.md`
- Read `README.md`
- Read `automation/validators/aios_governance_validator.py`
- Read `automation/validators/aios_approval_authority_integrity_validator.py`
- Confirm the working tree is clear of operator local self-build work

PHASE 1 (this packet, no APPLY): produce the DRY_RUN design, the preview diff plan,
the verdict model, the evidence checks, and the test plan. Then STOP for Human Owner
approval.

PHASE 2 (only after explicit APPLY approval naming this packet ID): implement the
validator and tests, run the validator chain, and stop before commit, push, or
merge unless that same approval explicitly authorizes them.

VALIDATOR CHAIN:
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-SELFBUILD-COMPLETION-EVIDENCE-VALIDATOR-DRY-RUN-FIRST.md`
- `python -m py_compile automation/validators/aios_completion_evidence_validator.py` in Phase 2
- `python -m pytest tests/orchestration` for the new completion validator tests in Phase 2
- a self-check proving the validator mutates no repo state
- `git diff --check`

EXPECTED OUTPUT FILES (Phase 1):
- `Reports/selfbuild/completion_evidence_validator_design_dry_run.md`
- `Reports/selfbuild/completion_evidence_validator_verdict.example.json`

FORBIDDEN ACTIONS:
- Do not mutate any repo state from the validator.
- Do not weaken the governance or approval validators.
- Do not register any scheduler, service, cron, or systemd unit.
- Do not commit, push, or merge without separate explicit approval.
- Do not store secrets, and do not enable broker, live, or webhook behavior.

STOP POINT:
Stop after producing the Phase 1 design, preview diff plan, verdict model, and
validator result. Stop immediately if preflight state does not match this packet,
if a collision with operator local self-build work is detected, if a forbidden path
would be touched, if validation fails, or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval
naming this packet ID, the exact allowed paths, the verdict model, and the
validator chain.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VERDICT MODEL:
EVIDENCE CHECKS:
COLLISION CHECK:
HARD-LIMIT COMPLIANCE CHECKLIST:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT ACTION:
STATUS: COMPLETE, NO COMMIT, NO PUSH
