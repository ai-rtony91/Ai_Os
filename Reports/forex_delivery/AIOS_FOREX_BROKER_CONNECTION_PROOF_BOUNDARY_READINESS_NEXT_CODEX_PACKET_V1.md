CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_BROKER_CONNECTION_PROOF_OWNER_REVIEW_DRY_RUN_V1

IDENTITY MARKER
AIOS_FOREX_BROKER_CONNECTION_PROOF_OWNER_REVIEW_DRY_RUN_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-BROKER-CONNECTION-PROOF-OWNER-REVIEW-DRY-RUN-V1

PACKET NAME
Broker Connection Proof Owner Review Dry Run V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Protected Broker Connection Boundary Review

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
BKT-FOREX-BROKER-CONNECTION-PROOF-OWNER-REVIEW-001

BUCKET NAME
Owner Review For Broker Connection Proof

APPROVAL AUTHORITY
Anthony is the only authority for broker contact, credentials, .env access, account identifiers, account inspection, demo execution, live execution, order placement, scheduler activation, daemon activation, webhook activation, background-loop activation, APPLY, repository history creation, publication, PR creation, integration, and live trading authorization.
This packet is DRY_RUN-only and does not approve any protected action.

MISSION
Review the protected broker connection proof boundary using repo evidence only.
Do not execute broker connection proof.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not inspect broker account state.
Do not place orders.
Do not authorize demo execution.
Do not authorize live execution.
Do not start scheduler, daemon, webhook, worker, watcher, listener, or background loop.
Do not create files.
Do not edit files.
Do not create repository history.
Do not publish.
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
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json

FORBIDDEN PATHS
AGENTS.md
README.md
RISK_POLICY.md
.env
.env.*
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
background-loop files
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\Dev\Ai.Os

REQUIRED BEHAVIOR
Confirm readiness_status is OWNER_GATED_BROKER_CONNECTION_PROOF_READY_FOR_REVIEW.
Confirm next protected boundary is broker connection proof.
Confirm owner_wake_required is true.
Confirm broker interface use, credentials, .env access, account identifiers, order placement, demo authorization, live authorization, scheduler, daemon, webhook, and background loop remain false.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN owner review report.
Do not contact broker, use credentials, read .env, use account identifiers, inspect account state, place orders, authorize demo/live action, start scheduler, daemon, webhook, worker, watcher, listener, or background loop.

SAFE NEXT ACTION
Request Human Owner review of the exact broker connection proof scope before any protected broker-facing action.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
READINESS_STATUS:
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
