# AIOS Forex OANDA Demo Runtime HTTP Transport One Order Owner Run V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-RUNTIME-HTTP-TRANSPORT-ONE-ORDER-OWNER-RUN-V1

Branch: feature/forex-oanda-demo-runtime-http-transport-one-order-owner-run-v1

Mission outcome: created the owner-run-only OANDA demo runtime HTTP transport bridge, owner CLI wrapper, and tests for exactly one manually approved demo order attempt path.

## Why This Is The Runtime HTTP Transport Layer

This layer sits after the actual owner command package and broker-call readiness package. The previous broker-call lane could build a sanitized request but intentionally stopped at `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED`.

This packet adds the final runtime HTTP bridge. It can create the real OANDA demo POST request only when Anthony later runs the owner script with runtime-only environment credentials, all owner confirmation flags, a sanitized one-order payload, stop loss, take profit, and one-order cap evidence.

## Why Tests, Import, And PR Creation Do Not Call OANDA Or Place Trades

The evaluator performs no import-time network call, no import-time environment read, no `.env` read, no credential file read, and no account identifier persistence.

Tests use a pure fake callable. Validation, compile, commit, push, and PR creation do not invoke `--execute-transport` and do not call the broker.

## Owner Command Dependency

The actual owner command result must have:

- status `ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND`
- `final_manual_command_package.ready` true
- one order only true
- max order attempts `1`
- all execution authority fields false

## Broker-Call Dependency

The broker-call result must have status `BROKER_CALL_DRY_RUN_READY` or `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED`.

It must prove network call false, order placement false, execution authority false, and no token, account ID, credential, secret, password, or authorization keys anywhere recursively.

## Transport Context Requirements

The runtime transport context requires OANDA demo, demo environment, demo endpoint only, live endpoint absent, practice base URL, runtime token external, runtime account ID external, credentials available only to the owner, no credential persistence, no account ID persistence, one order only, max one attempt, no prior attempt, zero open orders, zero pending orders, owner present, kill switch ready, daily stop ready, max loss gate ready, stop loss ready, take profit ready, pre-trade evidence ready, post-trade evidence plan ready, execution window open, and market open or owner override true.

## Order Payload Requirements

The sanitized order payload requires instrument, BUY or SELL direction, MARKET/LIMIT/STOP type, positive units, stop loss, take profit, positive risk amount, reward-risk ratio at least `1.0`, and a sanitized client order ID.

The OANDA payload signs units positive for BUY and negative for SELL, uses `positionFill: DEFAULT`, includes `clientExtensions.id`, and attaches stop-loss and take-profit prices as strings.

## Owner Confirmation Requirements

Anthony must confirm transport review, actual demo-order intent, demo-only scope, no live money, one order only, max one attempt, stop loss, take profit, loss possible, no profit guarantee, no second order, manual run only, post-trade evidence required, kill switch ready, and runtime credentials external.

## Exact Execute-Transport Behavior

With `execute_transport` false, all gates passing returns `TRANSPORT_DRY_RUN_READY` with no network call and no order placement.

With `execute_transport` true and missing runtime token or account ID, the evaluator returns `TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING` with no network call.

With `execute_transport` true and no callable, the evaluator returns `TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED` with no network call.

With `execute_transport` true, all gates passing, runtime credentials supplied, and a callable supplied, the callable receives exactly one POST request to the OANDA demo endpoint. The result status is `TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE`.

## Runtime Env Var Rule

The owner script reads runtime values only from process environment variables:

- `OANDA_DEMO_ACCESS_TOKEN`
- `OANDA_DEMO_ACCOUNT_ID`

It does not read `.env`, does not print runtime values, and does not persist credentials or account identifiers.

## One-Order Cap

The evaluator requires one order only, max order attempts `1`, order already attempted false, zero open orders, and zero pending orders. The transport callable is invoked at most once.

## Kill Switch Plan

Before run: confirm kill switch, daily stop, max loss gate, stop loss, take profit, owner presence, and pre-trade evidence.

During run: if any blocker appears, stop and do not retry.

After run: capture sanitized post-trade evidence and do not rerun the command.

## Risk Controls

- OANDA demo endpoint only
- no live endpoint
- no live money
- one order only
- no second order
- no retry loop
- stop loss required
- take profit required
- loss possible
- no profit guarantee
- owner manual run only
- post-trade evidence required

## Redaction Rules

Returned evidence redacts token, account ID, authorization, `accountID`, `account_id`, and credential-looking keys. Exact runtime token and account ID values are scrubbed from scalar strings before output.

## No Live Endpoint Rule

The transport context rejects non-practice base URLs and any live API base URL. The only permitted base URL prefix is `https://api-fxpractice.oanda.com`.

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

This owner-run runtime bridge does not grant Codex, schedulers, daemons, webhooks, or autonomous systems authority to place orders.

## Validation Results

Targeted validation after implementation:

- `python -m py_compile automation/forex_engine/oanda_demo_runtime_http_transport_one_order_owner_run_v1.py tests/forex_engine/test_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py -q`: PASS, 36 passed
- `python -m compileall automation/forex_engine tests/forex_engine scripts/forex_delivery`: PASS
- `git diff --check`: PASS

## Git Status

Branch `feature/forex-oanda-demo-runtime-http-transport-one-order-owner-run-v1` contains four scoped runtime HTTP transport files. `docs/legal/` remains untouched and untracked outside the lane.

## Exact Next Safe Action After PR Lands

OWNER MANUAL ACTION ONLY: execute the runtime HTTP transport for one OANDA demo order only if GO remains true, the execution window remains valid, all confirmations remain true, runtime credentials are supplied outside the repo, and post-trade evidence capture is ready.
