> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS_V2 authority. Current operating authority is `AGENTS.md`; current V2 front-door/context authority is `README.md`; current source-of-truth mapping lives under `docs/governance/`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved V2 canonical document explicitly promotes them.

# AI_OS Broker Boundary Overview Draft

## Purpose

This draft defines the AI_OS broker boundary at a planning level. It is documentation only and does not create broker code, API clients, credentials, `.env` changes, live API calls, paper trading, live trading, broker orders, telemetry writers, persistence, dashboard code, or GitHub actions.

## Boundary Position

Broker work belongs in Stage 8 Broker/Execution. AI_OS is not approved for broker execution while Stage 6 telemetry/reporting and Stage 7 signal intelligence boundaries remain incomplete.

## Allowed Planning Scope

Allowed broker planning may include:

- static boundary descriptions
- blocked-action lists
- approval gates
- sandbox review requirements
- credential exclusion rules
- execution separation rules
- audit logging requirements

## Blocked Actions

The following remain blocked:

- broker API clients
- broker account connection
- broker credential access
- `.env` reads or writes
- order placement
- order routing
- webhook firing
- paper trading
- live trading
- strategy activation
- background broker services
- telemetry collection from broker systems

## Required Future Gates

Any future broker planning beyond placeholder docs requires:

- approved telemetry schema and privacy boundaries
- approved legal/compliance placeholders
- risk policy review
- explicit human approval
- sandbox-only design review
- rollback and audit plan

## Non-Approval Statement

This draft does not approve broker integration, OANDA integration, API clients, credential handling, paper trading, live trading, or execution behavior.
