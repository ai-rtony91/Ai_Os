# AIOS Forex OANDA Demo Broker Adapter One-Order Final Wire V1

## Packet Context

Packet ID: AIOS-MERGE-1056-THEN-FOREX-OANDA-DEMO-BROKER-ADAPTER-ONE-ORDER-FINAL-WIRE-V1

Branch: feature/forex-oanda-demo-broker-adapter-one-order-final-wire-v1

Mission outcome: created the final broker adapter wire evaluator and CLI safety wrapper for one protected OANDA demo order attempt path.

## Why This Is The Final Wire Before The Manual Runtime Run

This evaluator sits after `AIOS_FOREX_OANDA_DEMO_RUNTIME_ONE_ORDER_EXECUTION_EXCEPTION_V1`. It requires the runtime exception to be ready for manual runtime invocation, then validates demo-only adapter context, a sanitized order payload, and explicit final owner confirmations.

When every gate passes, the evaluator builds a final wire request with `READY_FOR_MANUAL_RUNTIME_INVOCATION`. That request is still only a decision object for a separate manual runtime run.

## Why This Still Does Not Place A Trade Automatically

This packet does not call OANDA, does not call a broker, does not read `.env`, does not read credentials, does not read account identifiers, does not persist runtime material, and does not place a demo or live order.

The CLI wrapper defaults to dry-run JSON output. Its `--execute-demo-order` flag remains blocked with `BLOCKED_PENDING_FINAL_OWNER_RUNTIME_RUN` even when all local confirmation flags are present.

## Runtime Exception Dependency

The runtime exception gate requires:

- status `EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT`
- `allowed_manual_runtime_invocation` true
- all runtime exception execution authority fields false
- `one_order_runtime_contract.one_order_only` true
- `one_order_runtime_contract.max_order_attempts` 1

## Adapter Context Requirements

The adapter runtime context requires:

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
- broker network call performed false
- order placement performed false
- manual runtime invocation required true

## Sanitized Order Payload Requirements

The sanitized order payload requires:

- non-empty instrument
- direction `BUY` or `SELL`
- order type `MARKET`, `LIMIT`, or `STOP`
- positive units
- stop loss present
- take profit present
- positive risk amount
- reward-risk ratio at least 1.0
- non-empty sanitized client order ID
- no account ID field
- no token field
- no credential field
- no secret field
- no password field
- no authorization field

## Owner Approval Requirements

The final owner approval gate requires Anthony to confirm:

- final manual demo order attempt approved
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
- no second order

## CLI Safety Wrapper

Created:

`scripts/forex_delivery/run_oanda_demo_broker_adapter_one_order_final_wire_v1.py`

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
- `--i-confirm-no-second-order`

If confirmations are missing, it returns `BLOCKED_MISSING_REQUIRED_CONFIRMATIONS`.

If all confirmations are present, it still returns `BLOCKED_PENDING_FINAL_OWNER_RUNTIME_RUN`. No OANDA call is implemented in this packet.

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

- `python -m py_compile automation/forex_engine/oanda_demo_broker_adapter_one_order_final_wire_v1.py tests/forex_engine/test_oanda_demo_broker_adapter_one_order_final_wire_v1.py scripts/forex_delivery/run_oanda_demo_broker_adapter_one_order_final_wire_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_broker_adapter_one_order_final_wire_v1.py -q`: PASS, 27 passed

Full lane validation:

- `python -m py_compile automation/forex_engine/oanda_demo_broker_adapter_one_order_final_wire_v1.py tests/forex_engine/test_oanda_demo_broker_adapter_one_order_final_wire_v1.py scripts/forex_delivery/run_oanda_demo_broker_adapter_one_order_final_wire_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_broker_adapter_one_order_final_wire_v1.py -q`: PASS, 27 passed
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS
- `git diff --check`: PASS
- `git diff --name-only`: no tracked diff before staging because the scoped files were new and untracked
- `git status --short --branch`: branch `feature/forex-oanda-demo-broker-adapter-one-order-final-wire-v1`; four scoped final-wire files untracked; `docs/legal/` remains untouched and untracked

## Git Status

After report creation: new branch with four scoped final-wire files pending staging. `docs/legal/` remains untouched and untracked.

## Next Safe Action

Run the full validator chain, stage only the four approved files, commit, push, and open the PR. Do not place a trade. Do not call OANDA. Do not touch `docs/legal/`.
