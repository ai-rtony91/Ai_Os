# AI_OS Dispatch Blocker Classes

Blocker classes describe why a packet cannot proceed or why it must remain preview-only.

## Registry

- `DIRTY_TREE`
- `WRONG_BRANCH`
- `WRONG_WORKTREE`
- `ACTIVE_LOCK`
- `NIGHT_SUPERVISOR_ACTIVE`
- `SECRET_RISK`
- `API_KEY_RISK`
- `ENV_FILE_RISK`
- `SERVICE_ACCOUNT_FILE_RISK`
- `NETWORK_RISK`
- `LIVE_OPENAI_CALL_RISK`
- `PROMPTFOO_EXECUTION_RISK`
- `COMPUTER_USE_ACTION_RISK`
- `SKILL_UNREVIEWED_RISK`
- `TOOL_SEARCH_OVERPERMISSION_RISK`
- `MCP_OVERPERMISSION_RISK`
- `LIVE_TRADING_RISK`
- `BROKER_RISK`
- `OANDA_RISK`
- `PI_MOTOR_RISK`
- `APPROVAL_MISSING`
- `VALIDATOR_MISSING`
- `FORBIDDEN_PATH_RISK`
- `PROFITABILITY_PRIORITY_VIOLATION`
- `PROMPT_INJECTION_RISK`
- `RED_TEAM_REQUIRED`
- `UNKNOWN_RISK`

## Blocking Rules

Any secret, API key, `.env`, service account, live trading, broker, OANDA, Pi motor, profitability-priority violation, missing validator, or unknown high-risk blocker routes to `BLOCKED`.

Any Night Supervisor runtime start, OpenAI live call, Promptfoo run, computer-use click/type/submit/delete action, or unreviewed Skill execution requires separate human approval and remains pending approval or blocked.

