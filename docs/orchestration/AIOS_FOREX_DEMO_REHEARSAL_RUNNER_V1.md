# AIOS_FOREX_DEMO_REHEARSAL_RUNNER_V1

## What This Is

This is a safe paper/demo-review rehearsal runner.

It produces an in-memory evidence bundle from fixture or sample inputs. It produces evidence, not trades.

## What It Does

The runner can:

- normalize a market snapshot
- generate strategy candidates
- build a multi-trade queue
- create order preview evidence
- create paper fill evidence
- summarize lifecycle and balance state
- build an evidence ledger summary
- replay session evidence
- return blockers and next action

## What It Does Not Do

It does not:

- call a broker
- use credentials
- read account IDs
- submit orders
- authorize live trading
- create a scheduler, daemon, or webhook
- write runtime files

## Safety Output

Every bundle reports:

```text
live_trading_allowed = false
broker_submit_allowed = false
credentials_used = false
account_id_used = false
network_calls = false
live_order_submitted = false
runtime_file_written = false
```

## Next Safe Objective

Review a generated rehearsal bundle.

The next action is evidence review, not live trading.

