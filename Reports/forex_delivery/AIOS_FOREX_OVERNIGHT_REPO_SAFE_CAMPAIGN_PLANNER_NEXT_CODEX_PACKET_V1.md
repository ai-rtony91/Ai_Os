CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_NEXT_REPO_SAFE_BUILD_PACKET_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_NEXT_REPO_SAFE_BUILD_PACKET_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-NEXT-REPO-SAFE-BUILD-PACKET-REVIEW-V1

PACKET NAME
Forex Next Repo-Safe Build Packet Review V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Autonomy Completion / Repo-Safe Build Review

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
EPC-FOREX-AUTONOMY-COMPLETION-001

EPIC NAME
Autonomy Completion

BUCKET ID
BKT-FOREX-NEXT-REPO-SAFE-BUILD-REVIEW-001

BUCKET NAME
Next Repo-Safe Build Review

APPROVAL AUTHORITY
Anthony remains the only authority for APPLY, repository history creation, publication, PR creation, integration, broker contact, credentials, .env access, account identifiers, account inspection, order placement, demo execution, live execution, scheduler activation, daemon activation, webhook activation, worker activation, watcher activation, listener activation, and background-loop activation.
This packet is DRY_RUN-only and does not authorize protected actions.

MISSION
Review the finite repo-safe Forex build queue and select the next bounded local artifact packet.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not inspect broker account state.
Do not place orders.
Do not authorize demo or live execution.
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

READ SOURCE ARTIFACTS
Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_BROKER_CONNECTION_PROOF_BOUNDARY_READINESS_V1_STATE.json

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
Confirm campaign_status is REPO_SAFE_OVERNIGHT_BUILD_STAGE_READY.
Confirm the queue is finite and repo-safe only.
Confirm broker connection proof remains protected.
Confirm all broker/action/runtime booleans remain false.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_REPO_SAFE_CAMPAIGN_PLANNER_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN review. Do not execute broker connection proof or any protected runtime action.

SAFE NEXT ACTION
Select only the next bounded repo-safe packet, or stop for Human Owner approval before broker connection proof.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
CAMPAIGN_STATUS:
NEXT_REPO_SAFE_STAGE:
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
