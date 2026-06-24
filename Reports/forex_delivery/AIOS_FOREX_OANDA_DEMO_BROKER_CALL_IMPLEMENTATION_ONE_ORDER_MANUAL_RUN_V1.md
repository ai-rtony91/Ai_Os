# AIOS Forex OANDA Demo Broker Call Implementation One Order Manual Run V1

## Packet Context

Packet ID: AIOS-FOREX-OANDA-DEMO-BROKER-CALL-IMPLEMENTATION-ONE-ORDER-MANUAL-RUN-V1

Branch: feature/forex-oanda-demo-broker-call-one-order-manual-run-v1

Mission outcome: created the manual-run-only OANDA demo broker-call evaluator, CLI safety wrapper, and tests for one explicit owner-approved demo order attempt path.

## Why This Is The Broker-Call Implementation Lane

This packet sits after `AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_RUNTIME_RUN_ONE_ORDER_V1`. It adds the first broker-call implementation surface that can prepare an OANDA demo order request and, only with an injected runtime transport, attempt exactly one OANDA demo order.

The broker-call evaluator remains import-safe and test-safe. It requires final owner runtime readiness, demo-only broker context, a sanitized one-order payload, explicit owner broker-call approval, and an injected transport before any network call can occur.

## Why Tests, Import, And PR Creation Do Not Place A Trade

The module performs no import-time broker call, no import-time file read, no `.env` read, no environment-variable read, and no credential or account identifier persistence.

Tests use pure Python fake transport only. The CLI script keeps transport disabled in this PR and returns `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED` even when all execution confirmations are present.

## Final Owner Run Dependency

The final owner runtime result must include:

- status `OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND`
- `manual_runtime_run_contract.ready` true
- one order only true
- max order attempts 1
- actual execution requires owner command true
- all execution authority fields false

## Broker Call Context Requirements

The broker call context requires:

- broker `OANDA_DEMO`
- environment `DEMO`
- demo environment true
- live environment false
- demo API base URL beginning with `https://api-fxpractice.oanda.com`
- no live API base URL
- runtime access token present flag true
- runtime account ID present flag true
- token runtime-only true
- account ID runtime-only true
- credential persistence false
- account ID persistence false
- one order only true
- max order attempts 1
- order already attempted false
- existing open orders zero
- existing pending orders zero
- kill switch ready
- daily stop ready
- max loss gate ready
- pre-trade evidence ready
- post-trade evidence plan ready
- broker network call performed false
- order placement performed false

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
- no account ID, token, credential, secret, password, or authorization keys anywhere recursively

The generated OANDA payload sets BUY units positive and SELL units negative, uses `positionFill: DEFAULT`, includes client extension ID, and includes stop-loss and take-profit prices as strings.

## Owner Approval Requirements

Anthony must approve or confirm:

- actual OANDA demo broker call
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

## Manual Run Script Behavior

Created:

`scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py`

The script imports the evaluator and prints JSON. It reads no `.env`, reads no credentials, persists no credentials, persists no account IDs, and does not call a broker from this PR.

## Dry-Run Behavior

With no `--execute-demo-order` flag, the script prints JSON with:

- `script_status: DRY_RUN_DECISION_ONLY`
- broker network call false
- order placement false
- credential read false
- account ID read false

## Execute Flag Behavior

With `--execute-demo-order`, the script requires:

- `--i-approve-actual-oanda-demo-broker-call`
- `--i-understand-demo-only`
- `--i-understand-one-order-only`
- `--i-understand-loss-possible`
- `--i-understand-no-profit-guarantee`
- `--i-confirm-stop-loss`
- `--i-confirm-take-profit`
- `--i-confirm-no-second-order`
- `--i-confirm-post-trade-evidence`

If confirmations are missing, it returns `BLOCKED_MISSING_REQUIRED_CONFIRMATIONS`.

If all confirmations are present, it still returns `BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED` because this PR does not enable script-level network transport.

## Transport Injection Rule

The evaluator calls network only when all gates pass, `execute_demo_order=True`, and `http_transport` is callable. The injected transport receives exactly one request dictionary with:

- method `POST`
- demo-practice URL using `RUNTIME_ONLY_ACCOUNT_ID` placeholder
- authorization header using `RUNTIME_ONLY_BEARER_TOKEN` placeholder
- JSON OANDA order payload
- timeout 10 seconds

Returned evidence is sanitized so actual token and account ID values are not exposed.

## No Live Endpoint Rule

The context gate rejects live API base URLs and requires the demo practice base URL prefix `https://api-fxpractice.oanda.com`.

## One-Order Cap

The evaluator requires one-order-only true, max order attempts 1, no already-attempted order, zero open orders, and zero pending orders. When injected transport is called, it is called exactly once.

## No Credential Or Account Persistence

The evaluator uses runtime-present flags and sanitized placeholders. It does not read, write, return, or persist actual credentials or account identifiers.

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

Even when injected owner runtime transport is called, repo/governance execution authority remains false because the call is a manual owner runtime exception path only.

## Validation Results

Targeted validation before report creation:

- `python -m py_compile automation/forex_engine/oanda_demo_broker_call_one_order_manual_run_v1.py tests/forex_engine/test_oanda_demo_broker_call_one_order_manual_run_v1.py scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_broker_call_one_order_manual_run_v1.py -q`: PASS, 35 passed

Full validation after report creation:

- final validation recorded in the Codex completion report

## Git Status

Branch `feature/forex-oanda-demo-broker-call-one-order-manual-run-v1` with four scoped broker-call implementation files pending final validation and staging. `docs/legal/` remains untouched and untracked.

## Exact Next Safe Action After PR Lands

Prepare the next packet:

`AIOS-FOREX-OANDA-DEMO-OWNER-RUN-ACTUAL-ONE-ORDER-COMMAND-V1`

That packet must remain demo-only, one-order-only, owner-manual-run-only, runtime-credential-only, transport-injected, evidence-bound, and blocked from live trading, autonomous execution, schedulers, daemons, webhooks, credential persistence, and account ID persistence.
