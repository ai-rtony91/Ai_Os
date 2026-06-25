# AIOS Forex Broker Balance Bucket Equity Separation V1

## Packet Context

Packet ID: AIOS-FOREX-BROKER-BALANCE-BUCKET-EQUITY-SEPARATION-V1

Branch: feature/forex-broker-balance-bucket-equity-separation-v1

Mission outcome: created the governed broker balance, NAV/equity, unrealized P/L, AIOS bucket, and next-trade risk separation layer.

## Root Cause

After the OANDA demo micro trade was classified as open unrealized, AIOS needed a pre-allocation layer that prevents broker account values from being treated as AIOS trade capital.

Broker balance, NAV/equity, unrealized P/L, realized account P/L, and the configured AIOS trade bucket are related but not interchangeable:

- broker balance is not the AIOS trade bucket.
- NAV/equity may include open unrealized P/L.
- unrealized P/L is not withdrawable or compoundable profit.
- next-trade risk must be based on the configured AIOS bucket and risk policy.
- an open trade or position blocks next-trade permission unless policy explicitly allows review, and owner approval is still required.
- live allocation remains false.

## Implementation Summary

Created:

- `automation/forex_engine/broker_balance_bucket_equity_separation_v1.py`
- `scripts/forex_delivery/run_broker_balance_bucket_equity_separation_v1.py`
- `tests/forex_engine/test_broker_balance_bucket_equity_separation_v1.py`

The evaluator accepts sanitized in-memory account snapshot fields:

- balance
- NAV
- unrealizedPL
- pl
- marginUsed
- marginAvailable
- openTradeCount
- openPositionCount
- pendingOrderCount

It accepts AIOS bucket/risk policy fields:

- bucket_currency
- configured_trade_bucket_balance
- max_single_trade_risk_pct
- max_next_trade_risk_pct
- demo_only
- live_trading
- one_order_only
- require_owner_approval_for_next_trade
- allow_next_trade_while_open_position
- compounding_enabled
- no_live_allocation

The evaluator returns separated decision fields for:

- broker reported balance
- broker reported NAV
- account equity
- unrealized P/L
- realized lifetime or account P/L
- AIOS trade bucket balance
- max single-trade risk amount
- max next-trade risk amount
- risk available balance
- open exposure presence
- next-trade permission
- live allocation permission
- compounding permission
- withdrawal permission

## Safety Rules Implemented

Balance must be numeric and non-negative. NAV must be numeric and non-negative when supplied. Account equity uses NAV when present and falls back to balance plus unrealized P/L when NAV is absent.

The AIOS trade bucket must be explicitly configured. It does not automatically equal the full broker balance. If the configured bucket equals broker balance, the policy must explicitly say that equality is allowed.

Risk amounts are calculated from the configured AIOS trade bucket, not the full broker balance.

Unrealized P/L is never treated as compoundable or withdrawable profit. Realized account P/L is reported only; bucket updates remain deferred to the existing result-to-bucket layer.

Live trading true is rejected. Live allocation remains false and no live allocation remains true.

Owner approval remains required for any next trade.

## CLI Runner

The CLI runner prints sanitized JSON only. It does not read files, credentials, account identifiers, `.env`, environment variables, broker APIs, or raw broker payloads.

Supported modes are default dry-run package output, sanitized template output, and sanitized flat-account sample output. No owner-run command is issued in this packet.

## Tests Added

Unit tests cover:

- open trade blocks next trade by default.
- NAV/equity differs from broker balance when unrealized P/L exists.
- AIOS trade bucket remains separate from broker balance.
- bucket equality with broker balance requires explicit policy.
- max risk amount uses the trade bucket, not full broker balance.
- live trading true is rejected.
- compounding and withdrawal remain false while a trade is open/unrealized.
- network, broker, order, credential, endpoint, and persistence flags remain false.
- equity fallback uses balance plus unrealized P/L when NAV is absent.
- CLI default and template modes print sanitized JSON.

## Validation Results

Completed final lane validation:

- `python -m pytest tests/forex_engine/test_broker_balance_bucket_equity_separation_v1.py -q`: PASS, 11 passed
- `python -m py_compile automation/forex_engine/broker_balance_bucket_equity_separation_v1.py scripts/forex_delivery/run_broker_balance_bucket_equity_separation_v1.py`: PASS
- `git diff --check`: PASS
- `git status --short --branch`: PASS, four allowed untracked files only

## Next Safe Action

Run the validator chain and review the scoped diff. Do not commit, push, create a PR, merge, call a broker, place an order, close an order, mutate a trade or position, or perform any live funding step.
