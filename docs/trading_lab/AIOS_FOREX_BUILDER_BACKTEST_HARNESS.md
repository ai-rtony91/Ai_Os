# AIOS Forex Builder Backtest Harness

Packet: `PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS`

## Purpose

The backtest harness is a deterministic local scaffold for the forex-builder proof. It consumes local fixture candles and produces a `BacktestResult` schema record that can be reused by risk gates, dashboard state, evidence aggregation, and month-end readiness review.

It is research evidence only. It does not connect to a broker, fetch market data, place paper orders, place live orders, read credentials, start schedulers, or write reports by default.

## Local API

- `build_sample_backtest_fixture() -> MarketDataFixture`
- `run_local_backtest_harness(fixture, strategy_config, risk_config=None) -> BacktestResult`
- `backtest_harness_summary(result) -> dict`

## Rules

- Input fixtures must validate through `automation/forex_engine/schema_contracts.py`.
- `network_allowed` must remain `false`.
- `mode` must remain `PAPER_ONLY` or `LOCAL_ONLY`.
- Strategy and risk config must not request broker, live, credential, secret, order, webhook, scheduler, daemon, or network automation behavior.
- The result cannot grant live readiness.

## Acceptance

- The harness runs twice with the same fixture and returns the same result.
- Summary output states local fixtures only and no network.
- `tests/forex_engine/test_backtest_harness.py` validates deterministic behavior and safety boundaries.
