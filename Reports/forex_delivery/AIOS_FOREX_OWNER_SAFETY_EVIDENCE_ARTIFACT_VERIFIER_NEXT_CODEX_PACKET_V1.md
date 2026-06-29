CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_UPDATE_V1

IDENTITY MARKER
AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_UPDATE_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-FINISH-LINE-SAFETY-CLOSURE-CONSUMER-UPDATE-V1

MODE
APPLY

ZONE
Trading Lab / Forex

LANE
Forex Finish-Line Safety-Closure Consumer Update

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
EPC-FOREX-FINISH-LINE-SAFETY-CLOSURE-CONSUMER-UPDATE-001

EPIC NAME
Finish-Line Safety-Closure Consumer Update

BUCKET ID
BKT-FOREX-FINISH-LINE-SAFETY-CLOSURE-CONSUMER-UPDATE-001

BUCKET NAME
Consume Structurally Verified Owner Safety Evidence

PACKET NAME
Update Finish-Line Safety-Closure Consumer From Structurally Verified Owner Evidence

APPROVAL AUTHORITY
Anthony is the only authority for APPLY, commit, push, PR, merge, broker action, demo action, live action, credential use, owner evidence attestation, and live trading authorization.

A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.
A later Human Owner message that explicitly approves merge is required before merge.

MISSION
Update only the finish-line safety-closure consumer state/report to consume the structurally verified owner safety evidence artifact verifier output. This packet may not verify live operational control, may not claim broker readiness, and may not authorize demo, live micro, live trading, scheduler, daemon, webhook, credentials, broker API, or order execution.

PREFLIGHT
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_ARTIFACT_VERIFIER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_ARTIFACT_VERIFIER_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_REPORT.md

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
owner intake JSON modification
owner evidence artifact modification
broker modules
scheduler files
daemon files
webhook files
dashboard mutation files
unrelated docs
unrelated tests
any path outside C:\Dev\Ai.Os

RULES
Do not modify owner intake JSON.
Do not modify owner evidence artifact files.
Do not invent evidence.
Do not read .env.
Do not use credentials.
Do not use broker API.
Do not authorize live trading.
Do not place trades.
Do not start schedulers, daemons, loops, webhooks, or background workers.
Do not commit.
Do not push.
Do not create PR.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_ARTIFACT_VERIFIER_V1_STATE.json
git diff --check -- Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_SAFETY_CLOSURE_CONSUMER_V1_REPORT.md
git status --short --branch

SAFE NEXT ACTION
Consume structural owner evidence verification in the finish-line safety-closure consumer only; keep broker, demo, live micro, live trading, scheduler, daemon, webhook, credentials, broker API, and order execution locked.

STOP POINT
Stop after validators and final report. Do not commit. Do not push. Do not create PR.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
SOURCE_ARTIFACT_VERIFIER_STATUS:
CONSUMER_STATUS:
OPERATIONAL_CONTROL_VERIFIED:
BROKER_API_USED:
CREDENTIALS_USED:
ORDER_EXECUTION:
LIVE_TRADING_AUTHORIZED:
GIT_STATUS:
