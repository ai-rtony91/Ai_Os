# Forex Strategy Trend Pullback V1

## Purpose

Trend Pullback V1 is a paper-only strategy concept for reviewing a pullback in the direction of a broader trend.

It is not a live trading strategy. It has no broker, OANDA, webhook, API key, external request, or live order path.

## Strategy Idea

The strategy checks trend strength, pullback quality, RSI confirmation, session fit, and risk gate status before assigning a paper-only decision state.

## Inputs

- Pair from the local forex pair registry
- Timeframe
- EMA trend alignment
- RSI momentum confirmation
- Trend strength
- Session filter
- Volatility condition placeholder
- Risk condition

## Paper-Only Decision Role

The strategy supports local confluence scoring only. Live execution remains BLOCKED.
