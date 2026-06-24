# AIOS Forex OANDA Demo First Trade Runbook And Owner GO-NOGO V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-RUNBOOK-AND-OWNER-GO-NOGO-V1

Branch: feature/forex-oanda-demo-first-trade-runbook-go-nogo-v1

Mission outcome: created the governed first-trade GO/NOGO evaluator, JSON/checklist runbook script, and tests for the first protected OANDA demo one-order attempt path.

## Why This Is The First-Trade Runbook Layer

This packet sits after the owner command, broker-call readiness, post-trade evidence capture, and result-to-bucket layers.

It gives Anthony a final human-facing decision surface before any manual OANDA demo one-order attempt. The layer decides only whether the prerequisites are ready for Anthony to run the already-generated owner command one time.

## Why This PR Does Not Call OANDA Or Place Trades

This PR does not call OANDA, does not call a broker, does not place a demo or live order, does not read `.env`, does not read credentials, does not read account identifiers, and does not persist runtime material.

The script has no execute flag. It prints only JSON, checklist text, or a sanitized GO/NOGO template.

## Owner Command Dependency

The owner command result must have status `OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND`, must include `final_owner_command`, and must keep all execution authority fields false.

The runbook summarizes the command package but does not execute or reproduce the owner runtime command as a Codex action.

## Broker Call Readiness Dependency

The broker call readiness result must have status `BROKER_CALL_DRY_RUN_READY` or `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED`.

The attempted-once status `BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE` is treated as NOGO for this first-trade GO/NOGO surface because it belongs to evidence capture or already-attempted review, not a fresh first manual attempt.

The broker readiness payload must keep live order allowed false, autonomous order allowed false, all execution authority fields false, and must not contain token, account ID, credential, secret, password, or authorization keys.

## Result-To-Bucket Dependency

The result-to-bucket readiness result must have status `BUCKET_UPDATE_READY`.

Its recommendation must keep:

- next trade owner approval required true
- live allocation allowed false
- autonomous compounding allowed false

All execution authority fields must remain false.

## Runtime Readiness Requirements

The runtime context must prove:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo endpoint only
- live endpoint absent
- runtime token external
- runtime account ID external
- no credential persistence
- no account ID persistence
- one order only
- max order attempts `1`
- order not already attempted
- zero existing open orders
- zero existing pending orders
- kill switch ready
- daily stop ready
- max loss gate ready
- stop loss ready
- take profit ready
- pre-trade evidence ready
- post-trade evidence plan ready
- owner present for manual run

## Owner GO/NOGO Requirements

Anthony must confirm:

- GO/NOGO reviewed
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

## Pre-Run Checklist

- review PR landed and main synced
- confirm OANDA demo environment only and no live money
- confirm demo endpoint only and live endpoint absent
- confirm runtime token external and not persisted
- confirm runtime account ID external and not persisted
- confirm one order only, max one attempt, and no second order
- confirm order not already attempted
- confirm existing open orders zero
- confirm existing pending orders zero
- confirm stop loss ready and order value known
- confirm take profit ready and order value known
- confirm kill switch, daily stop, and max loss gates ready
- capture pre-trade evidence before manual command
- open owner command template only after GO
- do not rerun after one attempt

## Post-Run Evidence Checklist

- capture command exit status
- capture sanitized order reference
- capture fill or rejection status
- capture stop-loss and take-profit attachment status
- record realized or unrealized P/L
- record balance and NAV snapshot
- record UTC timestamp
- confirm no credentials or account IDs persisted
- confirm no second order attempted
- prepare post-trade evidence capture package
- prepare result-to-bucket update after evidence capture

## Kill Switch Plan

Before run: confirm the manual stop path and no-second-order rule before any owner command.

During run: if unexpected state appears, stop and do not retry.

After run: capture evidence, then stop before any next trade.

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
- zero existing open orders
- zero existing pending orders
- live order allowed false
- autonomous order allowed false

## GO/NOGO Semantics

`GO` means all five gates passed and Anthony may run the first OANDA demo order command once.

`NOGO` means one or more blockers exist and the next safe action is to repair the blocker before any owner manual demo attempt.

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

This runbook does not grant Codex, automation, schedulers, daemons, webhooks, or autonomous systems authority to place orders.

## Validation Results

Phase 1 main readiness was manually validated by the owner after Codex sandbox launch failure:

- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS by owner-run PowerShell validation
- `git diff --check`: PASS by owner-run PowerShell validation
- `git status --short --branch`: main synced with only untracked `docs/legal/`

Lane validation after implementation:

- `python -m py_compile automation/forex_engine/oanda_demo_first_trade_runbook_go_nogo_v1.py tests/forex_engine/test_oanda_demo_first_trade_runbook_go_nogo_v1.py scripts/forex_delivery/run_oanda_demo_first_trade_runbook_go_nogo_v1.py`: pending final lane validation
- `python -m pytest tests/forex_engine/test_oanda_demo_first_trade_runbook_go_nogo_v1.py -q`: pending final lane validation
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: pending final lane validation
- `git diff --check`: pending final lane validation

## Git Status

Branch `feature/forex-oanda-demo-first-trade-runbook-go-nogo-v1` with four scoped runbook files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

Prepare:

`AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-OWNER-MANUAL-EXECUTION-WINDOW-V1`

Anthony may then review the GO/NOGO package and, only if GO remains true, run the owner manual demo order command once. Codex must not run the broker command.
