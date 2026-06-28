# AIOS Forex Full Overnight Work Runner V1

## Purpose
Run repository-safe continuation across Flow 2 evidence, Flow 3 profit-loop gate work, and live exception bridge preparation.

## Current Anchors
- PR_1194_FLOW1_MERGED
- PR_1196_OVERNIGHT_END_TO_END_CONTRACT

## What This Runner Does
- inspect repo state for allowed file scope
- select and queue next safe packet work
- write validation, publish, and checkpoint artifacts
- detect external gates and stop for owner action

## What This Runner Does Not Do
- broker/API calls
- credential loading
- order placement
- money movement
- runtime activation
- production or live execution

## Untracked File Policy
Allowed untracked files are only in active packet scope. All other untracked files must be treated as disallowed worktree scope.

## Active Packet Queue
1) Flow 2 packet
2) Flow 3 packet
3) Live exception gate packet

## External Gate Stop Conditions
Owner, credential, broker, evidence, and capital gates stop host continuation.

## Host Runner Script
scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1

## Validation And Publish Flow
Run validator first, then publish, then merge only after checks pass.

## Owner Overnight Procedure
Run the host script in DryRun first, then run full cycle execution on clean state.

## Final Owner Sentence
AIOS Forex full overnight work runner is established locally: it gathers the landed flow 1 and overnight contract anchors, reads the active packet queue, classifies untracked files against active allowed paths, validates and publishes repo-safe packets when permitted, writes checkpoints and next Codex prompts, and continues toward Flow 2 evidence capture, Flow 3 profit-loop gating, and live exception bridging, while broker/API access, credentials, order submission, live trading, autonomous operation, and money movement remain separately gated.