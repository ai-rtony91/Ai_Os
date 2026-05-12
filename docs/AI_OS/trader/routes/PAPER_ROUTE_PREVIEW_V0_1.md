# Paper Route Preview V0.1

## Purpose

This document describes the AIOS trader paper route preview layer. It converts a mock alert payload into a local route preview decision.

## Route Preview Behavior

- Generates a local route identifier.
- Preserves symbol, timeframe, permission, signal, and the original payload.
- Always returns `route_status` as `PAPER_PREVIEW_ONLY`.
- Always returns `paper_only` as `true`.
- Always returns `live_execution_status` as `BLOCKED`.
- Always returns `execution_allowed` as `false`.

## Actions

- `PAPER_BUY_PREVIEW`: bullish permission with BUY signal.
- `PAPER_SELL_PREVIEW`: bearish permission with SELL signal.
- `NO_TRADE`: HOLD signal.
- `BLOCKED`: blocked permission or mismatched permission and signal.

## Safety Rules

- Paper preview only.
- No network calls.
- No credential handling.
- No external routing.
- No order placement.
- No live execution path.

## Validation Command

```powershell
python -m pytest tests/trader/test_mock_alert_payload_v01.py tests/trader/test_paper_route_preview_v01.py
```

This route preview is paper-only. It does not execute trades.
