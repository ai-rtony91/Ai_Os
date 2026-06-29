CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER
Project: AI_OS
Repository: ai-rtony91/Ai_Os
Worktree: C:\Dev\Ai.Os
Base branch: lane/forex-live-capability-governance-unblock-v1
Working branch: lane/forex-profit-loop-acceleration-v1
Supervisor identity: ChatGPT planning supervisor
Worker identity: Codex Forex 75-to-100 overnight profit-loop packet worker
Packet ID: AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1
Mode: LOCAL_APPLY
Zone: FOREX_PROFIT_LOOP_ACCELERATION
Lane: Forex / Profit loop / next-candidate gate

MISSION
Mission ID: AIOS-MISSION-FOREX-PROFITABILITY
Mission Name: Governed Forex Profitability Progression
Program ID: AIOS-PROGRAM-FOREX-DELIVERY
Program Name: Trading Lab / Forex Delivery
Epic ID: AIOS-EPIC-FOREX-LIVE-CAPABILITY-GOVERNANCE
Epic Name: Governed Live Capability Rules
Bucket ID: AIOS-BUCKET-LIVE-TRADE-GOVERNANCE-UNBLOCK
Bucket Name: Replace absolute live-trade block with gated live-capability authority
Packet ID: AIOS_FOREX_PROFIT_LOOP_ACCELERATION_GATE_V1
Packet Name: Build next-candidate profitability gate with closed-demo evidence requirements

CURRENT VERIFIED ANCHOR
Flow 2 evidence countdown module is validated on current working branch.
Governed live capability policy packet is expected to land before this packet.

CORE OBJECTIVE
Create or repair the profit-loop gate path so close-demo evidence leads to a next-candidate recommendation under controlled risk boundaries:
- closed-trade capture
- realized P/L classification
- candidate ranking
- walk-forward sample sufficiency
- mitigation and expectancy blockers
- owner review handoff

ALLOWED PATHS
- automation/forex_engine/
- tests/forex_engine/
- Reports/forex_delivery/

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
- secrets/
- credentials/
- any broker adapter code
- any broker credential file
- any order execution code
- any webhook file
- any scheduler file
- any daemon file
- any file outside ALLOWED PATHS

APPROVAL AUTHORITY
Anthony is Human Owner and approval authority.
No broker API access, credentials, order execution, or live trading is authorized by this packet.

PREFLIGHT
pwd
git status --short --branch
git branch --show-current
git remote -v
git log -1 --oneline

BRANCH HANDLING
Create and switch to: lane/forex-profit-loop-acceleration-v1
If branch already exists locally, stop and report:
STOP_BRANCH_ALREADY_EXISTS

IMPLEMENTATION OR ACTION REQUIREMENTS
1. Implement or repair modules and tests that compute and report:
   - closed demo trade evidence completeness
   - realized P/L summaries (bucketed and sanitized)
   - candidate score/selection output with blockers
   - walk-forward evidence sufficiency checks
2. Ensure no live execution logic is added.
3. Keep evidence schema JSON-safe and sanitize account/order identifiers where present.

VALIDATOR CHAIN
python -m pytest tests/forex_engine/test_candidate_to_gate_bridge_v1.py tests/forex_engine/test_candidate_scoring_v1.py tests/forex_engine/test_candidate_evidence_intake_v1.py -q
python -m py_compile automation/forex_engine/*.py
git diff --check -- automation/forex_engine/ tests/forex_engine/ Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_1_V2.md
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
Do not place trades.
Do not access broker APIs.
Do not request credentials.

FINAL REPORT FORMAT
PROFIT_LOOP_PACKET_STATUS:
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
