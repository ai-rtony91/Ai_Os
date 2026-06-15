# AIOS Forex Builder Broker-Paper Sandbox Gate

This document defines the future readiness gate only. It does not approve broker-paper trading, broker integration, live trading, credentials, network market automation, or order placement.

## Why This Gate Exists

Local paper-forward evidence can look promising while still being fragile. Before AIOS can even consider a broker-paper sandbox packet, it must show that local evidence is not dependent on one fixture, symbol, timeframe, regime, low-cost assumption, or unstressed fill model.

## Required Evidence Before Consideration

- Multi-fixture paper-forward evidence exists.
- Risk-to-reward and expectancy thresholds are evaluated.
- Opportunity capture, missed simulated PnL, cost drag, drawdown, and return percent are visible.
- Stress scenarios are reported, including conservative and disaster cases.
- Heldout fixtures are reported.
- Leave-one-regime, leave-one-symbol, and leave-one-timeframe checks are reported.
- Combined stress/OOS classification is FAIL, WATCHLIST, or PAPER_FORWARD_READY only.
- Live ready remains false.
- Protected gate required remains true.

## Contract Boundary

A future broker-paper sandbox readiness packet may define contracts, safety checks, and approval requirements. It must not:

- integrate a broker SDK
- place broker paper orders
- place live orders
- read or write credentials, secrets, or `.env`
- use live market APIs
- mutate accounts
- start schedulers or daemons
- use webhooks
- bypass protected approval

## Readiness Meaning

PAPER_FORWARD_READY is local simulation readiness only. It means AIOS has a stronger basis for the next protected review. It cannot authorize broker-paper trading or live trading.

The next protected step, if earned, is a broker-paper sandbox readiness contract. Broker integration remains a separate future approval.
