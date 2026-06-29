CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_SANITIZED_EVIDENCE_CAPTURE_OR_SAFETY_CLOSURE_V1

IDENTITY MARKER
AIOS-CODEX-EAST-PACKET

SUPERVISOR IDENTITY
Codex East Worksite Supervisor

WORKER IDENTITY
EAST_OCC_01

MODE
DRY_RUN

ZONE
East

LANE
forex_delivery_sanitized_evidence_capture

WORKTREE
C:\Dev\Ai.Os

BRANCH
main

MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY
Mission ID: MISSION-AIOS-FOREX-AUTONOMY-COMPLETION-V1
Mission Name: AIOS Forex Autonomy Completion
Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1
Program Name: Forex Profit Autonomy
Epic ID: EPC-FOREX-AUTONOMY-COMPLETION-001
Epic Name: Forex Autonomy Completion Governance
Bucket ID: BKT-FOREX-SANITIZED-EVIDENCE-CAPTURE-001
Bucket Name: Sanitized Evidence Capture And Safety Closure
Packet ID: PKT-FOREX-SANITIZED-EVIDENCE-CAPTURE-OR-SAFETY-CLOSURE-V1
Packet Name: Sanitized Evidence Capture Or Critical Safety Evidence Closure

MISSION
Inspect the current sanitized evidence intake state and prepare the next owner-safe evidence action. If blocked_evidence_fields are present, target critical safety evidence closure first. If only missing_evidence_fields are present, target owner-sanitized evidence capture for those fields. If no evidence gaps are present, recommend only an offline governor rerun and stop.

PRECHECK
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

REQUIRED STATE
- Branch must be main.
- Worktree must be C:\Dev\Ai.Os.
- This packet is DRY_RUN only.
- Do not edit files.
- Do not place trades.
- Do not call broker API.
- Do not read .env.
- Do not use credentials.
- Do not persist account identifiers.
- Do not authorize live trading.
- Do not start schedulers, daemons, loops, webhooks, or background workers.
- Do not commit.
- Do not push.
- Do not create PR.
- Stop if unrelated dirty files exist outside the allowed paths below.

ALLOWED PATHS
Read only:
- automation/forex_engine/supervised_autonomy_governor_v1.py
- automation/forex_engine/forex_autonomy_sanitized_evidence_intake_update_v1.py
- Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json
- Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json

Allowed write paths:
- none

FORBIDDEN PATHS
- .env
- any credential, token, key, secret, account, broker, OANDA, runtime, scheduler, daemon, webhook, production, or live-routing file
- any path outside C:\Dev\Ai.Os
- any path not listed in ALLOWED PATHS

APPROVAL AUTHORITY
Human Owner approval is required before any APPLY packet, commit, push, PR, broker connection, credential use, or live-trading action.

VALIDATORS
python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json
python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json
git status --short --branch

STOP POINT
Stop after producing the DRY_RUN evidence capture or safety closure report. Do not edit, commit, push, create PR, call broker API, read credentials, or authorize live trading.

FINAL REPORT FORMAT
STATUS:
CURRENT_INTAKE_STATUS:
MISSING_EVIDENCE_FIELDS:
BLOCKED_EVIDENCE_FIELDS:
OWNER_SAFE_EVIDENCE_TO_CAPTURE:
CRITICAL_SAFETY_EVIDENCE_TO_CLOSE:
OFFLINE_GOVERNOR_RERUN_RECOMMENDED:
ORDER_EXECUTION:
BROKER_API_USED:
CREDENTIALS_USED:
FILES_CHANGED:
VALIDATORS_RUN:
NEXT_SAFE_ACTION:
GIT_STATUS:
