# AIOS Forex Extended Evidence Campaign V1 Stop Rule

Stop immediately when any of the following occurs:

- ledger missing or invalid;
- accepted market-demo evidence is older than 14 days;
- trade-level PnL or drawdown evidence is incomplete;
- any accepted record enables live trading, live order execution, money movement, bank access, or live-capital authority;
- expectancy is not positive;
- profit factor is below the active tier threshold;
- drawdown exceeds the active tier threshold;
- evidence is fixture, mock, synthetic, duplicated, or backdated.

The campaign may report progress but may not place orders, read credentials, append evidence automatically, or authorize live trading.
