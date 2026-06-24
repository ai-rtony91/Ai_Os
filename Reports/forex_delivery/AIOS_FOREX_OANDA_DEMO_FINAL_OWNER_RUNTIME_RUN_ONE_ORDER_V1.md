# AIOS Forex OANDA Demo Final Owner Runtime Run One Order V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-FINAL-OWNER-RUNTIME-RUN-ONE-ORDER-V1

Branch: feature/forex-oanda-demo-final-owner-runtime-run-one-order-v1

Mission outcome: created the final owner runtime run evaluator and CLI safety wrapper for one protected OANDA demo order attempt path.

## Why This Is The Final Owner Runtime Run Packet

This packet sits after `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_ONE_ORDER_FINAL_WIRE_V1`. It requires the final wire decision object to be ready for manual runtime invocation, then validates explicit owner approval and OANDA demo-only runtime context before returning `OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND`.

This is the final owner runtime run package because it defines the last local decision gate, owner checklist, command surface, and evidence plan before a separate manual broker-call implementation lane can exist.

## Why This PR Still Does Not Place A Trade

This PR does not call OANDA, does not call a broker, does not read `.env`, does not read credentials, does not read account identifiers, does not persist runtime material, and does not place a demo or live order.

The CLI wrapper defaults to dry-run JSON output. Its `--execute-demo-order` flag requires explicit owner confirmations, then still returns `FINAL_OWNER_RUNTIME_RUN_READY_BUT_BROKER_CALL_NOT_IMPLEMENTED_IN_THIS_PR`.

## Final Wire Dependency

The final wire gate requires:

- status `FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT`
- final wire request status `READY_FOR_MANUAL_RUNTIME_INVOCATION`
- one order only true
- max order attempts 1
- live trading false
- autonomous execution false
- all final wire execution authority fields false

## Owner Approval Requirements

Anthony must approve or confirm:

- final manual runtime run
- demo-only
- no live money
- one order only
- max one attempt
- stop loss
- take profit
- loss possible
- no profit guarantee
- no second order
- manual run only
- no autonomous execution
- post-trade evidence required

## Runtime Context Requirements

The runtime context requires:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo environment true
- live environment false
- runtime credentials external
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
- pre-trade evidence ready
- post-trade evidence plan ready
- broker network call performed false
- order placement performed false

## CLI Safety Wrapper

Created:

`scripts/forex_delivery/run_oanda_demo_final_owner_runtime_run_one_order_v1.py`

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

- `--i-approve-final-manual-runtime-run`
- `--i-understand-demo-only`
- `--i-understand-one-order-only`
- `--i-understand-loss-possible`
- `--i-understand-no-profit-guarantee`
- `--i-confirm-stop-loss`
- `--i-confirm-take-profit`
- `--i-confirm-no-second-order`
- `--i-confirm-post-trade-evidence`

If confirmations are missing, it returns `BLOCKED_MISSING_REQUIRED_CONFIRMATIONS`.

If all confirmations are present, it still returns `FINAL_OWNER_RUNTIME_RUN_READY_BUT_BROKER_CALL_NOT_IMPLEMENTED_IN_THIS_PR`. No OANDA call is implemented in this packet.

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

- `python -m py_compile automation/forex_engine/oanda_demo_final_owner_runtime_run_one_order_v1.py tests/forex_engine/test_oanda_demo_final_owner_runtime_run_one_order_v1.py scripts/forex_delivery/run_oanda_demo_final_owner_runtime_run_one_order_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_final_owner_runtime_run_one_order_v1.py -q`: PASS, 22 passed

Full lane validation status in Codex:

- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: BLOCKED in Codex sandbox by `CreateProcessAsUserW failed: 1312` before Python launched
- `git diff --check`: PASS
- `git diff --name-only`: no tracked diff before staging because the scoped files were new and untracked
- `git status --short --branch`: branch `feature/forex-oanda-demo-final-owner-runtime-run-one-order-v1`; four scoped final owner runtime run files untracked; `docs/legal/` remains untouched and untracked

## Git Status

After report creation: branch `feature/forex-oanda-demo-final-owner-runtime-run-one-order-v1` with four scoped final owner runtime run files pending validation and staging. `docs/legal/` remains untouched and untracked.

## Next Safe Action

Complete the full validator chain, stage only the four approved files, commit, push, and open the PR. Do not place a trade. Do not call OANDA. Do not touch `docs/legal/`.

## Exact Next Manual Step After This PR Lands

After this PR lands, prepare the next packet:

`AIOS-FOREX-OANDA-DEMO-BROKER-CALL-IMPLEMENTATION-ONE-ORDER-MANUAL-RUN-V1`

That next packet must still be manual-run-only, demo-only, one-order-only, approval-gated, runtime-credential-only, and evidence-bound.
