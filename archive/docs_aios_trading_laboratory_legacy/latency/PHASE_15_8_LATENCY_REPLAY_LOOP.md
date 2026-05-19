# Phase 15.8 Latency Replay Loop

Status: paper-only / local-file-only

## Purpose

Phase 15.8 reviews the paper runner output and replays the decision path in plain English.

Replay means reading the saved paper files again and checking whether the timing, regime, risk gate, paper decision, and scorecard still make sense together.

## Replay Chain

signal
-> latency
-> regime
-> risk gate
-> paper decision
-> scorecard

## What This Phase Checks

- stale signals
- delayed signals
- missing time fields
- invalid time formats
- clock skew
- paper regime result
- paper risk gate result
- paper decision result
- paper scorecard status

## Current Replay Finding

The current paper latency report has a negative signal age. This means the signal generated time is later than the validation time.

The replay should mark this as `CLOCK_SKEW_DETECTED` and `BLOCKED_FOR_REVIEW`.

## Safety Boundary

This phase cannot unlock live trading.

- Live execution: BLOCKED
- Broker: BLOCKED
- OANDA: BLOCKED
- API keys: BLOCKED
- Secrets: BLOCKED
- Real webhooks: BLOCKED
- Real orders: BLOCKED
- Live market data: BLOCKED

## Next Safe Action

Run `powershell -ExecutionPolicy Bypass -File automation/trading_lab/Test-AiOsTradingLabLatencyReplay.DRY_RUN.ps1`.

