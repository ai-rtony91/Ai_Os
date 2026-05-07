# AI_OS Dashboard Future API Database Boundary Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.17 - Dashboard Config + Data Adapter Foundation

## Purpose

Define the future boundary between the browser dashboard, local mock-data, a later API adapter, and any later database/backend.

## Required Architecture

```text
Dashboard UI -> local config / mock-data now -> API adapter later -> database/backend later
```

## Browser Dashboard Rule

The browser dashboard must not connect directly to a database. It must not contain database credentials, broker tokens, API keys, private keys, recovery keys, or production secrets.

## Current Stage

Current approved direction is local mock-data and local config only.

## Future API Adapter

A future API adapter may be planned later if separately approved. It must:

- expose only approved read-only status data at first
- keep secrets outside browser code
- avoid broker or live trading paths
- validate responses before dashboard display
- return UNKNOWN or ERROR states instead of hiding failures

## Future Database / Backend

Any database or backend integration must be server-side only and must require:

- separate DRY_RUN
- human APPLY approval
- secrets management review
- authentication and authorization review
- privacy/compliance review
- rollback plan

## Blocked

- Direct browser-to-database connections
- Database credentials in dashboard config
- External API calls during local mock-data stage
- Broker execution, order routing, or live trading data paths

