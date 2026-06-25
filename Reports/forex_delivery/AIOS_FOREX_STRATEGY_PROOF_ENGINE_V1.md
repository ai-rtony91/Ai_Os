# AIOS Forex Strategy Proof Engine V1

## What It Does
Strategy Proof Engine V1 ranks ten local-only Forex strategy seeds with deterministic sample evidence. It includes Supertrend, EMA crossover, VWAP bias, Donchian breakout, ATR trend filter, ADX trend filter, RSI mean reversion, MACD confirmation, market structure break, and multi-timeframe alignment.

It does not claim guaranteed profit. It does not place trades, call brokers, use credentials, approve real money, approve compounding, or move money.

## Top Strategy
- top_strategy: supertrend.
- top_expectancy: 0.4833.
- top_profit_factor: 1.82.
- recommendation: PROMOTE_TO_STRATEGY_PROOF_REVIEW_ONLY.

## Supertrend Status
- status: SUPER_TREND_PROOF_REVIEW_READY.
- rank: 1.
- strategy proof review: ready for operator proof review only.
- 22/6 operation: not approved.

## Best Profit Candidate
Supertrend is the strongest candidate in the mixed deterministic sample. It has the highest combined proof ranking and the highest expectancy in the sample.

## Weak Strategies
- ATR trend filter needs out-of-sample proof.
- ADX trend filter needs out-of-sample proof and more market-regime coverage.
- EMA crossover needs stronger profit factor, out-of-sample proof, and slippage proof.
- VWAP bias needs stronger profit factor, walk-forward proof, out-of-sample proof, and market-regime coverage.
- MACD confirmation needs sample depth, stronger profit factor, loss-control repair, walk-forward proof, out-of-sample proof, market-regime coverage, and slippage proof.
- RSI mean reversion is rejected for now because expectancy is not positive and proof is weak.

## What Happens Next
Prepare operator proof review for Supertrend and collect missing 22/6 operation evidence before any readiness promotion.

## What Remains Blocked
- demo_trade_allowed: false.
- broker_action_allowed: false.
- real_money_allowed: false.
- compounding_allowed: false.
- bank_movement_allowed: false.
- live_trading_allowed: false.
