CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER: AI_OS_CODEX_APPLY_PACKET
SUPERVISOR IDENTITY: Anthony Human Owner
MODE: APPLY
ZONE: EAST
WORKER IDENTITY: EAST_OCC_01
LANE: forex-first-dollar-evidence-file-intake
WORKTREE: /workspace/Ai_Os
BRANCH: work, observed by preflight

MISSION ID: MISSION-AIOS-001
MISSION NAME: First Withdrawable Dollar
PROGRAM ID: PRG-FOREX-001
PROGRAM NAME: Governed Forex Profit Path
EPIC ID: EPC-FOREX-COUNTDOWN-001
EPIC NAME: Repository-Proven Profit Countdown
BUCKET ID: BKT-FOREX-EVIDENCE-CLI-002
BUCKET NAME: Durable Evidence Intake
PACKET ID: PKT-FOREX-FIRST-DOLLAR-EVIDENCE-FILE-INTAKE-V1
PACKET NAME: Add Durable First Dollar Evidence File Intake

ALLOWED PATHS:
- automation/orchestration/aios_work_countdown_v1.py
- tests/orchestration/test_aios_work_countdown_v1.py
- automation/orchestration/work_packets/complete/PKT-FOREX-FIRST-DOLLAR-EVIDENCE-FILE-INTAKE-V1.md

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

APPROVAL AUTHORITY: Anthony requested exactly one repository-proven workflow, one commit, and one PR. Merge, broker access, credentials, live execution, orders, and money movement remain blocked.

VALIDATOR CHAIN:
- python -m pytest tests/orchestration/test_aios_work_countdown_v1.py tests/forex_engine/test_first_withdrawable_dollar_v1.py -q
- python -m automation.orchestration.aios_work_countdown_v1 --help
- git diff --check
- git diff --cached

STOP POINT: Stop after exactly one commit and exactly one PR. Do not merge or perform financial actions.

MISSION: Make the existing countdown workflow consume a durable repository-local First Withdrawable Dollar evidence JSON file without shell escaping or custom Python, while rejecting non-object evidence before projection.

PREFLIGHT:
- pwd
- git status --short --branch
- git branch --show-current
- git remote -v
- preserve the observed clean branch and report unavailable remote evidence

APPLY STEPS:
1. Add a mutually exclusive evidence-file input beside the existing inline JSON input.
2. Read the file as UTF-8 JSON.
3. Reject non-object evidence at the command boundary.
4. Add focused file-intake and invalid-shape tests.
5. Run validators and review the exact three-file diff.
6. Commit once with message `fix(forex): accept durable first-dollar evidence files`.
7. Create one PR and stop before merge.

FINAL REPORT FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
