# AIOS Forex Builder Data Schemas

## Purpose

This document defines the local data schema layer for the AIOS forex-builder proof. The layer represents market fixtures, strategy signals, order-intent records, backtest outputs, walk-forward evidence, paper ledger records, risk-gate results, dashboard state, and daily edge reports without any broker, live, network, or credential path.

These schemas are contracts for local research evidence. They do not execute trades.

## Protected Boundaries

- No broker integration.
- No OANDA/live exchange integration.
- No live orders.
- No paper order execution unless separately approved later.
- No credentials/secrets/env reads/writes.
- No webhooks.
- No scheduler/daemon execution.
- No real-money trading.
- No account mutation.
- No network market automation.

## Mode Rules

- `PAPER_ONLY` means local research evidence only.
- `LOCAL_ONLY` means local fixture representation only.
- `INTENT_ONLY` means an order-like decision record that cannot execute.
- `SIMULATED_ONLY` means ledger evidence from a simulator, not a broker or paper order route.
- `live_ready` must always be `false`.
- `execution_allowed` must always be `false`.
- `broker_order_id` must always be empty.
- `network_allowed` must always be `false`.
- `live_order` must always be `false`.

## MarketDataFixture

Fields:

- `fixture_id`
- `symbol`
- `timeframe`
- `source`
- `candles`
- `mode = LOCAL_ONLY`
- `network_allowed = false`

Rules:

- Candles must be local fixture candles.
- Network market automation is forbidden.
- The fixture must not imply a broker feed.

## Candle

Fields:

- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume` optional
- `source = local fixture`

Rules:

- `high >= low`
- `open` and `close` must be inside `high` and `low`.
- Missing OHLC values are invalid.

## StrategySignal

Fields:

- `signal_id`
- `strategy_id`
- `symbol`
- `timeframe`
- `timestamp`
- `direction`: `BUY`, `SELL`, `HOLD`, or `NO_TRADE`
- `confidence`
- `reason`
- `mode = PAPER_ONLY`

Rules:

- Confidence must stay between `0` and `1`.
- Signals are research evidence only.
- `NO_TRADE` reasons should be explicit when no entry is permitted.

## OrderIntent

Fields:

- `intent_id`
- `signal_id`
- `symbol`
- `direction`
- `requested_units`
- `entry_reference_price`
- `stop_loss_reference_price` optional
- `take_profit_reference_price` optional
- `status = INTENT_ONLY`
- `broker_order_id = None`
- `execution_allowed = false`

Rules:

- This is an intent record, not an order.
- It must not route to broker, exchange, webhook, scheduler, daemon, or execution code.
- It must not create paper orders unless a future packet separately approves a simulator.

## BacktestTrade

Fields:

- `trade_id`
- `symbol`
- `direction`
- `entry_time`
- `exit_time`
- `entry_price`
- `exit_price`
- `units`
- `pnl_usd`
- `r_multiple`
- `mode = PAPER_ONLY`

Rules:

- A trade is a backtest record only.
- It is not a live trade, paper order, or account mutation.

## BacktestResult

Fields:

- `result_id`
- `strategy_id`
- `fixture_id`
- `total_trades`
- `expectancy_r`
- `profit_factor`
- `max_drawdown_pct`
- `trades`
- `mode = PAPER_ONLY`

Rules:

- `total_trades` must match the trade list length.
- Results are research evidence and cannot grant live readiness.

## WalkForwardWindow

Fields:

- `window_id`
- `train_start`
- `train_end`
- `test_start`
- `test_end`
- `result`
- `classification`

Rules:

- Classification must be `FAIL`, `WATCHLIST`, or `PAPER_FORWARD_READY`.
- Window results remain local and paper-only.

## WalkForwardSummary

Fields:

- `summary_id`
- `strategy_id`
- `windows`
- `consistent_windows_pct`
- `classification`
- `blockers`

Rules:

- Consistency must be measured across sequential windows.
- `PAPER_FORWARD_READY` is not live-ready.
- Blockers must remain visible.

## RiskGateResult

Fields:

- `gate_id`
- `classification`: `FAIL`, `WATCHLIST`, or `PAPER_FORWARD_READY`
- `live_ready = false`
- `blockers`
- `next_safe_action`

Rules:

- `live_ready` is always false.
- Any future live-readiness discussion requires a separate protected approval path.

## PaperLedgerEntry

Fields:

- `ledger_id`
- `timestamp`
- `intent_id`
- `simulated_fill_price` optional
- `simulated_pnl_usd` optional
- `status = SIMULATED_ONLY`
- `broker_order_id = None`
- `live_order = false`

Rules:

- This schema is for simulator evidence only.
- It cannot represent a broker order or live order.

## DashboardState

Fields:

- `current_phase`
- `selected_strategy`
- `data_fixture_status`
- `backtest_status`
- `walk_forward_status`
- `risk_gate_status`
- `paper_permission_state`
- `live_permission_state`
- `current_blocker`
- `sos_required`
- `next_safe_action`

Rules:

- Dashboard state must show blocked or unavailable permissions explicitly.
- `live_permission_state` must not grant live readiness.
- SOS state is reporting only.

## DailyEdgeReport

Fields:

- `report_id`
- `timestamp`
- `strategy_id`
- `symbols`
- `timeframe`
- `data_source`
- `total_trades`
- `expectancy_r`
- `max_drawdown_pct`
- `profit_factor`
- `classification`
- `blockers`
- `next_safe_action`
- `mode = PAPER_ONLY`

Rules:

- Classification can be `REJECTED`, `NEEDS_MORE_DATA`, `CANDIDATE`, or `PAPER_FORWARD_READY`.
- `PAPER_FORWARD_READY` is still not live-ready.
- Daily reports are evidence summaries, not trading instructions.

## Local Implementation

The matching pure Python contract module is:

```text
automation/forex_engine/schema_contracts.py
```

The focused validator tests are:

```text
tests/forex_engine/test_schema_contracts.py
```

This schema layer connects cleanly to existing paper-only forex engine concepts such as indicators, strategy signals, conservative costs, metrics, risk gates, daily edge reporting, and walk-forward evaluation. It does not rewrite those modules and does not add execution behavior.
