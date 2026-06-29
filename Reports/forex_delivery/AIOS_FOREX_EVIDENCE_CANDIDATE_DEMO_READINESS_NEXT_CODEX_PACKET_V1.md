CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_REPO_SAFE_EVIDENCE_QUEUE_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_REPO_SAFE_EVIDENCE_QUEUE_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

PACKET ID
PKT-FOREX-REPO-SAFE-EVIDENCE-QUEUE-REVIEW-V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Autonomy Completion / Repo-Safe Evidence Queue Review

WORKTREE
C:\Dev\Ai.Os

BRANCH
resolve after preflight

MISSION
Review the finite repo-safe evidence queue and select a bounded non-broker packet.

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_REPORT.md

FORBIDDEN PATHS
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
any path outside C:\Dev\Ai.Os

APPROVAL AUTHORITY
This packet is DRY_RUN-only. It does not approve APPLY, repository history creation, publication, PR creation, broker contact, credentials, .env access, account identifiers, account inspection, demo/live execution, orders, scheduler, daemon, webhook, worker, watcher, listener, or background loop.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_NEXT_REPO_SAFE_QUEUE_V1_STATE.json
git status --short --branch

STOP POINT
Stop after read-only queue review.

SAFE NEXT ACTION
Select one bounded repo-safe evidence packet, or stop for Human Owner approval before any protected boundary.

FINAL REPORT FORMAT
STATUS:
QUEUE_STATUS:
RECOMMENDED_NEXT_PACKET:
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
