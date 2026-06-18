# AIOS Opportunity Explanation Dashboard Slice V1

## Status

Status: IMPLEMENTED_READ_ONLY_VERTICAL_SLICE_UPDATE

Zone: DASHBOARD

Human Owner: Anthony Meza

## Files Changed

- `apps/dashboard/mock-data/aios-minimal-operator-dashboard-v1.example.json`
- `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- `apps/dashboard/src/MinimalOperatorDashboard.css`
- `docs/dashboard/AIOS_OPPORTUNITY_EXPLANATION_DASHBOARD_SLICE_V1.md`

## What The Explanation Panel Displays

The existing Minimal Operator Dashboard now includes an Opportunity Explanation panel for the selected watchlist pair.

The panel displays:

- selected pair
- data source label
- opportunity score
- confidence score
- why AIOS ranked the pair
- bullish factors
- bearish/risk factors
- Supertrend status
- volatility context
- session context
- spread/slippage status
- P/L readiness
- exit readiness
- safe/blocked decision
- block reason
- next safe action

## Data Labeling Behavior

The opportunity explanation uses structured fixture fields from `apps/dashboard/mock-data/aios-minimal-operator-dashboard-v1.example.json`.

Each pair explanation includes:

- `dataSourceLabel`
- `dataSourceType`
- `liveTradingAllowedFromThisData`
- `rankingReason`
- `bullishFactors`
- `riskFactors`
- `spreadSlippageStatus`
- `plReadiness`
- `exitReadiness`
- `safeDecision`
- `blockReason`
- `nextSafeAction`

All market-looking values remain labeled `FIXTURE_NOT_LIVE`. No fixture data is labeled live.

## Fixture And Read-Only Limits

This slice is read-only.

It does not:

- call broker APIs
- call live data APIs
- read secrets
- print environment variables
- place trades
- wire live BUY/SELL actions
- mutate runtime state
- display account IDs
- display raw broker payloads

The only interaction is local selected-pair state for watchlist-to-chart handoff.

## Validation Run

Required validation for this packet:

- `npm run build --prefix apps/dashboard`
- `git diff --check`
- `git status --short --branch`

## Next Packet Recommendation

Recommended next packet:

- `AIOS-DASHBOARD-DATA-LABEL-ENFORCEMENT-V1`

This should enforce the Live Data Source Gate labels at the dashboard component boundary before any live, delayed, demo, or broker-permitted market data adapter is introduced.
