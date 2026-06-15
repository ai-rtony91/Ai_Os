# AIOS Forex Builder Local Fixture Catalog

## Purpose

The local fixture catalog provides deterministic in-memory Python fixtures for paper-only forex demos.

Current fixtures:

- `EURUSD_5M_TREND_SAMPLE`
- `EURUSD_5M_CHOP_SAMPLE`
- `EURUSD_5M_PULLBACK_SAMPLE`

## Boundary

Fixtures are local Python data only.

There are no file reads, CSV ingestion, network calls, broker connections, credentials, webhooks, scheduler activation, daemon activation, or report writes.

This catalog supports local simulation only. It is not broker paper trading and does not prove live readiness.

## Current Local API

- `build_deterministic_fixture_catalog()`
- `get_fixture_by_id(fixture_id)`
- `list_fixture_ids()`
- `fixture_catalog_summary()`

## Evidence Use

The fixtures validate through `automation/forex_engine/schema_contracts.py` and can feed local backtest, paper-forward, evidence bundle, dashboard, and readiness demos.

Stronger out-of-sample data and longer forward evidence remain required before any downstream readiness promotion.
