# AIOS Forex Portfolio State

`forex_portfolio_state.py` is a paper-only account state component for the Forex proof lane.

It consumes deterministic execution-ledger records and returns a dashboard/orchestration-friendly dictionary with cash balance, open positions, realized PnL, safe-zero unrealized PnL when market prices are absent, trade count, daily loss used, exposure by symbol, and next-trade gate status.

Safety boundary:

- No broker execution.
- No credentials.
- No live trading.
- No real orders.
- No real webhooks.
- No network access.
- No scheduler, daemon, worker dispatch, queue mutation, or approval mutation.

Public function:

```python
build_portfolio_state(
    ledger_records,
    account_snapshot=None,
    market_prices=None,
    limits=None,
    **safety_flags,
)
```

Supported pairs are `EURUSD`, `GBPUSD`, and `USDJPY`. Supported paper actions are `buy`, `sell`, and `hold`.
