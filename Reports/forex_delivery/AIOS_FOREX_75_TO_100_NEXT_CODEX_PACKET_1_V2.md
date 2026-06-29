CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER
Project: AI_OS
Repository: ai-rtony91/Ai_Os
Worktree: C:\Dev\Ai.Os
Base branch: lane/forex-flow2-supervised-demo-evidence-countdown-capture-v1
Working branch: lane/forex-flow2-supervised-demo-evidence-countdown-capture-v1
Supervisor identity: ChatGPT planning supervisor
Worker identity: Codex Forex 75-to-100 Overnight Packet-1 execution worker
Packet ID: AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_LANDING_V1
Mode: LOCAL_APPLY
Zone: FOREX_COMPLETION_DISCOVERY_PACKET_FACTORY_AND_OVERNIGHT_QUEUE
Lane: Forex / 75-to-100 / overnight completion campaign

MISSION
Mission ID: AIOS-MISSION-FOREX-PROFITABILITY
Mission Name: Governed Forex Profitability Progression
Program ID: AIOS-PROGRAM-FOREX-DELIVERY
Program Name: Trading Lab / Forex Delivery
Epic ID: AIOS-EPIC-FOREX-LIVE-CAPABILITY-GOVERNANCE
Epic Name: Governed Live Capability Rules
Bucket ID: AIOS-BUCKET-LIVE-TRADE-GOVERNANCE-UNBLOCK
Bucket Name: Replace absolute live-trade block with gated live-capability authority
Packet ID: AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_LANDING_V1
Packet Name: Land validated Flow 2 evidence countdown work for owner handoff

CURRENT VERIFIED ANCHOR
PR #1199 merged.
Main is synced after PR #1199.
Previous runner selected:
AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1
Flow2 files remain available and uncommitted on current lane branch.

CORE OBJECTIVE
Create a safe owner handoff for the existing Flow 2 evidence countdown work by validating and preserving its scoped files, without touching live governance or execution code.

ALLOWED PATHS
- automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py
- tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py
- Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md

FORBIDDEN PATHS
- AGENTS.md
- README.md
- WHITEPAPER.md
- RISK_POLICY.md
- docs/architecture/AI_OS_WHITEPAPER.md
- .env
- .env.*
- *.key
- *.pem
- *.p12
- *.pfx
- secrets/*
- credentials/*
- any broker adapter code
- any broker credential file
- any order execution code
- any webhook file
- any scheduler file
- any daemon file
- any file outside ALLOWED PATHS

APPROVAL AUTHORITY
Anthony is the Human Owner and execution authority for this packet.
This packet does not authorize governance authority edits, broker/API access, credentials, or live execution.

PREFLIGHT
Run:
pwd
git status --short --branch
git branch --show-current
git remote -v
git log -1 --oneline

This packet is discovery-preserving and does not require main-state alignment.

BRANCH HANDLING
- Use current branch if it already matches current work (`lane/forex-flow2-supervised-demo-evidence-countdown-capture-v1`).
- Do not switch branches.

IMPLEMENTATION OR ACTION REQUIREMENTS
1. Validate required Flow 2 files:
   - compile module
   - run scoped tests
   - run diff check
2. Confirm report content exists and reflects exact scope.
3. Produce completion handoff and keep all Flow 2 files unchanged (or only report-scope updates to improve handoff metadata if needed).
4. Do not modify governance files.

VALIDATOR CHAIN
python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py
python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q
git diff --check -- automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md
git status --short --branch

PROCESS-LAUNCH FAILURE RULE
If CreateProcessAsUserW failed: 1312 occurs, retry once.
If it fails a second time, stop immediately and return:
SANDBOX_LAUNCH_FAILURE

STOP POINT
Stop after local APPLY and validation.
Do not commit.
Do not push.
Do not create a PR.
Do not merge.
Do not place orders.
Do not access broker APIs.
Do not request credentials.

FINAL REPORT FORMAT
FLOW2_PACKET_STATUS:
FILES_CREATED:
FILES_CHANGED:
VALIDATORS_RUN:
VALIDATORS_PASSED:
VALIDATORS_FAILED:
SAFETY_BOUNDARY:
GIT_STATUS:
COMMIT_STATUS:
PUSH_STATUS:
NEXT_SAFE_ACTION:
STOP_POINT_REACHED:
