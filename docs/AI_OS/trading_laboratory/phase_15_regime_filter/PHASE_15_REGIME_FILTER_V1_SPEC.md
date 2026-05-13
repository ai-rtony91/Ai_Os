# Phase 15 Regime Filter Contract v1

Status: APPLY scaffold, paper-only

## Purpose

Phase 15 Regime Filter v1 classifies the local paper market environment before a signal can move toward paper route preview.

This is a filter contract only. It does not trade, route to brokers, call OANDA, use API keys, send real webhooks, place real orders, or enable live execution.

## Workflow

1. AI_OS receives a paper signal reference.
2. AI_OS records the regime check timestamp.
3. AI_OS classifies session, trend, volatility, liquidity, spread, and news risk states.
4. AI_OS derives market_condition.
5. AI_OS assigns regime_confidence.
6. AI_OS sets regime_status.
7. AI_OS sets paper_route_allowed for paper preview only.
8. AI_OS records blocked_reason when the regime is not suitable.

## Required Regime Fields

- regime_record_id
- signal_id
- symbol
- timeframe
- session
- trend_state
- volatility_state
- liquidity_state
- spread_state
- news_risk_state
- market_condition
- regime_confidence
- regime_status
- paper_route_allowed
- blocked_reason
- regime_checked_at

## Regime Status Rules

- PASS requires regime_confidence at or above 70 and no unsafe market state.
- REVIEW is used for partial, uncertain, or incomplete regime evidence.
- BLOCKED is required when confidence is below 40 or when an unsafe market state is present.
- UNKNOWN is used when required evidence is missing.

Unsafe market states include high-impact news risk, severe liquidity warning, severe spread widening, and unstable regime transition.

## Paper Route Rules

- paper_route_allowed can be true only when regime_status is PASS.
- paper_route_allowed means paper route preview only.
- paper_route_allowed cannot enable live execution.
- REVIEW, BLOCKED, and UNKNOWN must keep paper_route_allowed false.
- blocked_reason is required whenever paper_route_allowed is false.

## Safety Gates

Required blocked values:

- live_execution_status: BLOCKED
- broker_status: BLOCKED
- oanda_status: BLOCKED
- api_key_status: BLOCKED
- real_webhook_status: BLOCKED
- real_order_status: BLOCKED

## Dashboard Boundary

This scaffold adds mock data only. It does not edit dashboard UI, JavaScript, broker logic, webhook logic, or execution code.

## Next Safe Action

Run `automation/trading_lab/Test-AiOsPhase15RegimeFilterV1.DRY_RUN.ps1` before any paper route preview consumes this contract.
