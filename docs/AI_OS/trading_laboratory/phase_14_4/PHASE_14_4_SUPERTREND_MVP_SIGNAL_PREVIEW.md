# Phase 14.4 SuperTrend MVP Signal Preview

Status: APPLY scaffold
Mode: paper-only / simulation-only
Live execution: BLOCKED

## Purpose

This file defines the Phase 14.4 SuperTrend MVP signal preview.

SuperTrend is trend permission only. It is not a buy/sell trigger, not a route trigger, and not an execution signal.

## Allowed Output

The preview may return only one of:

- bullish
- bearish
- neutral
- blocked

## Paper-Only Role

SuperTrend can help AI_OS decide whether the current paper signal context has trend permission for review.

It must not:

- place orders
- call brokers
- call OANDA
- require API keys
- send real webhooks
- enable live trading
- override the Phase 14.3 decision engine

## Required Connections

The preview must reference:

- signal intake
- latency status
- Phase 14.3 decision engine
- scorecard

## Compression Rule

The preview should be a compact operator signal:

`symbol -> direction -> SuperTrend permission -> latency -> decision engine -> scorecard`

It should not add dashboard clutter, second decision engines, or duplicated safety walls.

## Safety Boundary

Live execution remains BLOCKED. Broker, OANDA, API keys, real webhooks, real orders, and automatic route execution remain BLOCKED.

## Next Safe Action

Run `automation/trading_lab/Test-AiOsTradingLabPhase144SuperTrendPreview.DRY_RUN.ps1` and review the JSON preview before any future APPLY.
