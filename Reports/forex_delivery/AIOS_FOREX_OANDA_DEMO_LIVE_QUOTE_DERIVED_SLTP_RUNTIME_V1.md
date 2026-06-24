# AIOS Forex OANDA Demo Live Quote Derived SLTP Runtime V1

## 1. Prior Cancel Pattern

The latest owner evidence shows a repeated broker-side cancel pattern:

- static reference-price correction reached OANDA practice and canceled with
  `TAKE_PROFIT_ON_FILL_LOSS`
- static bid/ask correction reached OANDA practice and canceled with
  `TAKE_PROFIT_ON_FILL_LOSS`
- no `orderFillTransaction` was observed for the latest bid/ask-corrected run
- no fill, profit, strategy edge, allocation progress, or `120%` claim is supported

This packet does not reinterpret any canceled order as success.

## 2. Correction Standard

Static bid/ask inputs can become stale before broker evaluation. The new owner runtime flow fetches
current OANDA practice pricing immediately before order construction, derives SL/TP from the fresh
executable side, validates the computed values, and only then prepares or submits the one-order demo
request.

Created local packet components:

- `automation/forex_engine/oanda_demo_live_quote_derived_sltp_runtime_v1.py`
- `scripts/forex_delivery/run_oanda_demo_live_quote_derived_sltp_runtime_v1.py`
- `tests/forex_engine/test_oanda_demo_live_quote_derived_sltp_runtime_v1.py`

## 3. Owner Runtime Modes

Supported owner modes:

```text
--owner-build-live-quote-derived-demo-order
--owner-execute-live-quote-derived-demo-order
```

`--owner-build-live-quote-derived-demo-order` loads approved runtime credentials, fetches practice
pricing, computes SL/TP, validates the computed values, and returns sanitized JSON without placing
an order.

`--owner-execute-live-quote-derived-demo-order` performs the same pricing and validation path, then
may submit exactly one OANDA practice/demo order if all gates pass.

Codex did not run either owner mode.

## 4. Approved Vault Boundary

The owner runtime supports only these approved Windows Vault labels:

```text
AIOS_OANDA_DEMO_ACCESS_TOKEN
AIOS_OANDA_DEMO_ACCOUNT_ID
```

The CLI does not accept token or account ID arguments. It does not read `.env`, environment
variables, repo secret files, or account ID files.

All output is sanitized and redacts credential/account values.

## 5. Pricing Boundary

The owner runtime fetches current pricing with a read-only OANDA practice/demo GET request for
`EUR_USD`.

The pricing snapshot records:

- instrument
- timestamp when available
- current bid
- current ask

No live endpoint is supported.

## 6. SL/TP Derivation Rules

Inputs are pip distances, not absolute SL/TP prices:

- `--stop-loss-pips`
- `--take-profit-pips`
- `--min-distance-pips`
- `--pip-size 0.0001`

BUY rule:

- executable side: `ask`
- stop loss = current bid minus stop-loss pips
- take profit = current ask plus take-profit pips

SELL rule:

- executable side: `bid`
- stop loss = current ask plus stop-loss pips
- take profit = current bid minus take-profit pips

The computed absolute stop loss and take profit are validated through the bid/ask SLTP validator
before any owner order attempt.

## 7. One-Order Execution Boundary

The owner execute mode is one-order-only:

- no retries
- no second order
- no scheduler
- no daemon
- no webhook
- no autonomous execution
- no live endpoint

Post-trade evidence is required after any owner execution.

## 8. No Profit Claim

This packet does not claim:

- fill
- realized profit
- unrealized profit
- strategy edge
- allocation progress
- campaign progress
- `120%` return

Any owner execution requires a separate sanitized post-trade evidence report before outcome
classification.

## 9. Next Safe Action

Next safe action:

```text
Owner may review the live-quote-derived runtime template. Codex must not run it.
```

Next required packet after any owner execution:

```text
AIOS-FOREX-OANDA-DEMO-LIVE-QUOTE-DERIVED-POST-TRADE-EVIDENCE-V1
```
