# AIOS Forex Strategy Rules

This generated component is the fourth `forex-paper-bot` build step. It is a
paper-only deterministic strategy signal evaluator for local review.

The strategy supports EURUSD, GBPUSD, and USDJPY. It accepts a candle or
indicator dictionary with `fast_ma`, `slow_ma`, and optional indicator nesting.
It emits `buy`, `sell`, or `hold` paper signals only:

- `buy` when `fast_ma > slow_ma` and momentum is positive
- `sell` when `fast_ma < slow_ma` and momentum is negative
- `hold` when data is insufficient or filters are not aligned

The component blocks live execution, broker order fields, credentials, API key
fields, real order fields, and real webhook fields. It does not connect to a
broker, call APIs, trade live, or route orders.
