🧩 CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN: DRAFT_ONLY_DO_NOT_EXECUTE

TITLE
AI_OS Phase 16 Pipeline Draft - Repo Status Validator Packet

LANE
DRY_RUN validation lane

WORKTREE
C:\Dev\Ai.Os

BRANCH
main

MISSION
Check repo status, propose the next validator, and stop before APPLY.

DRAFT_ONLY
NO_APPLY_AUTHORITY
NO_COMMIT
NO_PUSH
NO_MERGE
NO_LIVE_API_CALL

PRECHECK
1. Run git status --short --branch.
2. Confirm branch is main.
3. Confirm working tree is clean.

ALLOWED PATHS
- docs/AI_OS/openai_api_bridge/
- automation/orchestration/openai_api_bridge/

FORBIDDEN PATHS
- telemetry/
- control/
- automation/orchestration/locks/
- automation/orchestration/approval_inbox/
- automation/orchestration/memory/
- automation/orchestration/night_supervisor/
- broker files
- OANDA files
- live trading files
- secret files
- .env files

HARD BLOCKS
- Do not use API keys.
- Do not call OpenAI.
- Do not install packages.
- Do not make network calls.
- Do not APPLY.
- Do not commit.
- Do not push.
- Do not merge.

VALIDATION CHAIN
- git_clean_state
- allowed_paths
- blocked_paths
- validate_only_runner
- json_integrity
- no_secrets
- no_network
- no_live_trading_enablement
- final_git_status

STOP POINT
Stop after reporting validator recommendation. Do not APPLY.

FINAL REPORT FORMAT
AI_OS DRAFT PACKET RESULT
1. Precheck: PASS/FAIL
2. Validator recommendation: [text]
3. Forbidden paths touched: YES/NO
4. Commit/push/merge performed: YES/NO
5. Final git status: [exact output]
