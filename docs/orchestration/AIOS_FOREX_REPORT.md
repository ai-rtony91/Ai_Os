# AIOS Forex Report

This generated component is the sixth `forex-paper-bot` build step. It creates
a deterministic paper/research-only scorecard from backtest summary, ledger
summary, and strategy metadata.

The scorecard includes `trade_count`, `win_rate`, `total_pnl`, `risk_flags`, and
`paper_only: true`.

The component blocks live execution, broker orders, credentials, API keys, real
orders, webhooks, network fields, and file-output fields. It performs no file
writes and no network access.
