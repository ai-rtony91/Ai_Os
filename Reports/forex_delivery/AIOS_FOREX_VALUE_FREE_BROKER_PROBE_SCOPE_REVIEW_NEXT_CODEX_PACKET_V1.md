CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_OWNER_APPROVAL_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_OWNER_APPROVAL_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-VALUE-FREE-BROKER-PROBE-SCOPE-OWNER-APPROVAL-REVIEW-V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Value-Free Broker Probe Scope Owner Approval Review

WORKTREE
C:\Dev\Ai.Os

BRANCH
main

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
BKT-FOREX-BROKER-PROBE-SCOPE-REVIEW-001

BUCKET NAME
Owner-Approved Broker Probe Scope Definition

PACKET NAME
Owner Approval Review Of Value-Free Broker Probe Scope V1

APPROVAL AUTHORITY
Anthony is the only authority for APPLY, commit, push, PR, merge, broker action, demo action, live action, credential use, owner evidence attestation, and live trading authorization.
A later Human Owner message that explicitly approves APPLY is required before any file write.
A later Human Owner message that explicitly approves broker contact is required before any broker contact.
A later Human Owner message that explicitly approves credential use is required before any credential use.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.
A later Human Owner message that explicitly approves merge is required before merge.

MISSION
Perform a DRY_RUN-only owner approval review of the value-free broker probe scope state and report.

This packet must only inspect and summarize the existing value-free broker probe scope review artifacts.
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
This packet must not start schedulers, daemons, loops, webhooks, or background workers.
This packet must not place orders.
This packet must not commit.
This packet must not push.
This packet must not create PR.

PREFLIGHT
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

READ FIRST
AGENTS.md
README.md
WHITEPAPER.md
docs/architecture/AI_OS_WHITEPAPER.md
RISK_POLICY.md

READ SOURCE ARTIFACTS
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROOF_OWNER_STATEMENT_V1.md
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROOF_OWNER_STATEMENT_V1.md
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_STATE.json

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
owner statement modification
owner intake JSON modification
owner evidence artifact modification
finish-line controller code
broker modules
scheduler files
daemon files
webhook files
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\Dev\Ai.Os except temporary validation paths

REQUIRED BEHAVIOR
Confirm whether the value-free broker probe scope review is ready for Human Owner approval review only.
Confirm broker_probe_scope_status.
Confirm owner_statement_present.
Confirm owner_statement_value_free.
Confirm required_negative_declarations_present.
Confirm missing_negative_declarations.
Confirm broker_probe_readiness_approved remains false.
Confirm demo_proof_exists remains false.
Confirm owner_live_micro_exception_approved remains false.
Confirm live_trading_owner_authorization_exists remains false.
Confirm broker_api_used false.
Confirm credentials_used false.
Confirm order_execution false.
Confirm live_trading_authorized false.
Confirm demo_action_authorized false.
Confirm live_micro_authorized false.
Confirm scheduler_started false.
Confirm daemon_started false.
Confirm webhook_started false.
Confirm account_identifier_persisted false.

SAFE NEXT ACTION
Report whether the value-free broker probe scope review is ready for Human Owner approval review only; keep broker contact, credential use, .env access, account identifier use, demo action, live micro action, live trading, scheduler, daemon, webhook, order execution, commit, push, and PR creation blocked.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
git diff --check -- Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_REPORT.md Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_NEXT_CODEX_PACKET_V1.md
git status --short --branch

STOP POINT
Stop after DRY_RUN owner approval review and final report.
Do not edit files.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not authorize demo, live micro, live trading, scheduler, daemon, webhook, or order execution.
Do not commit.
Do not push.
Do not create PR.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
BROKER_PROBE_SCOPE_STATUS:
OWNER_STATEMENT_PRESENT:
OWNER_STATEMENT_VALUE_FREE:
REQUIRED_NEGATIVE_DECLARATIONS_PRESENT:
MISSING_NEGATIVE_DECLARATIONS:
BROKER_PROBE_READINESS_APPROVED:
DEMO_PROOF_EXISTS:
OWNER_LIVE_MICRO_EXCEPTION_APPROVED:
LIVE_TRADING_OWNER_AUTHORIZATION_EXISTS:
BROKER_API_USED:
CREDENTIALS_USED:
ORDER_EXECUTION:
LIVE_TRADING_AUTHORIZED:
DEMO_ACTION_AUTHORIZED:
LIVE_MICRO_AUTHORIZED:
SCHEDULER_STARTED:
DAEMON_STARTED:
WEBHOOK_STARTED:
ACCOUNT_IDENTIFIER_PERSISTED:
NEXT_SAFE_ACTION:
GIT_STATUS:
