CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_CODEX_APPLY_PACKET
SUPERVISOR IDENTITY: Anthony Human Owner
WORKER IDENTITY: EAST_OCC_01
MODE: APPLY
ZONE: EAST
LANE: forex-first-dollar-evidence-file
OBSERVED WORKTREE: /workspace/Ai_Os
OBSERVED BRANCH: work

MISSION ID: MISSION-AIOS-001
MISSION NAME: First Withdrawable Dollar
PROGRAM ID: PRG-FOREX-001
PROGRAM NAME: Governed Forex Profit Path
EPIC ID: EPC-FOREX-COUNTDOWN-001
EPIC NAME: Repository-Proven Profit Countdown
BUCKET ID: BKT-FOREX-EVIDENCE-INTAKE-002
BUCKET NAME: Local Evidence Intake
PACKET ID: PKT-FOREX-FIRST-DOLLAR-EVIDENCE-FILE-V1
PACKET NAME: Load First Dollar Evidence From File

ALLOWED PATHS:
- automation/orchestration/aios_work_countdown_v1.py
- tests/orchestration/test_aios_work_countdown_v1.py
- automation/orchestration/work_packets/complete/PKT-FOREX-FIRST-DOLLAR-EVIDENCE-FILE-V1.md

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

APPROVAL AUTHORITY: Anthony explicitly authorized generation and immediate execution of one repository-proven workflow with one commit and one PR. Merge, broker access, credential access, live execution, orders, and money movement remain blocked.

VALIDATOR CHAIN:
- python -m pytest tests/orchestration/test_aios_work_countdown_v1.py tests/forex_engine/test_first_withdrawable_dollar_v1.py -q
- python -m automation.orchestration.aios_work_countdown_v1 --help
- git diff --check
- git diff --cached --check
- git diff --cached

EXACT COMMIT MESSAGE: feat(forex): load first-dollar evidence from file

EXACT STOP POINT: Stop after exactly one commit and exactly one PR. Do not merge. Do not access a broker, credentials, live trading, orders, or money movement.

MISSION: Let the repository-proven read-only work countdown load a sanitized local First Withdrawable Dollar execution-receipt evidence file, avoiding fragile shell-embedded JSON while preserving the existing fail-closed profit-stage projection.

PREFLIGHT:
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- confirm the observed worktree is /workspace/Ai_Os, the observed branch is work, and the tree is clean

APPLY STEPS:
1. Add one path-based command-line input for First Withdrawable Dollar evidence.
2. Reject simultaneous inline and file evidence inputs.
3. Route parsed file evidence through the existing read-only projection.
4. Add focused tests for file intake and mutual exclusion.
5. Run the validator chain.
6. Review and stage only the three allowed files.
7. Commit once with the exact commit message.
8. Create exactly one PR and stop before merge.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
COMMIT STATUS:
PUSH STATUS:
PR STATUS:
SAFE NEXT COMMAND:
STATUS: COMPLETE, COMMITTED, PR CREATED, NO MERGE
