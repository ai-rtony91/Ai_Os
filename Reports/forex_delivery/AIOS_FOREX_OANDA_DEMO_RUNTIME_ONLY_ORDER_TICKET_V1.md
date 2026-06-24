# AIOS Forex OANDA Demo Runtime-Only Order Ticket V1

## Packet Context

Packet ID: AIOS-MERGE-1048-THEN-FOREX-RUNTIME-ONLY-DEMO-ORDER-TICKET-V1

Branch: feature/forex-runtime-only-demo-order-ticket-v1

This packet creates the runtime-only demo order ticket readiness layer after the compounding capital bucket supervisor milestone. It is execution-path preparation for owner review, not broker execution.

## Mission Outcome

Created a deterministic, side-effect-free Forex evaluator that can package a reviewed OANDA demo order ticket only when the profitability bridge, owner approval evidence, compounding bucket supervisor, runtime context, stop loss, take profit, reward/risk, and overnight controls all pass.

## Why This Is The Execution Doorway

The module turns prior readiness artifacts into a non-executable order ticket payload. It is the handoff shape that a later runtime-only owner-final-click lane can inspect before any separately approved demo action.

## Why This Still Does Not Place A Trade

The evaluator performs no broker call, reads no credentials, reads no account identifiers, starts no background runtime, and writes no broker state. The returned ticket has status `REVIEW_ONLY_NOT_EXECUTABLE`.

## Required Hard Stop Loss

Every order ticket requires `stop_loss`. BUY tickets require `stop_loss < planned_entry < take_profit`. SELL tickets require `take_profit < planned_entry < stop_loss`.

## Required Hard Take Profit

Every order ticket requires `take_profit` and a reward/risk ratio at or above the configured minimum. The default minimum is 1.5.

## Overnight Trade Handling

Overnight review is blocked unless stop loss, take profit, daily stop, max loss gate, kill switch, max overnight risk amount, and an overnight risk note are present. Overnight risk amount must remain at or below the runtime maximum.

## Compounding Bucket Dependency

The evaluator requires the compounding bucket supervisor to be in an accumulating, collect-profit, or redistribution-review state. It rejects forced quota chasing and requires the instrument to be supported by the allocation plan or active cycle.

## Owner Approval Evidence Dependency

The evaluator requires owner evidence status to be ready for runtime-only demo review or awaiting post-trade result. It blocks live trading approval and autonomous execution approval.

## Profitability Bridge Dependency

The evaluator requires the OANDA demo micro-trade profitability bridge to be `MICRO_TRADE_READY_FOR_OWNER_REVIEW` with all execution authority fields false.

## Runtime-Only Credential Boundary

The runtime context must declare OANDA demo, demo environment true, live environment false, runtime-only credentials required, credential persistence false, account ID persistence false, no broker network call performed, no order placement performed, and owner runtime review required.

## Execution Authority False

The module always returns false for:

- `execution_allowed`
- `demo_order_allowed`
- `live_order_allowed`
- `broker_write_allowed`
- `autonomous_order_allowed`
- `scheduler_allowed`
- `daemon_allowed`
- `webhook_allowed`

## Validation Results

Validation passed in this lane:

- `python -m py_compile automation/forex_engine/oanda_demo_runtime_only_order_ticket_v1.py tests/forex_engine/test_oanda_demo_runtime_only_order_ticket_v1.py`
- `python -m pytest tests/forex_engine/test_oanda_demo_runtime_only_order_ticket_v1.py -q` - 19 passed
- `python -m compileall automation/forex_engine tests/forex_engine`
- `git diff --check`
- `git diff --name-only`
- `git status --short --branch`

## Git Status

Final status before staging showed branch `feature/forex-runtime-only-demo-order-ticket-v1` with the three scoped runtime ticket files untracked and `docs/legal/` still untracked and untouched.

## Next Safe Action

Validate the runtime-only demo order ticket lane, stage only the three approved files, commit, push, and open the PR. The next milestone remains `AIOS-FOREX-OANDA-DEMO-FINAL-OWNER-CLICK-ORDER-BRIDGE-V1`.
