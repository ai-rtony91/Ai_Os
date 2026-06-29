# AIOS_FOREX_AUTONOMY_FINISHER_V4

## Objective
Create a repo-safe overnight automation manager that can pick the next acceptable
Forex autonomy stage, emit the required next Codex prompt, emit checkpoint/state,
preserve current Flow 2 files, and provide restart guidance.

## Files Created
- `automation/forex_engine/forex_autonomous_campaign_manager_v1.py`
- `scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1`
- `tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_AUTONOMY_FINISHER_V4_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_RUNBOOK.md`
- `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json`
- `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md`
- `Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md`

## Files Changed
- `automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py` (preserved)
- `tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py` (preserved)
- `Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_COUNTDOWN_CAPTURE_V1_REPORT.md` (preserved)
- `Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_CAMPAIGN_MASTER_V2_REPORT.md` (preserved)
- `Reports/forex_delivery/AIOS_FOREX_75_TO_100_OVERNIGHT_PACKET_QUEUE_V2.md` (preserved)
- `Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_1_V2.md` (preserved)
- `Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_2_V2.md` (preserved)
- `Reports/forex_delivery/AIOS_FOREX_75_TO_100_NEXT_CODEX_PACKET_3_V2.md` (preserved)

## Autonomy Added
- deterministic stage model with immutable stage/state/decision objects
- automatic unknown-dirty-file blocking and hard-blocker handling
- checkpoint and next-codex prompt generation
- machine-readable state JSON with generated safe run metadata
- PowerShell entrypoint for repeated overnight cycles

## How It Prevents Stop/Start Bottlenecks
- explicit stage selection keeps one chosen next action instead of ambiguous manual prompts
- manager output includes exact `NEXT_ACTION`, `SELECTED_STAGE`, and artifact paths
- checkpoint and prompt files allow safe resume after operator handoff
- all critical decisions are written through one stable schema and report format

## Remaining Human Gates
- owner review for PR merge
- production/overnight campaign policy exceptions if any live-broker milestone is attempted
- broker capability gates are out of this packet’s control

## 24-Hour Run Strategy
- run manager in DryRun every 30 minutes for validation readiness
- execute normal mode during the 8-hour overnight window
- on blocker states, wait for explicit human approval and rerun only once corrected
- preserve and re-check scope before any optional branch operations

## Safety Boundary
No broker/API access, no credentials, no order execution, no live trading,
no money movement, no scheduler installation, no daemon installation,
and no webhook installation are used.

## Validation Commands
- `python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py`
- `python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q`
- `python -m py_compile automation/forex_engine/forex_autonomous_campaign_manager_v1.py`
- `python -m pytest tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py -q`
- `pwsh -File scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1 -DryRun -NoPublish -MaxCycles 3 -MaxMinutes 30`
- `git diff --check`
- `git status --short --branch`

## Validation Results
- `python -m py_compile automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py` -> PASS
- `python -m pytest tests/forex_engine/test_flow2_supervised_demo_evidence_countdown_capture_v1.py -q` -> PASS (8 passed)
- `python -m py_compile automation/forex_engine/forex_autonomous_campaign_manager_v1.py` -> PASS
- `python -m pytest tests/forex_engine/test_forex_autonomous_campaign_manager_v1.py -q` -> PASS (12 passed)
- `pwsh -File scripts/forex_delivery/Invoke-ForexAutonomousCampaignManager.V1.ps1 -DryRun -NoPublish -MaxCycles 3 -MaxMinutes 30` -> PASS
- `git diff --check -- ...` -> PASS (no whitespace/errors)
- `git status --short --branch` -> PASS

## Git Status
Current branch: `lane/forex-flow2-supervised-demo-evidence-countdown-capture-v1`
Working tree: untracked files only (all expected to packet scope)

## Commit Status
Commit attempt blocked by Git metadata write permission: `Unable to create '.git/index.lock': Permission denied`.

## Push Status
Not attempted (commit blocker).

## PR Status
Not attempted (commit blocker).

## Next Safe Action
Resolve Git metadata write blocker, rerun:
1) `git add` for allowed paths
2) `git commit` packet scope
3) validation + push + PR creation
4) run merge + branch sync steps from packet

## SAFETY Boundary
The packet remains repo-safe and does not interact with broker/API or trade execution.

## Broker/API Access
Not used.

## Credentials Used
Not used.

## Order Execution
Not used.

## Live Trading
Not used.

## Money Movement
Not used.

## Schedulers / Daemons / Webhooks
Not installed.
