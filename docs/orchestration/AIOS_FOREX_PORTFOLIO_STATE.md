# AIOS Forex Portfolio State

`forex_portfolio_state.py` is a paper-only account state component for the Forex proof lane.

It consumes deterministic execution-ledger records and returns a dashboard/orchestration-friendly dictionary with paper-only balance and risk fields, with explicit, deterministic, deterministic guards.

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

Hardened account-state fields returned:

- `starting_balance`
- `cash_balance`
- `current_balance`
- `equity`
- `realized_pnl`
- `unrealized_pnl`
- `open_risk`
- `available_risk`
- `max_daily_loss`
- `daily_loss_used`
- `drawdown`
- `drawdown_percent`
- `trade_count`
- `session_count`
- `last_update_timestamp`
- `open_positions`
- `exposure_by_symbol`
- `next_trade_allowed`
- `next_trade_blocked_reason`
- `paper_only`
- `safety`
- `next_safe_action`

Hardening constraints:

- Preserve existing key names for existing consumers when practical.
- Reject negative `starting_balance` and negative `cash_balance`/`current_balance`.
- Reject negative `max_daily_loss`, negative `daily_loss_used`, and negative `open_risk` when provided.
- Reject invalid `session_count` and invalid `last_update_timestamp` types.
- Reject unsafe execution flags (live, broker, credential, network, webhook), and block unsafe states.
- `equity = current_balance + unrealized_pnl`.
- `drawdown` and `drawdown_percent` compare `starting_balance` against equity when the start is positive.
- `available_risk = max(0, max_daily_loss - daily_loss_used - open_risk)`.
