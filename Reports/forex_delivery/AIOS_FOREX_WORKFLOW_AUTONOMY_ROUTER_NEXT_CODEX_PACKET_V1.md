CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_TO_COLLECTION_CHECKLIST_V1

IDENTITY MARKER
AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_TO_COLLECTION_CHECKLIST_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Workflow Autonomy Router

WORKTREE
C:\Dev\Ai.Os

BRANCH
resolve after preflight

MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY
Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1
Mission Name: Governed Forex Finish Line
Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1
Program Name: Forex Profit Autonomy System
Epic ID: EPC-FOREX-WORKFLOW-AUTONOMY-ROUTER-001
Epic Name: Forex Workflow Autonomy Router
Bucket ID: BKT-FOREX-WORKFLOW-AUTONOMY-ROUTER-001
Bucket Name: Single Next-Safe-Action Forex Router
Packet ID: PKT-FOREX-WORKFLOW-AUTONOMY-ROUTER-V1
Packet Name: Build Forex Workflow Autonomy Router V1

APPROVAL AUTHORITY
Anthony is the only authority for approvals, execution, and evidence changes.
Do not modify owner safety intake template JSON.

PREFLIGHT
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

ALLOWED PATHS
automation/forex_engine/forex_workflow_autonomy_router_v1.py
scripts/forex_delivery/run_forex_workflow_autonomy_router_v1.py
tests/forex_engine/test_forex_workflow_autonomy_router_v1.py
Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_WORKFLOW_AUTONOMY_ROUTER_NEXT_CODEX_PACKET_V1.md
Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md

FORBIDDEN PATHS
AGENTS.md
README.md
WHITEPAPER.md
docs/architecture/AI_OS_WHITEPAPER.md
RISK_POLICY.md
.env
secrets
credential files
broker account identifiers
broker modules
scheduler files
daemon files
webhook files
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\Dev\Ai.Os

MISSION
Produce a structured owner-sanitized evidence collection checklist/report only, then pause. Do not fill owner intake template fields automatically.

RULES
Do not invent evidence.
Do not mark evidence verified.
Do not use broker API.
Do not use credentials.
Do not authorize live trading.
Do not place trades.
Do not read .env.
Do not modify owner intake JSON template.
Do not start schedulers, daemons, loops, webhooks, or background workers.
Do not create PR.

VALIDATOR CHAIN
python scripts/forex_delivery/run_forex_owner_safety_evidence_collection_v1.py --write-state --write-report
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json
git status --short --branch

SAFE NEXT ACTION
Run the owner-safety evidence collection packet to generate a checklist/report, then keep broker_probe: locked, demo_proof: locked, live_micro: locked, live_trading: locked, vacation_mode: locked.

STOP POINT
Stop after generating collection checklist/report. Do not mutate owner evidence template, do not verify evidence, and do not authorize any execution mode.

FINAL REPORT FORMAT
WORKFLOW_STATUS:
ACTIVE_PHASE:
ACTIVE_LANE:
ACTIVE_BLOCKER:
LOCKED_MODES:
NEXT_SAFE_ACTION:
ORDER_EXECUTION:
BROKER_API_USED:
CREDENTIALS_USED:
LIVE_TRADING_AUTHORIZED:
GIT_STATUS:
