# AIOS Forex OANDA Demo Packet 12F Owner Read Helper Required Fields Completion V1 Report

- packet_id: AIOS-FOREX-OANDA-DEMO-PACKET-12F-OWNER-READ-HELPER-REQUIRED-FIELDS-COMPLETION-V2
- mode: APPLY
- lane: forex-oanda-demo-owner-read-helper-required-fields-completion
- worktree: C:\Dev\Ai.Os
- branch: feature/forex-oanda-demo-packet-12f-owner-read-helper-required-fields-completion-v1

## Summary

Packet 12F updated the owner-run sanitized broker read output generator so the Packet 12D safe owner-read helper can produce the required sanitized JSON artifact when the read succeeds and the helper supplies safe monitor/PL evidence.

## Root Cause

Packet 12D blocked with `OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS` because the generator only copied several helper fields by exact canonical key during the monitor/PL merge. Safe helper data could arrive under monitor/PL aliases such as `currentUnits`, `openTradePrice`, `realizedPL`, `trueUnrealizedPL`, `current_bucket_result`, `pl_result_bucket`, and `lastTransactionTime`; those values were not consistently normalized into the required sanitized output fields.

The missing Packet 12D fields were:

- side
- units
- entry_price
- realized_pl
- unrealized_pl
- monitor_bucket
- result_bucket
- broker_evidence_status
- evidence_timestamp_utc

## Changes

- Expanded safe alias handling for owner-read monitor/PL output fields.
- Updated the monitor/PL merge path to use the alias resolver instead of exact-key reads.
- Added deterministic side derivation from signed units only when units are present and nonzero.
- Added deterministic broker evidence status completion only when `broker_read_performed` is true and every other required sanitized field is present.
- Added safe nested helper source normalization for known monitor/PL helper buckets.
- Added targeted deterministic tests using injected owner-read/helper output only.

## Safety

- No broker command was run.
- No owner-read live command was run.
- No network call was added to tests.
- No order, close, mutation, transfer, withdrawal, live trade, secret write, or raw payload persistence behavior was added.
- JSON writing remains gated by complete required sanitized fields and Packet 12B capture readiness.
- True market fields such as instrument, units, entry price, realized PL, and unrealized PL are not invented. If they are absent, output remains blocked.

## Validation

- `python -m pytest tests/forex_engine/test_oanda_demo_owner_run_sanitized_broker_read_output_generator_v1.py -q`
  - result: PASS, 32 passed
- `python -m py_compile automation/forex_engine/oanda_demo_owner_run_sanitized_broker_read_output_generator_v1.py`
  - result: PASS

## Next Safe Action

Run Packet 12D owner-read command only after Anthony approves the broker read. If it succeeds, rerun Packet 12B and Packet 11 against `Reports/forex_delivery/oanda_demo_owner_run_sanitized_broker_read_output_v1.json`.
