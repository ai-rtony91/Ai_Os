# AIOS Forex Trade Latency Baseline Reporter V1 Report

## Packet

- packet_id: AIOS-FOREX-TRADE-LATENCY-BASELINE-REPORTER-LOCAL-APPLY-V1
- mode: LOCAL_APPLY
- lane: forex-trade-latency-baseline-reporter

## Files Created Or Changed

- `automation/forex_engine/trade_latency_baseline_reporter_v1.py`
- `tests/forex_engine/test_trade_latency_baseline_reporter_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_TRADE_LATENCY_BASELINE_REPORTER_V1_REPORT.md`

## What This Does For Anthony Up Front

This reporter makes timing visible before another trade is approved. It shows where time is being lost, reduces guessing after a demo loss, gives one plain continue/stop answer for timing evidence, protects Anthony from approving another trade when timing evidence is missing, and helps separate bad timing from bad strategy.

## Required Timestamps

- `quote_received_utc`
- `signal_generated_utc`
- `preview_started_utc`
- `preview_completed_utc`
- `risk_gate_started_utc`
- `risk_gate_completed_utc`
- `owner_approval_utc`
- `order_submit_started_utc`
- `order_filled_utc`
- `monitor_started_utc`
- `pl_classified_utc`
- `audit_written_utc`

## Required Trade Context

- `instrument`
- `direction`
- `strategy_name`
- `candidate_id`
- `order_fill_transaction_id`
- `pl_capture_classification`
- `profit_claimed`

## Latency Segments

- `quote_to_signal_ms`
- `signal_to_preview_ms`
- `preview_duration_ms`
- `preview_to_risk_gate_ms`
- `risk_gate_duration_ms`
- `risk_gate_to_approval_ms`
- `approval_to_submit_ms`
- `submit_to_fill_ms`
- `fill_to_monitor_ms`
- `monitor_to_pl_classification_ms`
- `pl_classification_to_audit_ms`
- `total_trade_cycle_ms`

## Decisions

- `BLOCK_LATENCY_MISSING_TIMESTAMPS`
- `BLOCK_LATENCY_SLOW_SEGMENT`
- `BLOCK_LATENCY_INVALID_EVIDENCE`
- `LATENCY_READY_FOR_REVIEW`

`LATENCY_READY_FOR_REVIEW` means the local timing evidence is complete and within configured limits. It does not approve, place, close, cancel, replace, or mutate a trade.

## Safety Boundary

- local-only: yes
- broker calls: blocked
- credential access: blocked
- `.env` access: blocked
- order placement: blocked
- order close/cancel/replace: blocked
- live endpoint: blocked
- scheduler, daemon, webhook, external service: blocked
- current time: not used
- repo mutation outside the three approved files: blocked
- commit, push, PR, merge: blocked

## Validator Commands

```powershell
python -m pytest tests/forex_engine/test_trade_latency_baseline_reporter_v1.py -q
python -m py_compile automation/forex_engine/trade_latency_baseline_reporter_v1.py tests/forex_engine/test_trade_latency_baseline_reporter_v1.py
```

## Stop Point

Stop after local files are created or changed and validators are attempted. Do not stage, commit, push, create a PR, merge, call brokers, use credentials, or place trades.

## Next Safe Action

Review the local reporter output against a trade evidence dictionary before any future demo-order approval discussion.
