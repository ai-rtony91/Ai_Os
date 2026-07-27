CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_CODEX_APPLY_PACKET
SUPERVISOR IDENTITY: Anthony Human Owner
MODE: APPLY
ZONE: EAST
WORKER IDENTITY: EAST_OCC_01
LANE: forex-first-dollar-canonical-receipt-1326
WORKTREE: /workspace/Ai_Os
BRANCH: work, observed by preflight

MISSION ID: MISSION-AIOS-001
MISSION NAME: First Withdrawable Dollar
PROGRAM ID: PRG-FOREX-001
PROGRAM NAME: Governed Forex Profit Path
EPIC ID: EPC-FOREX-COUNTDOWN-001
EPIC NAME: Repository-Proven Profit Countdown
BUCKET ID: BKT-FOREX-RECEIPTS-001
BUCKET NAME: Canonical Merged Execution Receipts
PACKET ID: PKT-FOREX-FIRST-DOLLAR-CANONICAL-RECEIPT-1326-V1
PACKET NAME: Record and Prove Canonical PR 1326 Receipt

ALLOWED PATHS:
- Reports/forex_delivery/AIOS_FIRST_WITHDRAWABLE_DOLLAR_EXECUTION_RECEIPTS_V1.json
- tests/orchestration/test_aios_work_countdown_v1.py
- automation/orchestration/work_packets/complete/PKT-FOREX-FIRST-DOLLAR-CANONICAL-RECEIPT-1326-V1.md

FORBIDDEN PATHS:
- AGENTS.md
- RISK_POLICY.md
- automation/forex_engine/first_withdrawable_dollar_v1.py
- automation/orchestration/aios_work_countdown_v1.py
- .github/
- secrets/
- credentials/
- .env
- broker/
- live_trading/
- every path not listed in ALLOWED PATHS

APPROVAL AUTHORITY: Anthony supplied verified PR 1326 evidence and explicitly approved exactly one receipt workflow, one commit, and one PR. Merge, broker access, credentials, trading, withdrawal, and money movement remain blocked.

VALIDATOR CHAIN:
- python -m pytest tests/orchestration/test_aios_work_countdown_v1.py tests/forex_engine/test_first_withdrawable_dollar_v1.py -q
- git diff --check
- git diff --cached

STOP POINT: Stop after exactly one commit and exactly one PR. Do not merge, access credentials or brokers, trade, withdraw, or move money.

MISSION: Store the owner-supplied verified PR 1326 receipt in the established Forex delivery evidence root and prove the unchanged artifact receives exactly 3.0 engineering hours of estimate-midpoint credit through the existing inline countdown CLI evidence input.

PREFLIGHT:
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- use the observed clean work branch and treat owner-supplied GitHub evidence as input

APPLY STEPS:
1. Store one canonical receipt envelope in Reports/forex_delivery.
2. Preserve the 3.0-hour estimate-midpoint provenance and do not call it wall-clock time.
3. Add one focused test that supplies the durable artifact through --first-withdrawable-dollar-evidence.
4. Assert exact credit, next blocker, zero presence credit, all protected actions false, and byte-for-byte source immutability.
5. Do not modify countdown or projection logic.
6. Run validators and review the exact three-file diff.
7. Commit once with message `feat(forex): record canonical first-dollar receipt`.
8. Create one PR and stop before merge.

FINAL REPORT FORMAT:
WORKFLOW COMPLETED:
EXECUTION RECEIPT CREATED:
HOURS CREDITED:
COUNTDOWN RESULT:
TESTS:
FILES CHANGED:
NEXT VERIFIED BLOCKER:
OWNER ACTION:
STATUS:
