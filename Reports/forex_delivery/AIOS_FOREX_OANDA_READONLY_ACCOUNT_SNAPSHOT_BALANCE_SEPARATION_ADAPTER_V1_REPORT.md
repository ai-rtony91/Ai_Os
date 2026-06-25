# AIOS Forex OANDA Read-Only Account Snapshot Balance Separation Adapter V1

## Root Cause

PR #1094 landed the broker balance, bucket, NAV/equity, and risk separation evaluator, but the sanitized OANDA read-only filled-trade P/L capture output did not yet have a bridge into that evaluator.

AIOS needed an adapter that can consume sanitized account summary evidence without treating broker balance as the AIOS trade bucket, without treating NAV/equity as withdrawable cash, and without allowing open unrealized P/L to drive compounding, withdrawal, or next-trade permission.

## Implementation Summary

Created an adapter-only layer:

- `automation/forex_engine/oanda_readonly_account_snapshot_balance_separation_adapter_v1.py`
- `scripts/forex_delivery/run_oanda_readonly_account_snapshot_balance_separation_adapter_v1.py`
- `tests/forex_engine/test_oanda_readonly_account_snapshot_balance_separation_adapter_v1.py`

The adapter accepts:

- `read_only_capture_result`
- `bucket_risk_policy`

The adapter supports sanitized account snapshots from:

- `pl_evidence.account_summary_snapshot`
- `decision.pl_evidence.account_summary_snapshot`
- `account_summary_snapshot`
- `account_snapshot`

The adapter normalizes:

- `balance`
- `NAV`
- `unrealizedPL`
- `pl`
- `marginUsed`
- `marginAvailable`
- `openTradeCount`
- `openPositionCount`
- `pendingOrderCount`

When counts are absent, it derives:

- `openTradeCount` from `pl_evidence.open_trade_evidence`
- `openPositionCount` from `pl_evidence.open_position_evidence`

The adapter then delegates the actual broker balance, bucket, NAV/equity, and permission decision to `evaluate_broker_balance_bucket_equity_separation_v1`.

## Safety

This is adapter-only and not a bucket updater.

The adapter does not:

- call OANDA
- call any broker API
- read Windows Vault
- read `.env`
- read environment variables
- accept runtime secrets
- require or print account identifiers
- persist raw broker payloads
- place orders
- close orders
- mutate orders, trades, or positions
- authorize live allocation
- update the AIOS trade bucket

The adapter rejects unsafe input authority or performed-action flags when a capture result or policy says broker/network/credential/order/live/write capability was allowed or performed.

The CLI runner prints sanitized JSON only and uses a sanitized open-trade 328-style sample by default. It does not run the OANDA capture.

## Tests

Added tests for:

- extracting `account_summary_snapshot` from `pl_evidence`
- deriving open trade count from `open_trade_evidence`
- blocking next trade by default when open trade/position evidence exists
- using configured bucket balance for risk instead of full broker balance
- blocking missing account snapshots
- rejecting unsafe authority flags
- rejecting `live_trading=true` through the balance-separation evaluator
- supporting `decision.pl_evidence.account_summary_snapshot`
- CLI sanitized JSON output with broker/order/credential flags false
- CLI template output

## Validation

Validation completed for this lane:

```powershell
python -m pytest tests/forex_engine/test_oanda_readonly_account_snapshot_balance_separation_adapter_v1.py -q
# PASS, 10 passed

python -m py_compile automation/forex_engine/oanda_readonly_account_snapshot_balance_separation_adapter_v1.py scripts/forex_delivery/run_oanda_readonly_account_snapshot_balance_separation_adapter_v1.py
# PASS

git diff --check
# PASS

git status --short --branch
# PASS, four allowed untracked files only
```

Additional no-index whitespace checks were run against the four new untracked files so new-file content was checked without staging. No whitespace errors were reported.

## Next Safe Action

Run the validator chain and review the scoped diff. Do not commit, push, create a PR, merge, call a broker, run OANDA capture, read credentials, place an order, close an order, mutate trades or positions, or perform any live funding step.
