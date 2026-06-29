CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER
PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-CLOSURE-DRY-RUN-V1

SUPERVISOR IDENTITY
ChatGPT planning supervisor

PACKET ID
PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-CLOSURE-DRY-RUN-V1

PACKET NAME
Critical Safety Evidence Closure Dry Run V1

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
Epic ID: EPC-FOREX-FINISH-LINE-CONTROLLER-001
Epic Name: One Script Forex Finish Line Controller
Bucket ID: BKT-FOREX-FINISH-LINE-CONTROLLER-001
Bucket Name: Finish Line Mission Controller And Emoji Dashboard Projection
Packet ID: PKT-FOREX-CRITICAL-SAFETY-EVIDENCE-CLOSURE-DRY-RUN-V1
Packet Name: Critical Safety Evidence Closure Dry Run V1

MISSION
Inspect the current blocked safety fields and produce a closure plan for kill switch, daily stop, max loss, and monitoring evidence.

PREFLIGHT
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

ALLOWED PATHS
automation/forex_engine/forex_critical_safety_evidence_closure_v1.py
scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py
tests/forex_engine/test_forex_critical_safety_evidence_closure_v1.py
Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json
Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md
Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md

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
python -m py_compile automation/forex_engine/forex_critical_safety_evidence_closure_v1.py scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py
python -m pytest tests/forex_engine/test_forex_critical_safety_evidence_closure_v1.py -q
python scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py
python -m json.tool Reports/forex_delivery/AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json
git status --short --branch

SAFE NEXT ACTION
Create a read-only closure plan for the remaining critical safety evidence blockers. Do not advance broker, demo, live micro, live trading, or vacation mode.

RULES
Create a read-only closure plan for the remaining critical safety evidence blockers. Do not advance broker, demo, live micro, live trading, or vacation mode.
Do not place trades.
Do not use broker API.
Do not use credentials.
Do not authorize live trading.
Do not start schedulers, daemons, loops, webhooks, or background workers.
Do not commit.
Do not push.
Do not create PR.

STOP POINT
Stop after read-only safety evidence closure plan and final report.

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
