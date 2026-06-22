# AIOS Forex Final Live Operator Bridge V1

## Objective

`AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1` defines the final offline arming surface for a governed single-live-micro-trade exception. It connects the existing Live Runtime Executor V1 and OANDA Live Runtime Connector V2 contracts without placing an order.

## Authority Boundary

General live trading remains blocked. Broker credentials, account identifiers, real orders, webhooks, schedulers, daemons, and uncontrolled automation remain blocked.

A single governed live micro-trade exception may exist only through `AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1` with explicit human approval, runtime-only credentials, one-order-only enforcement, micro-size enforcement, stop loss, take profit, max loss gate, daily stop gate, kill-switch state validation, sanitized evidence, and no credential or account persistence.

This bridge does not weaken `AGENTS.md`, `RISK_POLICY.md`, protected action gates, commit gates, push gates, or live execution approval rules.

## Runtime Behavior

- Builds sanitized bridge state.
- Validates the final live operator arm request.
- Builds an executor-compatible runtime execution plan.
- Builds a mobile operator payload for truth-field display.
- Classifies cleanup candidates supplied by the caller.
- Does not read `.env`.
- Does not read environment variables.
- Does not read or persist credentials.
- Does not persist account identifiers.
- Does not call the network.
- Does not place a real order.
- Does not start loops, retries, schedulers, daemons, or webhooks.

## Mobile Operator Surface

The dashboard panel is a display-only operator surface. It exposes mode, bridge status, account truth fields, order intent truth fields, risk gates, connector status, evidence freshness, blockers, and next safe action. It does not provide an execution button and does not authorize live execution.

The panel is designed to remain usable on narrow Samsung Galaxy Z Fold 6 screen widths by collapsing truth-field grids into two-column and one-column layouts.

## Cleanup Handling

Cleanup is classification-only in this version. No files are deleted, moved, renamed, archived, or promoted by the bridge.

