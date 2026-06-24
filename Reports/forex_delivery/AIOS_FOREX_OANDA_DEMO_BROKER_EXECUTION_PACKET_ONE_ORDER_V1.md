# AIOS Forex OANDA Demo Broker Execution Packet One Order V1

## Packet Context

Packet ID: AIOS-MERGE-1054-THEN-FOREX-OANDA-DEMO-BROKER-EXECUTION-PACKET-ONE-ORDER-V1

Branch: feature/forex-oanda-demo-broker-execution-packet-one-order-v1

Mission outcome: created the final broker execution packet model for one protected OANDA demo order attempt.

## Why This Is The Final Broker Execution Packet Model

This evaluator sits after the one-order-only runtime contract. It prepares the final broker execution packet shape for a separate runtime-only process by requiring the ready one-order contract, a demo-only broker execution context, and explicit owner approval for the separate runtime demo order attempt.

## Why This Still Does Not Place A Trade

This module does not call OANDA, does not call a broker, does not read credentials, does not read account IDs, does not persist runtime material, and does not place a demo or live order.

`BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT` means the packet can be reviewed for a later separate runtime action. It does not authorize this module to execute.

## One-Order Contract Dependency

The one-order dependency requires:

- `ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET`
- one-order contract status `READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET`
- all one-order execution authority fields false

## Broker Execution Context Requirements

The broker execution context requires:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo environment true
- live environment false
- runtime-only credentials present
- credential persistence false
- account ID persistence false
- one order only true
- max order attempts 1
- existing open orders zero
- existing pending orders zero
- order already attempted false
- kill switch ready
- daily stop ready
- max loss gate ready
- hard stop loss ready
- hard take profit ready
- pre-trade evidence ready
- post-trade evidence plan ready
- broker network call performed false
- order placement performed false

## Owner Approval Requirements

Anthony must approve or confirm:

- separate runtime demo order attempt
- demo-only
- no live money
- one order only
- max one attempt
- stop loss
- take profit
- loss is possible
- no profit guarantee
- runtime credentials remain outside repo
- no autonomous execution

## Broker Execution Packet Fields

The ready broker execution packet returns:

- broker `OANDA_DEMO`
- environment `DEMO`
- packet status `READY_FOR_EXTERNAL_RUNTIME_ONLY_ORDER_ATTEMPT`
- order attempt limit 1
- one order only true
- live trading false
- autonomous execution false
- credential persistence false
- account ID persistence false
- hard stop loss required
- hard take profit required
- pre-trade evidence required
- post-trade evidence required
- stop after order attempt true
- morning proof required if overnight true

## Pre-Trade Evidence Requirements

- broker_environment
- instrument
- direction
- order_type
- planned_entry
- stop_loss
- take_profit
- position_size_units
- risk_amount
- reward_risk_ratio
- spread_snapshot
- balance_snapshot
- nav_snapshot
- margin_snapshot
- timestamp_utc
- owner_approval_id

## Post-Trade Evidence Requirements

- order_attempted
- order_id_or_sanitized_reference
- filled_or_rejected
- fill_price_or_rejection_reason
- stop_loss_attached
- take_profit_attached
- realized_pl_when_closed
- close_reason
- post_balance
- post_nav
- timestamp_utc

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

## Validation Results

Targeted validation before report creation:

- `python -m py_compile automation/forex_engine/oanda_demo_broker_execution_packet_one_order_v1.py tests/forex_engine/test_oanda_demo_broker_execution_packet_one_order_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_broker_execution_packet_one_order_v1.py -q`: PASS, 20 passed

Full lane validation:

- `python -m py_compile automation/forex_engine/oanda_demo_broker_execution_packet_one_order_v1.py tests/forex_engine/test_oanda_demo_broker_execution_packet_one_order_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_broker_execution_packet_one_order_v1.py -q`: PASS, 20 passed
- `python -m compileall automation/forex_engine tests/forex_engine`: PASS
- `git diff --check`: PASS
- `git diff --name-only`: scoped broker execution packet files only
- `git status --short --branch`: branch `feature/forex-oanda-demo-broker-execution-packet-one-order-v1`; `docs/legal/` remains untouched and untracked

## Git Status

After validation: new branch with three scoped broker execution packet files pending staging. `docs/legal/` remains untouched and untracked.

## Next Safe Action

Run the full validator chain, stage only the three approved files, commit, push, and open the PR. Do not place a trade. Do not call OANDA. Do not touch `docs/legal/`.
