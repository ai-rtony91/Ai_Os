# Phase 15.9 Trading Lab Strategy Ranking

## Purpose

Phase 15.9 adds a paper-only strategy ranking layer for the Trading Lab.

It reviews the Phase 15.4 paper runner scorecard together with the Phase 15.8 replay result and produces a local ranking artifact for dashboard display and later review.

## Current Result

Status: BLOCKED_REPLAY_REVIEW

Reason:
- The current paper sample size is 1 trade.
- The replay result includes CLOCK_SKEW_DETECTED.
- The latency value is negative and must be reviewed before ranking can become trusted.

## Paper-Only Boundary

- live_execution_status: BLOCKED
- broker_status: BLOCKED
- oanda_status: BLOCKED
- api_key_status: BLOCKED
- secrets_status: BLOCKED
- real_webhook_status: BLOCKED
- real_order_status: BLOCKED

## Ranking Inputs

- Paper scorecard: apps/trading_lab/trading_lab/results/paper_runner/PAPER_SCORECARD_001.json
- Replay result: apps/trading_lab/trading_lab/results/paper_runner/PAPER_REPLAY_RESULT_001.json
- Risk gate result: apps/trading_lab/trading_lab/results/paper_runner/PAPER_RISK_GATE_RESULT_001.json

## Ranking Behavior

The strategy ranking must remain in REVIEW or BLOCKED_REPLAY_REVIEW until:
- Clock skew is resolved.
- Latency is non-negative and explainable.
- More paper samples exist.
- Risk gate pass rate can be evaluated across more than one sample.

## Next Safe Action

Review fixture timestamps, rerun latency replay, then collect more local paper-only samples before changing rank status.
