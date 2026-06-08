CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_PACKET_DRAFT_FROM_BRIDGE_HARDENING_ADDENDUM

SUPERVISOR IDENTITY: Codex East

PACKET ID: AIOS-APP-SERVICE-BRIDGE-V0-DRY-RUN-FIRST

MODE: DRY_RUN-FIRST

ZONE: East local service bridge

WORKER IDENTITY: EAST_OCC_02

LANE: AI_OS_APP_SERVICE_BRIDGE_V0

WORKTREE: C:\Dev\Ai.Os

BRANCH: main, verified before APPLY by preflight

SOURCE RECOMMENDATION:
Derived from the bridge-hardening addendum after inspection of `services/orchestrator`, `services/dispatcher`, `services/python_supervisor`, `automation/orchestration/openai_api_bridge`, `docs/AI_OS/dispatch/AIOS_OPENAI_PACKET_DISPATCH_FLOW.md`, and `docs/roadmap/AIOS_FULL_AUTONOMY_BRIDGE_MAP.md`.

MISSION:
Prepare and implement, only after explicit APPLY approval, a local-first AI_OS App Service Bridge v0 that coordinates inert packet intake, local planner-call previews, Codex execution queue previews, approval inbox status, worker queue status, worker lock status, latest Reports status, telemetry receipts, and SOS-only notification preview events.

ALLOWED PATHS:
- `services/orchestrator/`
- `services/package.json`
- `tests/services/`
- `automation/validators/`
- `Reports/phase_0_to_4_bridge/`
- `docs/workflows/`

FORBIDDEN PATHS:
- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `ARCHITECTURE.md`
- `.github/workflows/`
- `.githooks/`
- `.git/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/workers/`
- `automation/orchestration/work_packets/active/`
- `automation/orchestration/work_packets/blocked/`
- `automation/orchestration/work_packets/complete/`
- `automation/orchestration/night_supervisor/`
- `telemetry/night_supervisor/`
- `apps/trading_lab/trading_lab/execution/`
- `aios/modules/trader/`
- `.env`
- `.env.*`
- `secrets/`
- `credentials/`
- `broker/`
- `OANDA/`
- `live_trading/`

APPROVAL AUTHORITY:
Anthony Meza / Human Owner must approve before APPLY. Validator PASS is evidence only and does not approve APPLY, commit, push, merge, hook install, approval mutation, worker queue mutation, Night Supervisor mutation, live trading, broker runtime work, provider API calls, cloud deployment, tunnel creation, or secret handling.

PREFLIGHT:
Run these read-only checks before any APPLY work:
- `pwd`
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- Read `AGENTS.md`
- Read `README.md`
- Read `services/orchestrator/index.js`
- Read `services/orchestrator/runtimeApiService.js`
- Read `services/package.json`
- Read `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- Read `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- Read `automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json`
- Read `docs/workflows/AI_OS_API_INTEGRATION_SAFETY_WORKFLOW.md`

TARGET SERVICE FRAMEWORK:
Use the existing repo-native Node/Express `services/orchestrator` layer unless preflight proves it is unusable. Do not add FastAPI or install new dependencies in this packet.

MINIMAL ENDPOINTS:
- `GET /health`
- `POST /packets`
- `GET /queue`
- `POST /approvals`
- `GET /workers`
- `GET /reports/latest`
- `POST /sos`

V0 BEHAVIOR:
- `GET /health` returns local service status and safety boundary.
- `POST /packets` accepts a packet draft and returns validation/route preview only.
- `GET /queue` reads canonical queue and worker inbox status only.
- `POST /approvals` accepts an approval request preview and returns required Human Owner action only.
- `GET /workers` reads worker registry, worker inbox, and lock status only.
- `GET /reports/latest` reads latest bridge/report evidence only.
- `POST /sos` records or previews SOS-only notification events only after local DRY_RUN validation.
- Local planner-call handling must use fixtures or preview records only. No live provider call is allowed in v0.
- Codex execution queue handling must create preview records only. It must not launch Codex or run queued commands.

STATE STORE:
Use local JSONL receipts for v0 unless a later design review approves SQLite. Proposed generated-output root: `telemetry/app_service_bridge/`, with `.gitignore` handling proposed in DRY_RUN before any APPLY write.

EXPECTED OUTPUT FILES:
- `Reports/phase_0_to_4_bridge/app_service_bridge_v0_design_dry_run.md`
- `Reports/phase_0_to_4_bridge/app_service_bridge_v0_endpoint_contract.example.json`
- `Reports/phase_0_to_4_bridge/app_service_bridge_v0_validator_result.example.json`

VALIDATOR CHAIN:
- `node --check services/orchestrator/index.js`
- `node --check services/orchestrator/runtimeApiService.js`
- `npm --prefix services run typecheck`
- `python automation/validators/aios_governance_validator.py --sample-check`
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-APP-SERVICE-BRIDGE-V0-DRY-RUN-FIRST.md`
- `git diff --check`

FORBIDDEN ACTIONS:
- Do not implement cloud hosting.
- Do not deploy Azure App Service.
- Do not create tunnels.
- Do not make live model-provider calls.
- Do not store secrets.
- Do not create `.env` files.
- Do not mutate approval inbox state.
- Do not mutate worker queue state.
- Do not mutate worker locks.
- Do not start Night Supervisor runtime.
- Do not launch Codex.
- Do not run queued commands.
- Do not auto-run APPLY.
- Do not install hooks.
- Do not commit.
- Do not push.
- Do not merge.
- Do not run live trading.
- Do not enable broker runtime work.

NIGHT SUPERVISOR INTEGRATION PROPOSAL:
Expose read-only bridge health, pending approval counts, worker queue counts, lock status, latest report path, and SOS preview status for Night Supervisor reports. Night Supervisor must remain sandboxed and must not mutate service state without a later approved packet.

CODEX WORKER QUEUE INTEGRATION PROPOSAL:
Expose Codex-ready packet previews and queue status only. Any actual Codex execution must remain a separate explicit operator action or separately approved packet.

STOP POINT:
Stop after producing the local service bridge design, endpoint contract, DRY_RUN validator, and validation result. Stop immediately if preflight branch/worktree state does not match this packet, if dirty files overlap the mission in an unsafe way, if dependency installation is required, if any required authority file is missing, if validation fails, if a secret-like value appears, if live trading or broker runtime work appears in scope, if cloud/tunnel/deployment behavior appears, or if APPLY approval is not explicit.

HUMAN APPROVAL REQUIREMENT BEFORE APPLY:
This packet is a draft. APPLY requires a separate explicit Human Owner approval naming this packet ID, exact allowed paths, endpoint behavior, local state store boundary, and validation chain. This packet does not state that Anthony explicitly approves commit, push, or merge.

FINAL REPORT FORMAT:
Use this exact completion format:

SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
APP SERVICE BRIDGE DECISION:
SAFE NEXT COMMAND:
STATUS: COMPLETE, NO COMMIT, NO PUSH
