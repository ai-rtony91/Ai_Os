CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_CODEX_APPLY_PACKET
SUPERVISOR IDENTITY: Anthony Human Owner
MODE: APPLY
ZONE: EAST
WORKER IDENTITY: EAST_OCC_01
LANE: forex-first-dollar-countdown-cli-evidence
WORKTREE: /workspace/Ai_Os
BRANCH: work, observed by preflight

MISSION ID: MISSION-AIOS-001
MISSION NAME: First Withdrawable Dollar
PROGRAM ID: PRG-FOREX-001
PROGRAM NAME: Governed Forex Profit Path
EPIC ID: EPC-FOREX-COUNTDOWN-001
EPIC NAME: Repository-Proven Profit Countdown
BUCKET ID: BKT-FOREX-EVIDENCE-CLI-001
BUCKET NAME: Evidence Intake Accessibility
PACKET ID: PKT-FOREX-FIRST-DOLLAR-COUNTDOWN-CLI-EVIDENCE-V1
PACKET NAME: Route First Dollar Evidence Through Countdown CLI

ALLOWED PATHS:
- automation/orchestration/aios_work_countdown_v1.py
- tests/orchestration/test_aios_work_countdown_v1.py
- automation/orchestration/work_packets/complete/PKT-FOREX-FIRST-DOLLAR-COUNTDOWN-CLI-EVIDENCE-V1.md

FORBIDDEN PATHS:
- AGENTS.md
- RISK_POLICY.md
- .github/
- secrets/
- credentials/
- .env
- broker/
- live_trading/
- every path not listed in ALLOWED PATHS

APPROVAL AUTHORITY: Anthony explicitly requested one repository-local workflow, one commit, and one PR. Merge, broker access, credential access, live execution, orders, and money movement remain blocked.

VALIDATOR CHAIN:
- python -m pytest tests/orchestration/test_aios_work_countdown_v1.py tests/forex_engine/test_first_withdrawable_dollar_v1.py -q
- python -m automation.orchestration.aios_work_countdown_v1 --help
- git diff --check
- git diff --cached

STOP POINT: Stop after exactly one commit and exactly one PR. Do not merge. Do not access a broker, credentials, live trading, orders, or money movement.

MISSION: Expose the existing First Withdrawable Dollar evidence projection through the repository's countdown command so locally available canonical receipts can drive the workflow without requiring GitHub access.

PREFLIGHT:
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- classify the observed clean branch and missing remote without inventing state

APPLY STEPS:
1. Add one explicit JSON command-line input for First Withdrawable Dollar evidence.
2. Route parsed evidence to the existing fail-closed projection.
3. Add focused command-line coverage proving hours and the next blocker become visible.
4. Run the validator chain.
5. Review and stage only the three allowed files.
6. Commit once with message `feat(forex): expose first-dollar evidence in countdown CLI`.
7. Create one PR and stop before merge.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
