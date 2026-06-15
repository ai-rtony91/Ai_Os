# AIOS Forex Builder Dashboard Contract

Packet: `PKT-AIOS-FOREX-BUILDER-DASHBOARD-CONTRACT`

## Purpose

The forex-builder dashboard contract turns local evidence into a compact operator-facing status block. It is compatible with the AIOS operator checkpoint style: short default output, full details only when explicitly requested by a caller.

No report file is written by default.

## Local API

- `build_forex_dashboard_state(...) -> DashboardState`
- `format_forex_dashboard_lines(state) -> list[str]`
- `dashboard_contract_summary() -> dict`

## Required Fields

The compact state must show:

- strategy
- fixture status
- backtest status
- walk-forward status
- risk gate status
- paper-forward state
- blocker
- SOS state
- next safe action

## Safety

The dashboard is status evidence only. It must not expose controls for broker integration, live trading, credentials, orders, webhooks, scheduler activation, daemon activation, queue mutation, approval mutation, staging, committing, pushing, or merging.
