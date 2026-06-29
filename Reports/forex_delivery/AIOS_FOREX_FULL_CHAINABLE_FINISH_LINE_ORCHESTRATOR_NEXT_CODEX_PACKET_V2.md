CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_BROKER_CONNECTION_PROOF_PROTECTED_BOUNDARY_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_BROKER_CONNECTION_PROOF_PROTECTED_BOUNDARY_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-BROKER-CONNECTION-PROOF-PROTECTED-BOUNDARY-REVIEW-V1

PACKET NAME
Broker Connection Proof Protected Boundary Review V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Protected Broker Connection Boundary

WORKTREE
C:\Dev\Ai.Os

BRANCH
resolve after preflight

MISSION ID
MISSION-AIOS-FOREX-FINISH-LINE-V1

MISSION NAME
Governed Forex Finish Line

PROGRAM ID
PROGRAM-FOREX-PROFIT-AUTONOMY-V1

PROGRAM NAME
Forex Profit Autonomy System

EPIC ID
EPC-FOREX-BROKER-CONNECTION-PROOF-001

EPIC NAME
Broker Connection Proof Protected Boundary

BUCKET ID
BKT-FOREX-BROKER-CONNECTION-PROOF-PROTECTED-BOUNDARY-001

BUCKET NAME
Owner Approval Gate For Broker Connection Proof

APPROVAL AUTHORITY
Anthony is the only authority for broker contact, credentials, .env access, account identifiers, demo action, live action, order execution, scheduler activation, daemon activation, webhook activation, background-loop activation, APPLY, commit, push, PR, merge, and live trading authorization.
This packet is DRY_RUN-only and does not approve any protected action.
Anthony explicitly approves commit before any commit.
Anthony explicitly approves push before any push.
Anthony explicitly approves merge before any merge.

MISSION
Review the protected boundary now reached after exhausting repo-only Forex finish-line work.
Confirm that the next stage is broker connection proof and that it requires Human Owner approval before broker contact, credentials, .env access, account identifiers, or broker account status inspection.
Do not execute the broker connection proof.
Do not contact a broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not inspect private broker data.
Do not authorize demo action.
Do not authorize live micro action.
Do not authorize live trading.
Do not start scheduler, daemon, webhook, or background loop.
Do not place orders.
Do not create files.
Do not edit files.
Do not commit.
Do not push.
Do not create PR.

PREFLIGHT
cd C:\Dev\Ai.Os
pwd
git status --short --branch
git branch --show-current
git log -1 --oneline

READ FIRST
AGENTS.md
README.md
RISK_POLICY.md
docs/governance/AI_OS_REPO_MEMORY.md
docs/governance/aios-identity-and-lane-governance.md

READ SOURCE ARTIFACTS
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json

FORBIDDEN PATHS
AGENTS.md
README.md
RISK_POLICY.md
.env
secrets
credentials
broker account identifiers
broker modules
order modules
demo execution modules
live execution modules
scheduler files
daemon files
webhook files
background loops
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\Dev\Ai.Os except temporary validation paths

REQUIRED BEHAVIOR
Confirm completed repo-only stage count is 1.
Confirm remaining repo-only stage count is 0.
Confirm protected stage count is 12.
Confirm the next protected boundary is broker connection proof.
Confirm all safety booleans remain false.
Report that OWNER_WAKE_REQUIRED is true before any broker-facing action.

SAFE NEXT ACTION
Stop and request Human Owner approval for the exact broker connection proof scope before any broker contact, credential use, .env access, account identifier use, private broker data inspection, order execution, demo action, live action, scheduler, daemon, webhook, or background loop.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN protected boundary review and final report.
Do not execute broker connection proof.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not authorize demo, live micro, live trading, scheduler, daemon, webhook, background loop, or order execution.
Do not commit.
Do not push.
Do not create PR.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
COMPLETED_REPO_ONLY_STAGE_COUNT:
REMAINING_REPO_ONLY_STAGE_COUNT:
PROTECTED_STAGE_COUNT:
CURRENT_AUTONOMY_LEVEL:
NEXT_PROTECTED_BOUNDARY:
OWNER_WAKE_REQUIRED:
BROKER_API_USED:
CREDENTIALS_USED:
ENV_READ:
ACCOUNT_IDENTIFIERS_USED:
ORDER_EXECUTION:
DEMO_AUTHORIZED:
LIVE_AUTHORIZED:
SCHEDULER_STARTED:
DAEMON_STARTED:
WEBHOOK_STARTED:
BACKGROUND_LOOP_STARTED:
NEXT_SAFE_ACTION:
GIT_STATUS:
