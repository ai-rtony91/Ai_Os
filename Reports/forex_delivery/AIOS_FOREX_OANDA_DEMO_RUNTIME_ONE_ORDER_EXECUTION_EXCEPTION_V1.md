# AIOS Forex OANDA Demo Runtime One-Order Execution Exception V1

## Packet Context

Packet ID: AIOS-MERGE-1055-THEN-FOREX-OANDA-DEMO-RUNTIME-ONE-ORDER-EXECUTION-EXCEPTION-V1

Branch: feature/forex-oanda-demo-runtime-one-order-execution-exception-v1

Mission outcome: created the runtime one-order execution exception evaluator and CLI safety wrapper for a protected OANDA demo order attempt path.

## Why This Is The Runtime Exception Shell

This evaluator sits after the broker execution packet. It validates the ready broker execution packet, demo-only runtime exception context, runtime-only token/account state, and explicit owner approval before returning `EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT`.

The evaluator may return `allowed_manual_runtime_invocation: true` only when all gates pass. Execution authority still remains false.

## Why This Still Does Not Place A Trade Automatically

This packet does not call OANDA, does not call a broker, does not read credentials, does not read account IDs, does not persist runtime material, and does not place a demo or live order.

The CLI wrapper defaults to dry-run JSON output. Its `--execute-demo-order` flag remains blocked pending broker adapter implementation.

## Broker Execution Packet Dependency

The broker execution packet gate requires:

- `BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT`
- packet status `READY_FOR_EXTERNAL_RUNTIME_ONLY_ORDER_ATTEMPT`
- broker `OANDA_DEMO`
- environment `DEMO`
- order attempt limit 1
- one order only true
- live trading false
- autonomous execution false
- hard stop loss required
- hard take profit required
- pre-trade evidence required
- post-trade evidence required
- all broker packet execution authority fields false

## Runtime Exception Context Requirements

The runtime exception context requires:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo environment true
- live environment false
- runtime-only credentials present
- credential persistence false
- account ID persistence false
- account ID runtime-only true
- token runtime-only true
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
- manual runtime invocation required true

## Owner Approval Requirements

Anthony must approve or confirm:

- manual runtime demo order attempt
- demo-only
- no live money
- one order only
- max one attempt
- stop loss
- take profit
- loss possible
- no profit guarantee
- runtime credentials outside repo
- manual invocation required
- no autonomous execution

## CLI Safety Wrapper

Created:

`scripts/forex_delivery/run_oanda_demo_runtime_one_order_execution_exception_v1.py`

The wrapper imports the evaluator and prints JSON. It does not read `.env`, does not read credentials, does not call OANDA, does not persist account IDs, and does not place an order.

## Dry-Run Behavior

With no `--execute-demo-order` flag, the wrapper prints JSON with:

- `script_status: DRY_RUN_DECISION_ONLY`
- broker network call false
- order placement false
- credential read false
- account ID read false

## Execute Flag Behavior

With `--execute-demo-order`, the wrapper requires:

- `--i-understand-demo-only`
- `--i-understand-one-order-only`
- `--i-understand-loss-possible`
- `--i-understand-no-profit-guarantee`
- `--i-confirm-stop-loss`
- `--i-confirm-take-profit`

If confirmations are missing, it returns `BLOCKED_MISSING_REQUIRED_CONFIRMATIONS`.

If all confirmations are present, it still returns `BLOCKED_PENDING_BROKER_ADAPTER_IMPLEMENTATION`. No OANDA call is implemented in this packet.

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

- `python -m py_compile automation/forex_engine/oanda_demo_runtime_one_order_execution_exception_v1.py tests/forex_engine/test_oanda_demo_runtime_one_order_execution_exception_v1.py scripts/forex_delivery/run_oanda_demo_runtime_one_order_execution_exception_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_runtime_one_order_execution_exception_v1.py -q`: PASS, 21 passed

Full lane validation:

- `python -m py_compile automation/forex_engine/oanda_demo_runtime_one_order_execution_exception_v1.py tests/forex_engine/test_oanda_demo_runtime_one_order_execution_exception_v1.py scripts/forex_delivery/run_oanda_demo_runtime_one_order_execution_exception_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_runtime_one_order_execution_exception_v1.py -q`: PASS, 21 passed
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS
- `git diff --check`: PASS
- `git diff --name-only`: scoped runtime exception files only
- `git status --short --branch`: branch `feature/forex-oanda-demo-runtime-one-order-execution-exception-v1`; `docs/legal/` remains untouched and untracked

## Git Status

After validation: new branch with four scoped runtime one-order execution exception files pending staging. `docs/legal/` remains untouched and untracked.

## Next Safe Action

Run the full validator chain, stage only the four approved files, commit, push, and open the PR. Do not place a trade. Do not call OANDA. Do not touch `docs/legal/`.
