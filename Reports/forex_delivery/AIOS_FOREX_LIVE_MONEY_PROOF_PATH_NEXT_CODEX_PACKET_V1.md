CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_LIVE_MONEY_PROOF_PATH_NEXT_CODEX_PACKET_V1

MISSION
Run sanitized evidence intake and rerun the supervised autonomy governor for live-micro proof progression toward `LIVE_MICRO_EXCEPTION_REVIEW_READY`.

PRECHECK
Set-Location C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

REQUIRED
- branch is main
- worktree clean
- HEAD at or after f91cab92
- PR #1203 landed

READ
Reports/forex_delivery/AIOS_FOREX_LIVE_MONEY_PROOF_PATH_PREP_V1.md
Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json
automation/forex_engine/supervised_autonomy_governor_v1.py

OBJECTIVE
1. Update only sanitized evidence inputs in
   `Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json` with real, non-credential, repo-safe evidence.
2. Run:
   `python scripts/forex_delivery/run_supervised_autonomy_governor_v1.py --input-json Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json`.
3. Capture governor output and if status is `LIVE_MICRO_EXCEPTION_REVIEW_READY`, route to owner review card capture next.

SAFETY CONSTRAINTS
- Do not place orders.
- Do not use broker API.
- Do not read `.env`.
- Do not persist credentials or account identifiers.
- Do not authorize live trading.

STOP POINT
Stop after validator outputs and governor result; do not place orders.

VALIDATORS
python -m json.tool Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json
git diff --check -- Reports/forex_delivery/AIOS_FOREX_LIVE_MONEY_PROOF_PATH_PREP_V1.md Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_OWNER_APPROVAL_CARD_V1.md Reports/forex_delivery/AIOS_FOREX_LIVE_MONEY_PROOF_PATH_NEXT_CODEX_PACKET_V1.md
