# Phase 14.5 TradingView Alert Payload Mock

Status: DRY_RUN scaffold
Mode: paper-only / mock-only
Live execution: BLOCKED

## Purpose

Phase 14.5 defines a local TradingView-style alert payload fixture for the minimum paper bot loop.

The payload is a mock input only. It is not a real TradingView alert, login, API call, webhook, or route trigger.

## Required Fields

- symbol
- timeframe
- direction_intent
- alert_timestamp
- strategy_name
- strategy_metadata
- supertrend_preview_ref
- latency_ref
- phase_14_3_decision_ref
- scorecard_ref

## Safety

The fixture must remain paper-only. It must not include external account identifiers, webhook URLs, live order identifiers, broker fields, or real execution fields.

## Next Safe Action

Run `automation/trading_lab/Test-AiOsTradingLabPhase145TradingViewPayloadMock.DRY_RUN.ps1`.
