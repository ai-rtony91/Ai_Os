# TradersPost Paper Route Preview v1

## Purpose

This scaffold defines a paper-only TradersPost-style route preview inside AI_OS Trading Lab.

It connects a TradingView-style alert reference to AI_OS validation, latency review, risk gate review, and a local paper route preview. It does not create a real TradersPost webhook, broker route, OANDA connection, API key path, real order path, or live execution path.

## Paper-Only Workflow

1. TradingView-style alert enters AI_OS as a local paper signal reference.
2. AI_OS validates required signal fields before route preview.
3. AI_OS measures latency when local timestamps exist, otherwise latency remains Pending validation.
4. AI_OS checks the risk gate and keeps the route in review or blocked status.
5. AI_OS creates a paper route preview for operator review.
6. AI_OS blocks live execution.
7. Future TradersPost handoff remains placeholder-only until a separate approved live safety process exists.

## Required Route Preview Fields

- route_id
- source_signal_id
- source
- target
- symbol
- timeframe
- direction_intent
- paper_only
- risk_gate_status
- latency_status
- route_preview_created_at
- simulated_destination
- live_execution_blocked
- blocked_reason
- approval_required_before_live

## Required Blocked States

- paper_only: true
- live_execution_blocked: true
- approval_required_before_live: true
- simulated_destination: PAPER_ROUTE_PREVIEW_ONLY

## Blocked Capabilities

- No real TradersPost webhook
- No broker
- No OANDA
- No API keys
- credentials
- account connection
- No real orders
- No live execution
- autonomous execution

## Validation

Run the DRY_RUN validator before using this scaffold in reports, replay, scorecards, or dashboard mock-data review:

```powershell
powershell -ExecutionPolicy Bypass -File .\automation\trading_lab\Test-AiOsTradersPostPaperRoutePreviewV1.DRY_RUN.ps1
```

## Next Safe Action

Keep this scaffold paper-only and review the local route preview fields before any future APPLY expansion.
