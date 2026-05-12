# Phase 23 Paper Signal Normalization

## Purpose

Phase 23 creates a local paper-only signal normalization layer for Trading Lab.

The goal is to make paper signals use one consistent shape before they reach:

- Phase 24 workstation display
- Phase 25 latency measurement
- Phase 26 paper replay
- Phase 27 journal and scorecard
- Phase 28 TV/TP paper handoff

## Workflow

1. Read a local mock paper signal reference.
2. Normalize signal identity, symbol, timeframe, direction, strategy, type, and confidence.
3. Validate required fields.
4. Mark missing fields and rejected reason when incomplete.
5. Keep risk gate in review until later paper-only validation passes.

## Required Fields

- normalized_signal_id
- source_signal_id
- source_platform
- received_by
- symbol
- timeframe
- direction
- strategy_name
- signal_type
- confidence
- payload_valid
- normalization_status
- missing_fields
- rejected_reason
- risk_gate_status
- live_execution
- broker
- real_order
- api_key_required

## Safety Boundary

Phase 23 is paper-only and local mock-data only.

Required states:

- live_execution: BLOCKED
- broker: BLOCKED
- real_order: BLOCKED
- api_key_required: false

No OANDA, broker, API key, secret, account connection, real webhook, live trading, real order, or autonomous execution path is approved.

## Dashboard Placement

Trading Lab only.

Display may appear inside Advanced Diagnostics or a workstation secondary panel. It must not appear on the AI_OS first screen and must not duplicate the Phase 24 workstation or Phase 28 handoff surfaces.

## Next Safe Action

Run the Phase 23 dry-run validator before using normalized paper signal data in later phases.
