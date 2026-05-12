# Phase 20 TV/TP Paper Route Workflow

## Purpose

Phase 20 defines an AI_OS-owned external handoff workflow for a paper-only route preview.

The workflow uses external platform names as references only:

TradingView Signal Reference -> AI_OS Signal Intake -> Latency Check -> Clock Skew Check -> Regime Check -> Risk Gate -> Strategy Ranking -> Paper Route Preview -> TradersPost Paper Route Reference -> Paper Result Review -> Next Safe Action

## Boundary

This phase does not connect to external platforms. It does not collect credentials. It does not create live routes. It does not place orders.

Required status values:

- source_status: EXTERNAL_REFERENCE_ONLY
- target_platform: TRADERSPOST_REFERENCE
- route_mode: PAPER_PREVIEW_ONLY
- live_execution_status: BLOCKED
- broker_status: BLOCKED
- oanda_status: BLOCKED
- api_key_status: BLOCKED
- secrets_status: BLOCKED
- real_webhook_status: BLOCKED
- real_order_status: BLOCKED

## Workflow Steps

1. TradingView Signal Reference
2. AI_OS Signal Intake
3. Latency Check
4. Clock Skew Check
5. Regime Check
6. Risk Gate
7. Strategy Ranking
8. Paper Route Preview
9. TradersPost Paper Route Reference
10. Paper Result Review
11. Next Safe Action

## Review Rule

Any route preview must remain paper-only until a future approved boundary phase. Current readiness remains review-gated when clock skew, small sample size, or validation gaps exist.

## Next Safe Action

Validate the local contract and dashboard fixture, then keep dashboard display mock-data only until a separate APPLY request wires a panel.
