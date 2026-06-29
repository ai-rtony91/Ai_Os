CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER
PKT-FOREX-VALUE-FREE-BROKER-PROBE-SCOPE-REVIEW-DRY-RUN-V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

PACKET ID
PKT-FOREX-VALUE-FREE-BROKER-PROBE-SCOPE-REVIEW-DRY-RUN-V1

PACKET NAME
Value-Free Broker Probe Scope Review Dry Run V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

WORKER IDENTITY
Codex

LANE
Forex value-free broker probe scope review

WORKTREE
C:\Dev\Ai.Os

BRANCH
resolve after preflight

MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY
Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1
Mission Name: Governed Forex Finish Line
Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1
Program Name: Forex Profit Autonomy System
Epic ID: EPC-FOREX-FINISH-LINE-CONTROLLER-001
Epic Name: One Script Forex Finish Line Controller
Bucket ID: BKT-FOREX-FINISH-LINE-CONTROLLER-001
Bucket Name: Finish Line Mission Controller And Emoji Dashboard Projection
Packet ID: PKT-FOREX-VALUE-FREE-BROKER-PROBE-SCOPE-REVIEW-DRY-RUN-V1
Packet Name: Value-Free Broker Probe Scope Review Dry Run V1

MISSION
Perform a read-only, owner-approved value-free broker probe scope review using structural safety-closure evidence only.

PREFLIGHT
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_VALUE_FREE_BROKER_PROBE_SCOPE_REVIEW_NEXT_CODEX_PACKET_V1.md

FORBIDDEN PATHS
AGENTS.md
README.md
WHITEPAPER.md
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

APPROVAL AUTHORITY
Human Owner approval required for APPLY, broker/API use, credentials, live trading, scheduler, daemon, webhook, or dashboard mutation.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json
git status --short --branch

SAFE NEXT ACTION
Require owner-approved value-free broker probe scope review with no broker API call, no credentials, no .env read, no account identifiers, no demo action, no live micro authorization, no live trading, no scheduler, no daemon, no webhook, and no order execution.

RULES
Require owner-approved value-free broker probe scope review with no broker API call, no credentials, no .env read, no account identifiers, no demo action, no live micro authorization, no live trading, no scheduler, no daemon, no webhook, and no order execution.
Do not place trades.
Do not use broker API.
Do not use credentials.
Do not read .env.
Do not authorize live trading.
Do not start schedulers, daemons, loops, webhooks, or background workers.
Do not commit.
Do not push.
Do not create PR.

STOP POINT
Stop after read-only broker probe scope review plan and final report. Do not contact any broker.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
WHAT_WAS_INSPECTED:
FINDINGS:
NEXT_SAFE_ACTION:
ORDER_EXECUTION:
BROKER_API_USED:
CREDENTIALS_USED:
GIT_STATUS:
