# Phase 14.1 - Paper Edge Validation Core

Status: paper-only / simulation-only

Live execution remains BLOCKED. This scaffold does not connect to brokers, OANDA, API keys, real orders, or live market data.

## Purpose

Create the first Trading Lab profitability validation layer for paper-only strategy review.

## Flow

Strategy Registry -> Signal Intake Ledger -> Regime Filter -> Risk Gate -> Paper Trade Simulation Ledger -> Profitability Scorecard

## Blocked Actions

- broker execution
- OANDA execution
- API keys
- real orders
- live market data dependency

## Paper Metrics

- win_rate
- average_win
- average_loss
- expectancy
- profit_factor
- max_drawdown
- trade_count
- confidence_score
- blocked_reason

## Draft Validation Thresholds

These thresholds are draft review targets only and are not approved for live trading.

- minimum_trade_count: 30 paper trades
- minimum_expectancy: above 0.00R
- minimum_profit_factor: 1.20
- maximum_drawdown: 10 percent paper equity drawdown
- minimum_confidence_score: 70
- risk_gate_status: pass_paper_review_only
- regime_filter_status: reviewed

## Traceability Rule

Every paper result must trace back to:

- strategy_id
- signal_id
- regime_id
- risk_gate_id
- paper_trade_id
- profitability_scorecard_id

## Next Safe Action

Fill one paper strategy registry entry, intake one mock signal, run regime and risk review, then record a simulated paper result.
