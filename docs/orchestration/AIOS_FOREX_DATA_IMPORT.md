# AIOS Forex Data Import

This generated component is the fifth `forex-paper-bot` build step. It is a
paper/research-only historical data import and normalization helper for local
CSV-style rows.

Required row fields are `timestamp`, `pair`, `open`, `high`, `low`, and `close`.
Optional numeric fields are `volume`, `fast_ma`, `slow_ma`, and `momentum`.
Supported pairs are EURUSD, GBPUSD, and USDJPY.

The importer validates required fields, supported pairs, numeric OHLC values,
and basic OHLC consistency. It blocks live execution, broker orders,
credentials, API keys, real orders, and webhooks.

It performs no network access, broker access, credential access, live trading,
real order routing, or webhook execution.
