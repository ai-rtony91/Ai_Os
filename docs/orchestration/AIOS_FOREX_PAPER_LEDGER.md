# AIOS Forex Paper Ledger

This generated component is the third `forex-paper-bot` build step. It records
paper-only Forex trade outcomes for local review and does not create broker
orders, credential access, live execution, real orders, or real webhooks.

The ledger records pair, direction, entry, stop, target, position size,
deterministic result pips, paper PnL, and timestamp. The summary reports
`trade_count`, `winning_trades`, `losing_trades`, `total_pnl`, and
`paper_only: true`.

Unsupported pairs and unsafe live/broker/credential/order fields are blocked.
