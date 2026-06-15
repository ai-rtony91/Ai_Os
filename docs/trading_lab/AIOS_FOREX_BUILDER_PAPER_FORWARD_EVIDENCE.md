# AIOS Forex Builder Paper-Forward Evidence

## Purpose

This document describes the local paper-forward evidence layer for the forex builder.

The evidence layer combines:

- deterministic local fixture data.
- local backtest result.
- local walk-forward summary.
- local paper-forward simulated ledger.
- risk gate result.
- evidence classification.
- compact dashboard state.
- month-end readiness review.

## Boundary

This is local simulation only.

This is not broker paper trading. It does not place broker paper orders, call OANDA, use credentials, read `.env`, call webhooks, activate a scheduler, start a daemon, or create real orders.

This does not prove live readiness. Stronger out-of-sample and forward evidence is required before any downstream promotion discussion.

Live readiness remains a protected downstream gate requiring separate approval, validators, and explicit safety review.

## Current Local API

- `build_local_evidence_bundle(fixture_id="EURUSD_5M_PULLBACK_SAMPLE")`
- `evidence_bundle_summary(bundle)`
- `classify_local_evidence_bundle(bundle)`
- `run_paper_forward_demo_bundle(fixture_id="EURUSD_5M_PULLBACK_SAMPLE")`

## Allowed Classifications

- `FAIL`
- `WATCHLIST`
- `PAPER_FORWARD_READY`

The local evidence layer must never output `LIVE_READY`.

## Next Safe Action

Use the demo commands in `AIOS_FOREX_BUILDER_READINESS_DEMO_COMMANDS.md` and treat the output as local evidence only.
