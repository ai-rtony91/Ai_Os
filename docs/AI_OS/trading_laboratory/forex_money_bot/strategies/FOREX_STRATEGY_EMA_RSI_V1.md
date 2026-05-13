# Forex Strategy EMA RSI V1

## Purpose

EMA RSI V1 is a paper-only strategy concept for AI_OS Forex Money Bot decision review. It does not place trades, connect to a broker, call a webhook, use API keys, or enable live execution.

## Strategy Idea

The strategy checks whether moving-average trend direction and RSI momentum agree before a paper-only signal can receive a higher confluence score.

## Inputs

- Pair from the local forex pair registry
- Timeframe
- EMA trend alignment
- RSI momentum confirmation
- Session filter
- Spread condition placeholder
- Volatility condition placeholder
- Regime tag
- Risk gate status

## Paper-Only Decision Role

This strategy can support ALLOW, REJECT, WAIT, LOW_CONFIDENCE, SESSION_BLOCK, or RISK_BLOCK decisions for paper review only.

Live execution remains BLOCKED.
