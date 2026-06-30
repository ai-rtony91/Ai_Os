# AIOS Forex Live Micro Repeatability Evidence Ledger V1

## Purpose

This lane creates a local-only repeatability ledger for the controlled live micro proof.
It uses existing redacted evidence snapshots and compares them across time without placing
or changing trades.

## Scope

- No broker API calls.
- No Bitwarden reads.
- No POST/PUT/PATCH/DELETE operations.
- No order creation, close, or modify operations.
- No money movement.
- No scheduler, daemon, webhook, or autonomous execution.

## Contract

The ledger reads one or more read-only state files, defaults to:

`Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EVIDENCE_REVIEW_V1_STATE.json`

and writes:

- `Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_REPEATABILITY_EVIDENCE_LEDGER_V1_STATE.json`
- `Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_REPEATABILITY_EVIDENCE_LEDGER_V1_REPORT.md`

## Evidence processing

For each supplied state file, the runner:

1. Loads and validates JSON.
2. Captures required booleans (trade flags, forbidden flags, runtime flags, money movement).
3. Aggregates P/L history and SL/TP evidence continuity:
   - `snapshot_count`
   - `pnl_values`
   - `profit_positive_count`
   - `profit_flat_count`
   - `profit_negative_count`
   - `sltp_complete_count`
   - `sltp_missing_count`
   - `sltp_latest_complete`
4. Computes evidence fingerprints for each snapshot and for observed SL/TP/trade values.
5. Classifies repeatability status.

## Classification

- `LIVE_MICRO_REPEATABILITY_INSUFFICIENT_SNAPSHOTS`
- `LIVE_MICRO_REPEATABILITY_OPEN_TRADE_STILL_NEGATIVE`
- `LIVE_MICRO_REPEATABILITY_OPEN_TRADE_FLAT`
- `LIVE_MICRO_REPEATABILITY_OPEN_TRADE_POSITIVE`
- `LIVE_MICRO_REPEATABILITY_SLTP_EVIDENCE_MISSING`
- `LIVE_MICRO_REPEATABILITY_FORBIDDEN_FLAG_DETECTED`
- `LIVE_MICRO_REPEATABILITY_MONEY_MOVEMENT_FLAG_DETECTED`
- `LIVE_MICRO_REPEATABILITY_LEDGER_READY`
- `LIVE_MICRO_REPEATABILITY_REPAIR_REQUIRED`

## Safety invariants

- Do not execute live or demo order endpoints.
- Do not call post/put/patch/delete order actions.
- Do not mutate positions/trades.
- Do not allow money movement.
- Do not start local schedulers, daemons, or webhooks.
- Preserve redaction policy: no raw tokens, raw account IDs, or raw sessions in outputs.

## Output expectations

State/STDOUT output includes:

- `module`
- `packet_id`
- `input`
- `result`
- `runtime_summary`

`input` includes snapshot paths, missing files, local-only guard rails, and safety booleans.
`runtime_summary` includes counts, latest P/L classification, readiness flags, and evidence fingerprints.

## Supervised transition

This lane is a bridge to supervised repeatability decisioning only.
It intentionally produces an evidence artifact for a human operator and does not
automate any execution decisions.
