CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER
PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-OWNER-COLLECTION-DRY-RUN-V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

PACKET ID
PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-OWNER-COLLECTION-DRY-RUN-V1

PACKET NAME
Critical Safety Evidence Owner Collection Dry Run V1

MODE
DRY_RUN

ZONE
Trading Lab / Forex

WORKER IDENTITY
Codex

LANE
Forex critical safety evidence closure

WORKTREE
C:\Dev\Ai.Os

BRANCH
resolve after preflight

MISSION / PROGRAM / EPIC / BUCKET / PACKET IDENTITY
Mission ID: MISSION-AIOS-FOREX-FINISH-LINE-V1
Mission Name: Governed Forex Finish Line
Program ID: PROGRAM-FOREX-PROFIT-AUTONOMY-V1
Program Name: Forex Profit Autonomy System
Epic ID: EPC-FOREX-CRITICAL-SAFETY-CLOSURE-001
Epic Name: Critical Safety Evidence Closure
Bucket ID: BKT-FOREX-CRITICAL-SAFETY-CLOSURE-001
Bucket Name: Forex Critical Safety Evidence Closure
Packet ID: PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-OWNER-COLLECTION-DRY-RUN-V1
Packet Name: Critical Safety Evidence Owner Collection Dry Run V1

MISSION
Inspect the remaining critical safety evidence blockers and produce an owner evidence collection checklist without inventing evidence.

PREFLIGHT
pwd
git status --short --branch
git branch --show-current
git remote -v

ALLOWED PATHS
automation/forex_engine/forex_critical_safety_evidence_closure_v1.py
scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py
Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md

FORBIDDEN PATHS
AGENTS.md
README.md
RISK_POLICY.md
.env
secrets
credential files
broker account identifiers
broker modules
scheduler files
daemon files
webhook files
any path outside C:\Dev\Ai.Os

APPROVAL AUTHORITY
Human Owner approval required for APPLY, broker/API use, credentials, live trading, scheduler, daemon, webhook, or dashboard mutation.
A later Human Owner message that explicitly approves commit is required before commit.
A later Human Owner message that explicitly approves push is required before push.

VALIDATOR CHAIN
python scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py
git status --short --branch

SAFE NEXT ACTION
Collect or repair evidence for: kill_switch_state, daily_stop_state, max_loss_state, monitoring_ready.

RULES
Collect or repair evidence for: kill_switch_state, daily_stop_state, max_loss_state, monitoring_ready.
Do not invent evidence.
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
Stop after read-only critical safety evidence closure inspection and final report.

FINAL REPORT FORMAT
STATUS:
CURRENT_BRANCH:
CURRENT_HEAD:
SAFETY_COMPLETION_PERCENT:
VERIFIED_CONTROLS:
BLOCKED_CONTROLS:
NEXT_SAFE_ACTION:
ORDER_EXECUTION:
BROKER_API_USED:
CREDENTIALS_USED:
GIT_STATUS:
