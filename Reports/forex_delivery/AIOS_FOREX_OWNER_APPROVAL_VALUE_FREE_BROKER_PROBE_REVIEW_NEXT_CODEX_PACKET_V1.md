CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_FIRST_READ_ONLY_BROKER_PROBE_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_FIRST_READ_ONLY_BROKER_PROBE_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-FIRST-READ-ONLY-BROKER-PROBE-REVIEW-V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
First Read-Only Broker Probe Review

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
BKT-FOREX-FIRST-READ-ONLY-BROKER-PROBE-REVIEW-001

BUCKET NAME
First Read-Only Broker Probe Review

PACKET NAME
First Read-Only Broker Probe Review V1

APPROVAL AUTHORITY
Anthony is the only authority for APPLY, commit, push, PR, merge, broker action, demo action, live action, credential use, owner evidence attestation, and live trading authorization.
A later Human Owner message that explicitly approves broker contact is required before any broker contact.
A later Human Owner message that explicitly approves credential use is required before any credential use.
A later Human Owner message that explicitly approves .env access is required before any .env access.
A later Human Owner message that explicitly approves sanitized output fields is required before any broker-derived output is generated.
A later Human Owner message that explicitly approves APPLY is required before any file write.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.
A later Human Owner message that explicitly approves merge is required before merge.

MISSION
Perform a DRY_RUN-only readiness review for the first read-only broker probe path after owner approval of the value-free broker probe scope.

This packet must only inspect local governance artifacts and report whether the first read-only broker probe can be prepared under owner-approved boundaries.
This packet must not create files.
This packet must not modify files.
This packet must not contact a broker.
This packet must not use credentials.
This packet must not read .env.
This packet must not use account identifiers.
This packet must not inspect private broker data.
This packet must not persist endpoint URLs.
This packet must not persist exact balances.
This packet must not persist screenshots.
This packet must not persist raw broker payloads.
This packet must not persist order IDs.
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
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_STATE.json

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_REPORT.md
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
broker modules
execution code
trading code
demo code
live code
order code
scheduler files
daemon files
webhook files
dashboard mutation files
owner statement modification
owner intake JSON modification
owner evidence artifact modification
finish-line controller code
unrelated docs
unrelated tests
any path outside C:\Dev\Ai.Os except temporary validation paths

REQUIRED BEHAVIOR
Confirm owner_approval_review_status.
Confirm owner_approval_status.
Confirm source_scope_review_status.
Confirm source_owner_statement_present.
Confirm source_owner_statement_value_free.
Confirm source_required_negative_declarations_present.
Confirm source_missing_negative_declarations.
Confirm broker_probe_readiness_approved remains false unless a separate owner approval artifact explicitly changes it.
Confirm demo_proof_exists remains false.
Confirm owner_live_micro_exception_approved remains false.
Confirm live_trading_owner_authorization_exists remains false.
Confirm broker_api_used false.
Confirm credentials_used false.
Confirm env_file_read false.
Confirm account_identifiers_used false.
Confirm account_identifier_persisted false.
Confirm order_execution false.
Confirm demo_authorized false.
Confirm live_authorized false.
Confirm live_micro_authorized false.
Confirm scheduler_started false.
Confirm daemon_started false.
Confirm webhook_started false.
Report whether the first read-only broker probe path can move to an owner-approved, separately tokenized probe packet.

SAFE NEXT ACTION
Report whether the first read-only broker probe path is ready for a separate owner-approved probe packet. Keep broker contact, credential use, .env access, account identifier use, demo action, live micro action, live trading, scheduler, daemon, webhook, order execution, commit, push, and PR creation blocked unless Anthony provides explicit approval in a later packet.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json
git diff --check -- Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_V1_REPORT.md Reports/forex_delivery/AIOS_FOREX_OWNER_APPROVAL_VALUE_FREE_BROKER_PROBE_REVIEW_NEXT_CODEX_PACKET_V1.md
git status --short --branch

STOP POINT
Stop after DRY_RUN first read-only broker probe readiness review and final report.
Do not edit files.
Do not contact broker.
Do not use credentials.
Do not read .env.
Do not use account identifiers.
Do not inspect private broker data.
Do not authorize demo, live micro, live trading, scheduler, daemon, webhook, or order execution.
Do not commit.
Do not push.
Do not create PR.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
OWNER_APPROVAL_REVIEW_STATUS:
OWNER_APPROVAL_STATUS:
SOURCE_SCOPE_REVIEW_STATUS:
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
ENV_FILE_READ:
ACCOUNT_IDENTIFIERS_USED:
ACCOUNT_IDENTIFIER_PERSISTED:
ORDER_EXECUTION:
DEMO_AUTHORIZED:
LIVE_AUTHORIZED:
LIVE_MICRO_AUTHORIZED:
SCHEDULER_STARTED:
DAEMON_STARTED:
WEBHOOK_STARTED:
NEXT_SAFE_ACTION:
GIT_STATUS:
