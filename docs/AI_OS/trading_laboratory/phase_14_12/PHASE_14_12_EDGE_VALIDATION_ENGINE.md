# Phase 14.12 - Edge Validation Engine

Phase 14.12 adds the first paper-only edge validation layer for Trading Lab. It does not execute trades. It scores whether a paper signal has enough quality to continue into review.

## Purpose

The edge validation engine asks a simple question before a paper route moves forward:

Does this setup have enough evidence to be worth reviewing?

The answer must come from local paper data only. A signal can be blocked even when the direction looks interesting, because direction alone is not an edge.

## Expectancy

Expectancy estimates whether a strategy has positive value over many paper trades. A setup with a few wins can still be weak if the average loss is too large or the win rate is too low.

Simple meaning:

expectancy = average expected result per trade

Positive expectancy means the paper pattern may be worth more study. Negative or unknown expectancy means AI_OS should block or delay the route until more evidence exists.

## Profit Factor

Profit factor compares total paper wins to total paper losses.

Simple meaning:

profit factor = gross paper profit / gross paper loss

A profit factor above 1.0 means paper winners are larger than paper losers. A weak profit factor means the setup may not survive spread, slippage, or latency.

## Session Filtering

Markets behave differently by session. A setup that works during one session may fail during another. Phase 14.12 tracks the session so AI_OS can later learn whether a signal is better during specific market hours.

Examples:

- London session
- New York session
- Asia session
- overlap periods
- low-liquidity periods

## Latency Decay

Signals lose value when they arrive late. A paper signal that was valid 30 seconds ago may no longer be useful if price has moved.

Latency decay means the edge score gets weaker as delay increases. Fast review protects signal quality. Slow review should reduce confidence or block the paper route.

## Volatility Filtering

Volatility changes risk. Low volatility can make a setup too slow or choppy. High volatility can make fills worse and stops easier to hit.

The edge validation layer tracks volatility state so AI_OS can block paper routes when the environment is not suitable for the strategy.

## Why Bad Trades Should Be Blocked

Bad trades consume attention, produce noisy scorecard data, and train the operator to accept weak signals. Blocking weak paper routes is part of building a better system.

AI_OS should prefer no paper trade over a low-quality paper trade.

## Why Overtrading Destroys Systems

Overtrading creates more decisions, more noise, more false confidence, and more operational friction. Even paper-only systems can become misleading if they accept too many low-quality setups.

The edge validation engine reduces overtrading by requiring:

- acceptable expectancy evidence
- acceptable confidence evidence
- session context
- latency quality
- volatility context
- spread context

## Current Safety State

- Paper-only scoring: enabled
- Live execution: blocked
- External routing: blocked
- Real orders: blocked
- Internet calls: blocked

Phase 14.12 is an evidence layer only. It does not connect to execution systems.
