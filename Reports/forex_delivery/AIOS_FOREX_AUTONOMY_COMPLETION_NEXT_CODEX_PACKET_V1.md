CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1

MISSION
Rerun supervised autonomy governance against the latest sanitized evidence and update bucket policy artifacts for the next bounded completion cycle.

TARGET_ID
AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1

PRECHECK
Set-Location C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git log -1 --oneline

READ
Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_STATE_MODEL_V1.json
Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json
Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_MASTER_ORCHESTRATOR_V1.md
Reports/forex_delivery/AIOS_FOREX_DAILY_WEEKLY_HOURLY_PROFIT_CYCLE_V1.md
automation/forex_engine/supervised_autonomy_governor_v1.py

SAFE READING RULE
- Use only sanitized numeric and enum evidence values.
- Do not introduce credentials, account identifiers, secrets, or raw broker artifacts.

OBJECTIVE
1. Consume the completion state model.
2. Consume and update only sanitized evidence fields in
   `Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json`.
3. Run governor evaluation with sanitized input.
4. Classify next state as one of:
   - REQUIRE_MORE_EVIDENCE
   - DEMO_SUPERVISED_READY
   - LIVE_MICRO_EXCEPTION_REVIEW_READY
   - blocked
5. Update required bucket/policy notes for the next safe state.
6. Emit a follow-up packet in the same lane with the next safe action.

CLASSIFICATION OUTPUT FORMAT
- candidate_status
- governor_blockers
- next_safe_action
- state_classification (one of the four required values)
- next_packet_path

SAFETY BOUNDARY
- Do not place orders.
- Do not use broker API.
- Do not read .env.
- Do not persist credentials.
- Do not call owner authorization actions directly.
- Do not start schedulers, daemons, or webhooks.
- Do not start loops.

STOP CONDITION
- Stop after governor output and generated next-packet recommendation.
- Do not authorize execution.

VALIDATORS (within this packet execution)
- Python JSON check on the governor input template.
- Diff-check for touched report evidence files only.
