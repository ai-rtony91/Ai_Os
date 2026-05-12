# Phase 14.13 - Market Regime Engine

Phase 14.13 adds the first paper-only market regime classification layer for Trading Lab. It does not trade, route, call brokers, or send webhooks. It labels the market environment so later paper decisions can understand whether a strategy is operating in the conditions it was designed for.

## Purpose

Most strategies are not universal. A strategy that performs well in a strong trend can fail in a range. A strategy that works in quiet conditions can break during volatility expansion.

The market regime engine gives AI_OS a simple local label before any paper route moves forward.

## Trending Markets

A trending market has directional movement with follow-through. In this regime, trend-following systems may have better paper evidence because price keeps moving in one direction long enough for a setup to develop.

Trend labels do not create buy or sell signals. They only describe the environment.

## Ranging Markets

A ranging market moves sideways between support and resistance zones. Trend-following systems often fail here because breakouts fade and directional signals become noisy.

Range labels help AI_OS block or reduce confidence for strategies that require continuation.

## Volatility Expansion

Volatility expansion means price movement is getting larger. This can create opportunity, but it can also create wider spreads, worse fills, and higher stop risk.

AI_OS tracks volatility expansion so paper routes can be reviewed with caution.

## Volatility Compression

Volatility compression means price movement is getting smaller. This can happen before a breakout, but it can also trap systems in low-quality chop.

Compression does not mean a trade should happen. It means the system should wait for more evidence.

## Liquidity Conditions

Liquidity affects whether paper assumptions are realistic. Thin liquidity can cause spread widening, slippage, and unstable movement.

The regime engine records liquidity state so poor market conditions can block paper review.

## News-Event Instability

News events can change price behavior quickly. During news instability, historical strategy behavior may stop working for a short period.

The market regime engine can mark news risk as elevated so AI_OS avoids treating unstable conditions as normal evidence.

## Why Strategies Fail Outside Their Intended Regime

Strategies are usually designed for a specific environment. When the market changes, the same indicator can produce a signal with very different quality.

Examples:

- trend strategy inside a sideways range
- breakout strategy during low liquidity
- mean reversion strategy during strong trend expansion
- low-latency strategy during delayed signal intake

The regime label helps AI_OS avoid forcing the wrong tool into the wrong market.

## Why Regime Filtering Matters More Than Indicators

Indicators describe price. Regime filtering describes whether the current market is suitable for the strategy.

An indicator can be technically correct and still produce a bad paper trade if the regime is wrong. Regime filtering protects the system from overtrading, noisy signals, and false confidence.

## Current Safety State

- Paper-only classification: enabled
- Live execution: blocked
- Broker connection: blocked
- External webhooks: blocked
- Internet calls: blocked

Phase 14.13 is a classification layer only. It does not enable execution.
