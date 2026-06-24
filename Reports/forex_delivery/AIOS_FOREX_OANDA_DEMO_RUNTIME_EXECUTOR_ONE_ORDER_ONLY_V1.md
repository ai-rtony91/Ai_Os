# AIOS Forex OANDA Demo Runtime Executor One-Order-Only V1

## Packet Context

Packet ID: AIOS-MERGE-1053-THEN-FOREX-OANDA-DEMO-RUNTIME-EXECUTOR-ONE-ORDER-ONLY-V1

Branch: feature/forex-oanda-demo-runtime-executor-one-order-only-v1

Mission outcome: created the one-order-only runtime contract evaluator for the governed OANDA demo path.

## Why This Is The One-Order-Only Runtime Contract

This evaluator sits after the final-gated runtime package and before any separate broker execution packet. It confirms that the package is ready, the runtime context is demo-only, no open or pending order conflicts exist, and Anthony has confirmed the one-order-only boundary.

It models the final runtime executor contract for exactly one OANDA demo order attempt, but it does not perform that attempt.

## Why This Still Does Not Place A Trade

This module does not call OANDA, does not call a broker, does not read credentials, does not read account IDs, does not persist runtime material, and does not place a demo or live order.

The output status `ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET` means a separate packet may be reviewed. It does not authorize this module to execute.

## Final-Gated Dependency

The final-gated dependency requires:

- `FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET`
- prepared runtime package status `READY_FOR_SEPARATE_RUNTIME_EXECUTOR_PACKET`
- all final-gated execution authority fields false

## Runtime Context Requirements

The runtime one-order context requires:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo environment true
- live environment false
- runtime-only credentials present
- credential persistence false
- account ID persistence false
- one order only true
- existing open orders zero
- existing pending orders zero
- order already attempted false
- broker network call performed false
- order placement performed false
- kill switch ready
- daily stop ready
- max loss gate ready
- hard stop loss ready
- hard take profit ready
- pre-trade evidence ready
- post-trade evidence plan ready

## Owner Confirmation Requirements

Anthony must confirm:

- demo-only
- one order only
- no live money
- stop loss
- take profit
- loss is possible
- no profit guarantee
- runtime credentials remain outside repo
- no autonomous execution
- separate broker execution packet is required

## One-Order Contract

The ready contract returns:

- broker `OANDA_DEMO`
- environment `DEMO`
- contract status `READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET`
- one order only true
- max order attempts 1
- live trading false
- autonomous execution false
- credential persistence false
- account ID persistence false
- hard stop loss required
- hard take profit required
- pre-trade evidence required
- post-trade evidence required
- morning proof required if overnight

## Execution Rehearsal Steps

1. verify OANDA demo environment
2. verify no live environment
3. verify one-order-only state
4. verify no existing open or pending orders
5. verify runtime-only credentials are present outside repo
6. verify stop loss and take profit are ready
7. verify pre-trade evidence is ready
8. prepare separate broker execution packet
9. stop before broker call

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

- `python -m py_compile automation/forex_engine/oanda_demo_runtime_executor_one_order_only_v1.py tests/forex_engine/test_oanda_demo_runtime_executor_one_order_only_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_runtime_executor_one_order_only_v1.py -q`: PASS, 19 passed

Full lane validation:

- `python -m py_compile automation/forex_engine/oanda_demo_runtime_executor_one_order_only_v1.py tests/forex_engine/test_oanda_demo_runtime_executor_one_order_only_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_runtime_executor_one_order_only_v1.py -q`: PASS, 19 passed
- `python -m compileall automation/forex_engine tests/forex_engine`: PASS
- `git diff --check`: PASS
- `git diff --name-only`: scoped one-order-only runtime executor files only
- `git status --short --branch`: branch `feature/forex-oanda-demo-runtime-executor-one-order-only-v1`; `docs/legal/` remains untouched and untracked

## Git Status

After validation: new branch with three scoped one-order-only runtime executor files pending staging. `docs/legal/` remains untouched and untracked.

## Next Safe Action

Run the full validator chain, stage only the three approved files, commit, push, and open the PR. Do not place a trade. Do not call OANDA. Do not touch `docs/legal/`.
