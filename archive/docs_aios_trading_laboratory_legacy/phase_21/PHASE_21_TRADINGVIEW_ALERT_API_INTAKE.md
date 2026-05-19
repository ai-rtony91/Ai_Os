# Phase 21 TradingView Alert API Intake

## Purpose

Phase 21 creates a local AI_OS paper signal intake for TradingView-style alert references.

Endpoint:

`POST /paper-signal`

This endpoint is local and paper-only. It accepts a reference payload, validates it, and creates a paper route preview. It does not connect to external accounts or execution systems.

## Required Request Fields

- symbol
- timeframe
- direction
- strategy_id
- confidence
- alert_time
- source

## Validation

The intake rejects:

- missing required fields
- stale signals
- clock skew or future timestamp drift
- unsupported direction values

## Outputs

- `paper_signal_intake_ledger`
- `validation_result`
- `paper_route_preview`

## Safety Boundary

- route_mode: PAPER_PREVIEW_ONLY
- live_execution_status: BLOCKED
- broker_status: BLOCKED
- oanda_status: BLOCKED
- api_key_status: BLOCKED
- secrets_status: BLOCKED
- real_webhook_status: BLOCKED
- real_order_status: BLOCKED

## UI Boundary

Use AI_OS-owned labels only. Do not imitate external platform screens, layouts, logos, or visual identity.

## Next Safe Action

Run the Phase 21 dry-run validator and keep dashboard wiring as a separate approval.
