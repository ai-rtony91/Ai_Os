# AIOS Forex OANDA Demo First Trade Owner Manual Execution Window V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-OWNER-MANUAL-EXECUTION-WINDOW-V1

Branch: feature/forex-oanda-demo-first-trade-owner-manual-execution-window-v1

Mission outcome: created the governed first-trade owner manual execution-window evaluator, script, and tests for the first protected OANDA demo one-order attempt path.

## Why This Is The First-Trade Execution-Window Layer

This packet sits after the first-trade GO/NOGO runbook. It narrows a GO result into a bounded owner manual execution window with final timing, owner-presence, runtime-only value handling, one-order cap, kill switch, and evidence-path checks.

The layer does not execute the order. It tells Anthony whether the final manual window package is ready.

## Why This PR Does Not Call OANDA Or Place Trades

This PR does not call OANDA, does not call a broker, does not place a demo or live order, does not read `.env`, does not read credentials, does not read account identifiers, and does not persist runtime material.

The script has no execute flag. It prints JSON, checklist text, window text, or a sanitized owner command reminder with placeholders only.

## GO/NOGO Dependency

The GO/NOGO result must have:

- status `RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT`
- `go_nogo` set to `GO`
- next safe action `owner_may_run_first_demo_order_command_once`
- all execution authority fields false

## Owner Command Dependency

The owner command result must have status `OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND`, must include `final_owner_command`, and must keep all execution authority fields false.

The owner command result must not contain token, account ID, credential, secret, password, or authorization keys anywhere recursively. Runtime values remain outside the repo and outside Codex.

## Execution Window Context Requirements

The execution window context must prove:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo endpoint only
- live endpoint absent
- runtime token external
- runtime account ID external
- runtime credentials available to owner
- no credential persistence
- no account ID persistence
- one order only
- max order attempts `1`
- order not already attempted
- zero existing open orders
- zero existing pending orders
- owner present for manual run
- kill switch ready
- daily stop ready
- max loss gate ready
- stop loss ready
- take profit ready
- pre-trade evidence ready
- post-trade evidence plan ready
- execution window minutes numeric, greater than zero, and no more than sixty
- market open or owner override true

## Owner Confirmation Requirements

Anthony must confirm:

- execution window reviewed
- demo only
- no live money
- one order only
- max one attempt
- stop loss
- take profit
- loss possible
- no profit guarantee
- no second order
- manual run only
- post-trade evidence required
- kill switch ready
- runtime credentials external

## Execution Window Semantics

`WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION` means the final owner manual execution window is ready and Anthony may execute one OANDA demo order inside the approved window.

Any blocker means the next safe action is to repair the blocker before the execution window.

## Final Pre-Execution Checklist

- confirm GO/NOGO still GO
- confirm owner command package ready
- confirm runtime values are owner supplied only
- confirm demo endpoint only and no live money
- confirm execution window time limit
- confirm market open or owner override
- confirm owner present for manual run
- confirm one order only and max one attempt
- confirm no second order
- confirm existing open orders zero
- confirm existing pending orders zero
- confirm stop loss ready
- confirm take profit ready
- confirm kill switch, daily stop, and max loss gates ready
- capture pre-trade evidence before owner command

## Final Post-Execution Evidence Path

- capture command exit status
- capture sanitized order reference
- capture fill or rejection status
- capture SL/TP attachment status
- record realized or unrealized P/L
- record balance and NAV snapshot
- record UTC timestamp
- confirm no credentials or account IDs persisted
- confirm no second order attempted
- feed post-trade evidence capture layer
- feed result-to-bucket layer after evidence capture

## One-Order Cap

The execution-window evaluator requires one order only, max order attempts `1`, order already attempted false, zero existing open orders, and zero existing pending orders.

The package output keeps `actual_order_requires_owner_manual_command` true and does not grant Codex any authority to run the command.

## Kill Switch Plan

Before run: confirm kill switch, daily stop, max loss gate, stop loss, and take profit.

During run: if any unexpected state appears, stop and do not retry.

After run: capture sanitized evidence and stop before any next trade.

## Risk Controls

- demo only
- no live money
- one order only
- max one attempt
- no second order
- stop loss required
- take profit required
- loss possible
- no profit guarantee
- owner present
- runtime credentials external
- live order allowed false
- autonomous order allowed false

## Runtime Credential Placeholder Rule

Runtime OANDA demo values must be supplied by Anthony outside the repo during the owner manual command window. The evaluator and script do not read, store, print, or persist real runtime values.

## No Live Endpoint Rule

The execution window requires demo endpoint only and live endpoint absent. Live trading remains blocked.

## Execution Authority False

All execution authority fields remain false:

- execution_allowed
- demo_order_allowed
- live_order_allowed
- broker_write_allowed
- autonomous_order_allowed
- scheduler_allowed
- daemon_allowed
- webhook_allowed

This execution-window package does not grant Codex, automation, schedulers, daemons, webhooks, or autonomous systems authority to place orders.

## Validation Results

Phase 1 main readiness was manually validated by the owner after Codex sandbox launch failure:

- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS by owner-run PowerShell validation
- `git diff --check`: PASS by owner-run PowerShell validation
- `git status --short --branch`: main synced with only untracked `docs/legal/`
- `git log -1 --oneline`: `294074c9 feat(forex): add OANDA demo first trade go-nogo runbook (#1063)`

Lane validation after implementation:

- `python -m py_compile automation/forex_engine/oanda_demo_first_trade_owner_manual_execution_window_v1.py tests/forex_engine/test_oanda_demo_first_trade_owner_manual_execution_window_v1.py scripts/forex_delivery/run_oanda_demo_first_trade_owner_manual_execution_window_v1.py`: pending final lane validation
- `python -m pytest tests/forex_engine/test_oanda_demo_first_trade_owner_manual_execution_window_v1.py -q`: pending final lane validation
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: pending final lane validation
- `git diff --check`: pending final lane validation

## Git Status

Branch `feature/forex-oanda-demo-first-trade-owner-manual-execution-window-v1` with four scoped execution-window files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

Prepare:

`AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-ACTUAL-OWNER-COMMAND-RUN`

Anthony may then review the execution-window package and, only if the window remains ready, manually execute one demo order command inside the approved window. Codex must not run the broker command.
