🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: DRAFT_ONLY_DO_NOT_EXECUTE

TITLE
Phase 17 Draft Packet - Repo Status Validator Recommendation

LANE
DRY_RUN validation lane

WORKTREE
C:\Dev\Ai.Os

BRANCH
main

MISSION
Inspect repo status and propose the next validation step without APPLY.

PRECHECK
1. Run `git status --short --branch`.
2. Confirm branch is `main`.
3. Confirm working tree is clean.

ALLOWED PATHS
- `docs/AI_OS/execution_pipeline/`
- `automation/orchestration/execution_pipeline/`
- `schemas/aios/execution_pipeline/`

FORBIDDEN PATHS
- `telemetry/`
- `control/`
- `automation/orchestration/locks/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/memory/`
- `automation/orchestration/night_supervisor/`
- broker/OANDA/live trading files
- secret files
- `.env` files

HARD BLOCKS
- No APPLY.
- No commit.
- No push.
- No merge.
- No API key.
- No network/OpenAI call.
- No package install.
- No broker/OANDA/live trading.

VALIDATION CHAIN
- git clean-state check
- forbidden-path check
- no-secret check
- no-network check
- no-trading check
- final git status

STOP POINT
Stop after recommending the next validator.

FINAL REPORT
Report precheck, validator recommendation, forbidden paths touched, protected actions performed, and final git status.
