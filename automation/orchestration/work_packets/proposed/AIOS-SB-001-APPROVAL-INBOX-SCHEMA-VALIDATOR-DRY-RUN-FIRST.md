CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_FROM_BRIDGE_RECOMMENDATION

SUPERVISOR IDENTITY: Codex East

PACKET ID: AIOS-SB-001-APPROVAL-INBOX-SCHEMA-VALIDATOR-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: East orchestration validation

WORKER IDENTITY: EAST_OCC_01

LANE: APPROVAL_INBOX_SCHEMA_VALIDATOR_ONLY

WORKTREE: C:\Dev\Ai.Os

BRANCH: main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Derived from bridge recommendation `AIOS-SB-001` in `Reports/phase_0_to_4_bridge/phase4_self_build_inspection.json`.

MISSION:
Create an APPLY-ready local validator lane for canonical approval inbox schema checks. The lane must read approval inbox files, validate required fields and safety status, emit local evidence, and avoid mutating approvals, worker queue state, Night Supervisor state, hooks, trading systems, secrets, commits, or pushes.

ALLOWED PATHS:
- `automation/validators/`
- `tests/governance/`
- `Reports/phase_0_to_4_bridge/`

FORBIDDEN PATHS:
- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `docs/architecture/AI_OS_WHITEPAPER.md`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/workers/`
- `automation/orchestration/work_packets/active/`
- `automation/orchestration/work_packets/blocked/`
- `automation/orchestration/work_packets/complete/`
- `automation/orchestration/night_supervisor/`
- `.githooks/`
- `.git/`
- `.github/workflows/`
- `telemetry/night_supervisor/`
- `services/`
- `apps/trading_lab/trading_lab/execution/`
- `aios/modules/trader/`
- `.env`
- `secrets/`
- `broker/`
- `OANDA/`
- `live_trading/`

APPROVAL AUTHORITY:
Anthony Meza / Human Owner must approve before APPLY. Validator PASS is evidence only and does not approve APPLY, commit, push, merge, hook install, approval mutation, worker queue mutation, Night Supervisor mutation, live trading, broker runtime work, or secret handling.

PREFLIGHT:
Run these read-only checks before any APPLY work:
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `README.md`
- Read `Reports/phase_0_to_4_bridge/phase4_self_build_inspection.json`
- Read `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- Read `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`

AFFECTED FILES:
- `automation/validators/aios_approval_inbox_schema_validator.py`
- `tests/governance/test_approval_inbox_schema_validator.py`
- `Reports/phase_0_to_4_bridge/approval_inbox_schema_validator_dry_run.example.json`

EXPECTED OUTPUT FILES:
- `Reports/phase_0_to_4_bridge/approval_inbox_schema_validator_dry_run.example.json`

VALIDATOR CHAIN:
- `python -m py_compile automation/validators/aios_approval_inbox_schema_validator.py`
- `python -m pytest tests/governance`
- `python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root .`
- `git diff --check`
- Existing secret-scan or governance validator if present and safe: `python automation/validators/aios_governance_validator.py --sample-check`

FORBIDDEN ACTIONS:
- Do not mutate approval inbox state.
- Do not mutate worker inbox or worker registry state.
- Do not start Night Supervisor runtime.
- Do not install hooks.
- Do not commit.
- Do not push.
- Do not merge.
- Do not create branches unless separately approved.
- Do not run live trading.
- Do not enable broker runtime work.
- Do not read, print, create, or move secrets.
- Do not call external services.
- Do not create network tunnels.

STOP POINT:
Stop after producing the validator, tests, example evidence, and validation results. Stop immediately if preflight branch/worktree state does not match this packet, if dirty files overlap the mission in an unsafe way, if any required authority file is missing, if validation fails, if a secret-like value appears, if live trading or broker runtime work appears in scope, or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval naming this packet ID, the exact allowed paths, and the exact validation chain. Commit and push require separate later approvals.
This packet does not state that Anthony explicitly approves commit, push, or merge.

FINAL REPORT FORMAT:
Use this exact completion format:

SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS: COMPLETE, NO COMMIT, NO PUSH
