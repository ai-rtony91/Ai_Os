# AIOS Forex Full Overnight Work Runner Owner Handoff V1

## How To Run The Runner
- `pwsh -File scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1 -DryRun -NoPublish -MaxCycles 12 -MaxMinutes 480`
- `pwsh -File scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1 -MaxCycles 12 -MaxMinutes 480`

## Safe Files
- automation/forex_engine/forex_full_overnight_work_runner_v1.py
- scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py
- scripts/forex_delivery/validate_forex_full_overnight_work_runner_v1.ps1
- scripts/forex_delivery/publish_forex_full_overnight_work_runner_v1.ps1
- scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1
- docs/governance/programs/contracts/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1_REPORT.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_ACTION_QUEUE_V1.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_CHECKPOINT_V1.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_ACTIVE_PACKET_QUEUE_V1.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_EXTERNAL_GATE_STOP_V1.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_OWNER_HANDOFF_V1.md
- Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_CODEX_PROMPT_V1.md
- tests/forex_engine/test_forex_full_overnight_work_runner_v1.py

## Blocked Files
- files outside active allowed scope
- broker or credential artifacts
- any .env or key-like file
- non-approved order/execution artifacts

## What To Paste Back On Stop
- runner output markers and latest checkpoint path
- path classification summary (if action returned STOP_DIRTY_SCOPE)
- selected packet identifier and next required flow
- selected next prompt file content

## External Gates
- If external gate returns immediately, resolve by opening the mapped gate packet.

## Final Owner Sentence
AIOS Forex full overnight work runner is established locally: it gathers the landed flow 1 and overnight contract anchors, reads the active packet queue, classifies untracked files against active allowed paths, validates and publishes repo-safe packets when permitted, writes checkpoints and next Codex prompts, and continues toward Flow 2 evidence capture, Flow 3 profit-loop gating, and live exception bridging, while broker/API access, credentials, order submission, live trading, autonomous operation, and money movement remain separately gated.