# AIOS Forex Backtest

This generated component is the second `forex-paper-bot` build step. It is a
deterministic, paper-only backtest helper that consumes local candle-like
dictionaries, calls the local Forex paper bot decision function, and returns a
summary for review.

The backtest summary includes `trades_considered`, `trades_allowed`,
`trades_blocked`, `ending_balance`, and `paper_only: true`.

The component blocks broker fields, credential fields, live execution flags,
real order fields, and real webhook fields. It does not mutate queues, approvals,
workers, runtime, schedulers, daemons, Git state, broker state, credentials, or
live trading paths.
