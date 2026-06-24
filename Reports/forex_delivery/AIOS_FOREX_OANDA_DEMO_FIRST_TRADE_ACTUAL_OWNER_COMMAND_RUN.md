# AIOS Forex OANDA Demo First Trade Actual Owner Command Run

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-FIRST-TRADE-ACTUAL-OWNER-COMMAND-RUN

Branch: feature/forex-oanda-demo-first-trade-actual-owner-command-run

Mission outcome: created the governed actual owner-command run evaluator, command package script, and tests for the first protected OANDA demo one-order attempt path.

## Why This Is The Actual Owner-Command Run Package

This packet sits after the execution-window layer. It packages the final manual command Anthony may run later if all gates remain true.

The package is a command generator and final safety-interlock evaluator only. It does not execute the command, does not inject transport, and does not call OANDA from Codex.

## Why This PR Does Not Call OANDA Or Place Trades

This PR does not call OANDA, does not call a broker, does not place a demo or live order, does not read `.env`, does not read credentials, does not read account identifiers, and does not persist runtime material.

The script has no execute flag. It prints JSON, a placeholder-only owner command, or a final warning and evidence checklist.

## Execution Window Dependency

The execution window result must have:

- status `WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION`
- `execution_window_package.ready` true
- one order only true
- max order attempts `1`
- actual order requires owner manual command true
- all execution authority fields false

## Owner Command Dependency

The owner command result must have status `OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND`, must include `final_owner_command`, and must keep all execution authority fields false.

The input owner command result must not contain token, account ID, credential, secret, password, or authorization keys anywhere recursively. Runtime values remain outside the repo and outside Codex.

## Broker-Call Dependency

The broker-call readiness result must have status `BROKER_CALL_DRY_RUN_READY` or `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED`.

It must prove broker network call false, order placement false, all execution authority fields false, and no token, account ID, credential, secret, password, or authorization keys anywhere recursively.

## Runtime Context Requirements

The actual run context must prove:

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
- execution window open
- market open or owner override true

## Owner Final Confirmation Requirements

Anthony must confirm:

- actual command reviewed
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
- ready to press the manual demo button

## Exact Command Template Behavior

The printed command template references:

`scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py`

It includes placeholders for:

- `OANDA_DEMO_ACCESS_TOKEN`
- `OANDA_DEMO_ACCOUNT_ID`
- `INSTRUMENT`
- `DIRECTION`
- `UNITS`
- `STOP_LOSS`
- `TAKE_PROFIT`
- `RISK_AMOUNT`
- `CLIENT_ORDER_ID`

It includes the required confirmation flags:

- `--execute-demo-order`
- `--i-approve-actual-oanda-demo-broker-call`
- `--i-understand-demo-only`
- `--i-understand-one-order-only`
- `--i-understand-loss-possible`
- `--i-understand-no-profit-guarantee`
- `--i-confirm-stop-loss`
- `--i-confirm-take-profit`
- `--i-confirm-no-second-order`
- `--i-confirm-post-trade-evidence`

## Final Warning Behavior

The final warning tells Anthony:

- run exactly one OANDA demo order attempt only if every gate remains ready
- do not use live money
- loss is possible
- profit is not guaranteed
- do not rerun after one attempt
- Codex must not execute the command or call OANDA

## One-Order Cap

The actual-run evaluator requires one order only, max order attempts `1`, order already attempted false, zero existing open orders, and zero existing pending orders.

The package output keeps `owner_must_run_manually` true and does not grant Codex any authority to run the command.

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

Runtime OANDA demo values must be supplied by Anthony outside the repo during the owner manual command. The evaluator and script do not read, store, print, or persist real runtime values.

## No Live Endpoint Rule

The actual owner-command package requires demo endpoint only and live endpoint absent. Live trading remains blocked.

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

This package does not grant Codex, automation, schedulers, daemons, webhooks, or autonomous systems authority to place orders.

## Validation Results

Phase 1 main readiness was manually validated by the owner after Codex sandbox launch failure:

- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS by owner-run PowerShell validation
- `git diff --check`: PASS by owner-run PowerShell validation
- `git status --short --branch`: main synced with only untracked `docs/legal/`
- `git log -1 --oneline`: `5bb874b6 feat(forex): add OANDA demo first trade execution window (#1064)`

Lane validation after implementation:

- `python -m py_compile automation/forex_engine/oanda_demo_first_trade_actual_owner_command_run.py tests/forex_engine/test_oanda_demo_first_trade_actual_owner_command_run.py scripts/forex_delivery/run_oanda_demo_first_trade_actual_owner_command_run.py`: pending final lane validation
- `python -m pytest tests/forex_engine/test_oanda_demo_first_trade_actual_owner_command_run.py -q`: pending final lane validation
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: pending final lane validation
- `git diff --check`: pending final lane validation

## Git Status

Branch `feature/forex-oanda-demo-first-trade-actual-owner-command-run` with four scoped actual-owner-command files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

OWNER MANUAL ACTION ONLY:

Run the exact OANDA demo one-order command only if GO remains true and the execution window remains ready. Codex must not run the broker command.
