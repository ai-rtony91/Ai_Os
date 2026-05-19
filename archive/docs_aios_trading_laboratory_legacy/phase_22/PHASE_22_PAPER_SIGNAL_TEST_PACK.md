# Phase 22 Paper Signal Test Pack

## Purpose

Phase 22 adds a repeatable local signal review set for the Phase 21 paper signal intake.

Flow:

sample signal -> paper signal intake logic -> validation result -> paper route preview -> pass or reject reason

## Test Cases

1. valid long
2. valid short
3. missing field
4. stale signal
5. future clock skew
6. bad direction
7. low confidence
8. unsupported symbol
9. unsupported timeframe
10. duplicate signal

## Batch Gates

- confidence gate
- supported symbol gate
- supported timeframe gate
- duplicate signal gate

## Output Files

- PAPER_SIGNAL_TEST_PACK_LEDGER_001.json
- PAPER_SIGNAL_TEST_PACK_SCORECARD_001.json
- PAPER_SIGNAL_TEST_PACK_VALIDATION_REPORT_001.json

## Safety Boundary

- route_mode: PAPER_PREVIEW_ONLY
- live_execution_status: BLOCKED
- broker_status: BLOCKED
- oanda_status: BLOCKED
- api_key_status: BLOCKED
- secrets_status: BLOCKED
- real_webhook_status: BLOCKED
- real_order_status: BLOCKED

## Next Safe Action

Review rejected local paper signals and decide whether Phase 21 should permanently include the Phase 22 gates.
