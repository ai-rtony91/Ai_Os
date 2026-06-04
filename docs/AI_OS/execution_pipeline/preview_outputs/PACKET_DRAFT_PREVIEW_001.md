🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: DRAFT_ONLY_DO_NOT_EXECUTE

TITLE
Phase 17 Draft Packet - Inspect Repo Status

LANE
DRY_RUN validation lane

WORKTREE
C:\Dev\Ai.Os

BRANCH
main

MISSION
Inspect repo status and propose the next validation step without APPLY.

PRECHECK
Run git status --short --branch and confirm clean main.

ALLOWED PATHS
- docs/AI_OS/execution_pipeline/
- automation/orchestration/execution_pipeline/
- schemas/aios/execution_pipeline/

FORBIDDEN PATHS
- telemetry/
- control/
- automation/orchestration/locks/
- automation/orchestration/approval_inbox/
- automation/orchestration/memory/
- automation/orchestration/night_supervisor/
- broker/OANDA/live trading files
- secret files
- .env files

HARD BLOCKS
No APPLY, commit, push, merge, API keys, network, package install, broker, OANDA, or live trading.

VALIDATION CHAIN
git_clean_state -> forbidden_path_check -> no_secret_check -> no_network_check -> trading_safety_check -> final_git_status

STOP POINT
Stop after validator recommendation.

FINAL REPORT
Report precheck, validator recommendation, protected actions, and final git status.
