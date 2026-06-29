CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_OWNER_SAFETY_EVIDENCE_RETURN_READINESS_REVIEW_V1

IDENTITY MARKER
AIOS_FOREX_OWNER_SAFETY_EVIDENCE_RETURN_READINESS_REVIEW_V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

WORKER IDENTITY
Codex

MODE
DRY_RUN

ZONE
Trading Lab / Forex

LANE
Forex Owner Safety Evidence Return Readiness Review

WORKTREE
C:\Dev\Ai.Os

BRANCH
resolve after preflight

MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY
Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1
Mission Name: Governed Forex Finish Line
Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1
Program Name: Forex Profit Autonomy System
Epic ID: EPC-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-001
Epic Name: Owner Safety Evidence Collection
Bucket ID: BKT-FOREX-OWNER-SAFETY-EVIDENCE-COLLECTION-001
Bucket Name: Owner Critical Safety Evidence Collection
Packet ID: PKT-FOREX-OWNER-SAFETY-EVIDENCE-RETURN-READINESS-REVIEW-V1
Packet Name: Owner Safety Evidence Return Readiness Review V1

APPROVAL AUTHORITY
Human Owner approval is required before APPLY execution, PR creation, broker/API use, credential use, live trading authorization, scheduler activation, daemon activation, webhook activation, dashboard mutation, or order execution.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.

MISSION
Read the owner safety evidence collection state and report whether owner-returned evidence can be prepared for a later verification packet. Do not inspect private evidence, do not verify evidence, and do not mutate files.

PREFLIGHT
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

ALLOWED PATHS
Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md

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

CURRENT OWNER EVIDENCE MISSING
kill_switch_state, daily_stop_state, max_loss_state, monitoring_ready

RULES
Do not invent evidence.
Do not verify evidence.
Do not place trades.
Do not use broker API.
Do not use credentials.
Do not read .env.
Do not authorize live trading.
Do not start schedulers, daemons, loops, webhooks, or background workers.
Do not commit.
Do not push.
Do not create PR.

VALIDATOR CHAIN
python -m json.tool Reports/forex_delivery/AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json
git status --short --branch

SAFE NEXT ACTION
Prepare a later owner evidence verification packet only after sanitized owner evidence is available; keep broker, demo, live micro, live trading, and vacation modes locked.

STOP POINT
Stop after read-only readiness report. Do not commit. Do not push. Do not create PR.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
OWNER_EVIDENCE_MISSING:
EVIDENCE_VERIFIED_BY_THIS_PACKET:
NEXT_SAFE_ACTION:
ORDER_EXECUTION:
BROKER_API_USED:
CREDENTIALS_USED:
GIT_STATUS:
