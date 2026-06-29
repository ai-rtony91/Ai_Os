CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

CONTRACT TITLE
AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_NEXT_CODEX_PACKET_V1

MISSION
Route the next controlled packet after running the governor rerun and bucket policy controller.

REQUIRED STATE SNAPSHOT
- candidate_status: REQUIRE_MORE_EVIDENCE
- bucket_status: BUCKET_MAX_LOSS_HOLD
- next_autonomy_action: COLLECT_MORE_EVIDENCE

NEXT STATE TARGET
REQUIRE_MORE_EVIDENCE

NEXT EXECUTION ACTION
Run sanitized evidence intake update packet to collect and normalize missing evidence, then rerun this governor controller.

TARGET_PACKET
Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_NEXT_CODEX_PACKET_V1.md

SAFETY BOUNDARY
- Do not place trades.
- Do not use broker API.
- Do not read .env.
- Do not use credentials.
- Do not persist account identifiers.
- Do not authorize live trading.

OUTPUT EXPECTATION
This packet must emit a controller-safe evidence update summary only.
