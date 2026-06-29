CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER
Project: AI_OS
Repository: ai-rtony91/Ai_Os
Worktree: C:\Dev\Ai.Os
Base branch: main
Working branch: lane/forex-live-capability-governance-unblock-v1
Supervisor identity: ChatGPT planning supervisor
Worker identity: Codex Forex 75-to-100 Overnight governance packet worker
Packet ID: AIOS_FOREX_LIVE_CAPABILITY_GOVERNANCE_UNBLOCK_V2
Mode: LOCAL_APPLY
Zone: FOREX_GOVERNED_LIVE_CAPABILITY_RULES
Lane: Forex / Governance / Live capability enablement

MISSION
Mission ID: AIOS-MISSION-FOREX-PROFITABILITY
Mission Name: Governed Forex Profitability Progression
Program ID: AIOS-PROGRAM-FOREX-DELIVERY
Program Name: Trading Lab / Forex Delivery
Epic ID: AIOS-EPIC-FOREX-LIVE-CAPABILITY-GOVERNANCE
Epic Name: Governed Live Capability Rules
Bucket ID: AIOS-BUCKET-LIVE-TRADE-GOVERNANCE-UNBLOCK
Bucket Name: Replace absolute live-trade block with gated live-capability authority
Packet ID: AIOS_FOREX_LIVE_CAPABILITY_GOVERNANCE_UNBLOCK_V2
Packet Name: Replace categorical live prohibition with governed live-capability gate language

CURRENT VERIFIED ANCHOR
Flow 2 countdown evidence work exists and validates on lane branch.
Current live governance evidence remains single-exception-based.

CORE OBJECTIVE
Edit root authority files to change policy from:

- live trading = blocked except one micro-trade exception

to:

- live trading = allowed only under a Governed Live Forex Capability Gate.

ALLOWED PATHS
- RISK_POLICY.md
- README.md
- WHITEPAPER.md
- docs/architecture/AI_OS_WHITEPAPER.md
- Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md

FORBIDDEN PATHS
- AGENTS.md
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
Anthony is the Human Owner and approval authority.
No commit, no push, no PR merge is authorized by this packet.

PREFLIGHT
Run:
pwd
git status --short --branch
git branch --show-current
git remote -v
git log -1 --oneline

BRANCH HANDLING
Create and switch to: lane/forex-live-capability-governance-unblock-v1
If branch already exists locally, stop and report: STOP_BRANCH_ALREADY_EXISTS.

IMPLEMENTATION OR ACTION REQUIREMENTS
Update `RISK_POLICY.md` with the new Governed Live Forex Capability Gate structure:
- live mode default false
- explicit owner arming required
- required gate fields:
  - broker path
  - account mode
  - instrument
  - side
  - units or notional limit
  - maximum loss per trade
  - daily loss cap
  - stop loss
  - take profit or exit rule
  - order type
  - approval window
  - pre-trade evidence bundle
  - post-trade evidence bundle
  - arming step
  - kill-switch state
  - stop point
- runtime requirements:
  - explicit owner arming
  - kill-switch and loss caps active before arming
  - one controlled order path per gate
  - no retry/autonomous re-entry unless separately approved
  - live evidence before and after execution
  - automatic hard stop on fill, rejection, error, timeout, or approval expiry
- credential rules:
  - runtime-only supply by owner
  - no commit/persistence/logging/print in repo/artifacts/prompts
  - account ids and order IDs sanitized

Update `README.md`, `WHITEPAPER.md`, and `docs/architecture/AI_OS_WHITEPAPER.md` to align with new stage-gated interpretation:
- AIOS is broker-capable through governed stages.
- live execution remains blocked by default except gate-active path.
- one exception becomes a first gate instance, not the only future model.

VALIDATOR CHAIN
python - <<'PY'
from pathlib import Path
required = [
    "RISK_POLICY.md",
    "README.md",
    "WHITEPAPER.md",
    "docs/architecture/AI_OS_WHITEPAPER.md",
    "Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md",
]
for path in required:
    text = Path(path).read_text(encoding='utf-8')
    assert "Governed Live Forex Capability Gate" in text or path.endswith("_REPORT.md"), path
print("TEXT_VALIDATION_PASSED")
PY

git diff --check -- RISK_POLICY.md README.md WHITEPAPER.md docs/architecture/AI_OS_WHITEPAPER.md Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md
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
LIVE_GOVERNANCE_PACKET_STATUS:
FILES_CREATED:
FILES_CHANGED:
POLICY_BEFORE:
POLICY_AFTER:
NEWLY_UNBLOCKED_FUTURE_IMPLEMENTATION:
STILL_BLOCKED:
VALIDATORS_RUN:
VALIDATORS_PASSED:
VALIDATORS_FAILED:
SAFETY_BOUNDARY:
GIT_STATUS:
COMMIT_STATUS:
PUSH_STATUS:
NEXT_SAFE_ACTION:
STOP_POINT_REACHED:
