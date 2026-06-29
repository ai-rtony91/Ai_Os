CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

## IDENTITY MARKER
Project: AI_OS
Repository: ai-rtony91/Ai_Os
Worktree: C:\\Dev\\Ai.Os
Supervisor identity: ChatGPT planning supervisor
Worker identity: Codex Forex autonomy finisher worker
Packet ID: AIOS_FOREX_AUTONOMY_FINISHER_V4
Mode: APPLY_VALIDATE_PR_MERGE_CONTINUOUS_MANAGER
Zone: FOREX_AUTONOMOUS_CAMPAIGN_MANAGER
Lane: Forex / autonomy finisher / overnight continuous execution

## ALLOWED PATHS
- scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1
- automation/forex_engine/forex_autonomous_campaign_manager_v1.py
- tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py
- Reports/forex_delivery/AIOS_FOREX_AUTONOMY_FINISHER_V4_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_RUNBOOK.md
- Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json
- Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md
- Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md
- automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py
- tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py
- Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_CAMPAIGN_MASTER_V2_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_PACKET_QUEUE_V2.md
- Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_1_V2.md
- Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_2_V2.md
- Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md

## FORBIDDEN PATHS
- AGENTS.md\n- README.md\n- WHITEPAPER.md\n- RISK_POLICY.md\n- docs/architecture/AI_OS_WHITEPAPER.md\n- .env\n- .env.*\n- *.key\n- *.pem\n- *.p12\n- *.pfx\n- secrets/*\n- credentials/*\n- services/*\n- apps/*\n- telemetry/*\n- any broker credential file\n- any broker API client\n- any live order file\n- any scheduler install file\n- any daemon install file\n- any webhook file\n- any file outside ALLOWED PATHS

## APPROVAL AUTHORITY
- preserve current Flow 2 files\n- stage-safe edits only\n- run required validators\n- no broker/API, credentials, order execution, live trading, money movement\n- no scheduler/daemon/webhook changes\n

## VALIDATOR CHAIN
python -m py_compile automation/forex_engine/forex_autonomous_campaign_manager_v1.py | python -m pytest tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py -q | python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py | python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q

## STOP POINT
Stop when status is CAMPAIGN_COMPLETE or CAMPAIGN_BLOCKED.

## MISSION
AIOS Forex autonomy finisher continuation

## CURRENT STATE
campaign_id: AIOS_FOREX_AUTONOMY_FINISHER_V4
current_branch: lane/forex-flow2-supervised-demo-evidence-countdown-capture-v1
head: 4218f673
dirty_files: ['Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_1_V2.md', 'Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_2_V2.md', 'Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md', 'Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_CAMPAIGN_MASTER_V2_REPORT.md', 'Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_PACKET_QUEUE_V2.md', 'Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md', 'Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md', 'Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_RUNBOOK.md', 'Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json', 'Reports/forex_delivery/AIOS_FOREX_AUTONOMY_FINISHER_V4_REPORT.md', 'Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md', 'automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py', 'automation/forex_engine/forex_autonomous_campaign_manager_v1.py', 'scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1', 'tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py', 'tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py']
completed_stage_ids: []
active_stage_id: FLOW2_EVIDENCE_COUNTDOWN_LANDING
selected_stage_id: FLOW2_EVIDENCE_COUNTDOWN_LANDING
next_action: RUN_SELECTED_STAGE

## TASK
Run the next validator and follow repository-safe steps for stage FLOW2_EVIDENCE_COUNTDOWN_LANDING.

## FINAL REPORT FORMAT
AUTONOMY_FINISHER_STATUS:
STAGE_A_FLOW2_PRESERVATION:
STAGE_B_CAMPAIGN_MANAGER:
FILES_CREATED:
FILES_CHANGED:
VALIDATORS_RUN:
VALIDATORS_PASSED:
VALIDATORS_FAILED:
PR_CREATED:
PR_MERGED:
CURRENT_BRANCH:
CURRENT_HEAD:
FINAL_GIT_STATUS:
SAFETY_BOUNDARY:
BROKER_API_ACCESS:
CREDENTIALS_USED:
ORDER_EXECUTION:
LIVE_TRADING:
MONEY_MOVEMENT:
SCHEDULERS_DAEMONS_WEBHOOKS:
NEXT_SAFE_ACTION:
STOP_REASON:
