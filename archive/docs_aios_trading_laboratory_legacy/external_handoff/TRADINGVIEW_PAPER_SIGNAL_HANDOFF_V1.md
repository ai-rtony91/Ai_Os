# TradingView Paper Signal Handoff v1

Status: APPLY scaffold, paper-only

## Purpose

Create a local TradingView-style alert handoff record for AI_OS Trading Lab.

This scaffold tracks a mock alert through AI_OS validation, route preview, and paper simulation. It does not create a real webhook, broker route, OANDA connection, API key path, live execution path, or real order path.

## Workflow

1. TradingView-style paper alert is created.
2. AI_OS receives the local paper alert record.
3. AI_OS starts validation.
4. AI_OS completes validation.
5. AI_OS records a paper route preview time.
6. AI_OS records paper simulation time.
7. AI_OS calculates latency fields.
8. AI_OS marks stale signal status.
9. AI_OS records delay reason or blocked reason.

## Required Latency Fields

- latency_record_id
- signal_id
- source
- symbol
- timeframe
- alert_created_at
- alert_received_at
- validation_started_at
- validation_completed_at
- route_preview_at
- paper_trade_simulated_at
- alert_to_receive_ms
- receive_to_validation_ms
- validation_duration_ms
- validation_to_route_ms
- route_to_paper_sim_ms
- total_delay_ms
- stale_signal
- latency_status
- delay_reason
- blocked_reason

## Stale Signal Rules

- Missing timestamps keep the record in PENDING_VALIDATION.
- Negative step delays are CLOCK_SKEW_DETECTED and require a blocked reason.
- total_delay_ms under 300000 is PASS.
- total_delay_ms from 300000 through 899999 is DELAYED and requires a delay reason.
- total_delay_ms at or above 900000 is STALE, sets stale_signal to true, and requires a blocked reason.

## Safety Gates

Required blocked values:

- live_execution: BLOCKED
- broker: BLOCKED
- oanda: BLOCKED
- real_webhook: BLOCKED
- real_order: BLOCKED
- api_key_required: false

Latency status cannot unlock live trading, broker routing, OANDA, real webhooks, account connections, API keys, secrets, autonomous execution, or real orders.

## Dashboard Boundary

The mock-data fixture may support Trading Lab diagnostics only. This APPLY does not edit dashboard UI code or JavaScript.

## Next Safe Action

Run `automation/trading_lab/Test-AiOsTradingViewPaperSignalHandoffV1.DRY_RUN.ps1` and keep all execution paths blocked.
