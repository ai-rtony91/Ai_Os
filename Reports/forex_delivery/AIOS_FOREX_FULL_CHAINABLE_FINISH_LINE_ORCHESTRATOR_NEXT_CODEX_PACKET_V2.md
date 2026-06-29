CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_FIRST_READ_ONLY_BROKER_PROBE_REVIEW_RELAY_DRY_RUN_V2

IDENTITY MARKER
AIOS_FOREX_FIRST_READ_ONLY_BROKER_PROBE_REVIEW_RELAY_DRY_RUN_V2

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-FIRST-READ-ONLY-BROKER-PROBE-REVIEW-RELAY-DRY-RUN-V2

PACKET NAME
First Read-Only Broker Probe Review Relay Dry Run V2

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
First Read-Only Broker Probe Review Relay Dry Run

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
EPC-FOREX-BROKER-PROBE-SCOPE-REVIEW-001

EPIC NAME
Value-Free Broker Probe Scope Review

BUCKET ID
BKT-FOREX-FIRST-READ-ONLY-BROKER-PROBE-REVIEW-001

BUCKET NAME
First Read-Only Broker Probe Review

APPROVAL AUTHORITY
Anthony is the only authority for APPLY, commit, push, PR, merge, broker contact, credential use, .env access, account identifier use, demo action, live action, order execution, scheduler activation, daemon activation, webhook activation, background-loop activation, and live trading authorization.
A later Human Owner message that explicitly approves APPLY is required before any file write.
A later Human Owner message that explicitly approves broker contact is required before any broker contact.
A later Human Owner message that explicitly approves credential use is required before any credential use.
A later Human Owner message that explicitly approves .env access is required before any .env access.
A later Human Owner message that explicitly approves account identifier use is required before any account identifier use.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.
A later Human Owner message that explicitly approves merge is required before merge.

MISSION
Perform a DRY_RUN-only relay review for the first read-only broker probe path from current repo evidence.

This packet may inspect only listed local artifacts.
This packet must not create files.
This packet must not modify files.
This packet must not contact a broker.
This packet must not use credentials.
This packet must not read .env.
This packet must not use account identifiers.
This packet must not inspect private broker data.
This packet must not authorize demo action.
This packet must not authorize live micro action.
This packet must not authorize live trading.
This packet must not start scheduler, daemon, webhook, or background loop.
This packet must not place orders.
This packet must not commit.
This packet must not push.
This packet must not create PR.

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
Confirm the orchestrator current stage is first read-only broker probe review.
Confirm next protected boundary remains owner approval before broker contact, credentials, .env access, account identifiers, demo action, live action, order execution, scheduler, daemon, webhook, or background loop.
Confirm all safety booleans remain false.
Report whether the next non-repo-only stage requires OWNER_WAKE_REQUIRED.

SAFE NEXT ACTION
Stop after DRY_RUN relay review. Keep protected Forex boundary locked unless Anthony provides explicit later approval in a complete tokenized packet.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_FULL_CHAINABLE_FINISH_LINE_ORCHESTRATOR_V2_STATE.json
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
git status --short --branch

STOP POINT
Stop after DRY_RUN relay review and final report.
Do not edit files.
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
CURRENT_STAGE:
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
