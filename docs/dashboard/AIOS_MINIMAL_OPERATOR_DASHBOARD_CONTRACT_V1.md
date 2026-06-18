# AIOS Minimal Operator Dashboard Contract V1

## Status

Status: DESIGN_CONTRACT

Zone: DASHBOARD

Human Owner: Anthony Meza

## Purpose

Define the AIOS Dashboard Website as the daily operator interface for the next AIOS phase.

This document is a design contract only. It does not implement dashboard code, trading logic, broker integration, runtime services, validators, tests, scripts, secrets handling, or live-trading behavior.

## Authority Boundary

This contract works under:

- `AGENTS.md`
- `README.md`
- `docs/specs/aios-dashboard-data-contracts.md`
- `docs/forex_delivery/AIOS_MASTER_OPERATOR_DASHBOARD_FOREX_AUTONOMY_BACKLOG_V1.md`
- `docs/forex_delivery/AIOS_AUTO_EXIT_INTELLIGENCE_GATE_V1.md`
- `docs/forex_delivery/AIOS_PL_TRUTH_LAYER_REQUIREMENTS_V1.md`

If this document conflicts with root governance, risk policy, source-of-truth maps, or the broader dashboard data-contract spec, the higher authority wins.

## Operating Model

Dashboard Website = daily operator interface.

PowerShell Terminal = engineering/control plane.

Broker Website = fallback, verification, and emergency manual intervention.

The dashboard is not the PowerShell terminal.

The dashboard is not the broker website.

The dashboard is not a TradingView clone.

The dashboard is minimalist by default.

Advanced diagnostics are hidden by default.

## Truth Contract

The dashboard displays truth.

The dashboard never creates truth.

The dashboard may display approved evidence, status, gate results, recommendations, P/L truth state, auto-exit readiness, and next safe action. It must not create broker truth, runtime truth, approval truth, validator truth, or trading truth.

If evidence is missing, stale, conflicting, or unsafe, the dashboard must display `UNKNOWN`, `STALE`, `MISMATCH`, `INVALID DATA`, or `BLOCKED` instead of implying success.

## Primary Dashboard Inputs

- pair selector
- risk cap
- units / position size
- mode
- confirm
- stop / kill switch

Inputs are operator intent surfaces. They do not bypass approval, risk gates, secret-safe runtime handling, broker boundaries, auto-exit gates, P/L truth requirements, or live-trading restrictions.

## Primary Dashboard Actions

- BUY
- SELL
- ADD POSITION
- REDUCE POSITION
- CLOSE POSITION
- STOP / KILL SWITCH

These actions are contract-level interface targets only. They are not approved implementation behavior. Future execution packets must define exact approval gates, runtime boundaries, risk checks, fail-closed behavior, one-position locks, no-retry rules, and validation before any action can affect a live system.

## Primary Dashboard Outputs

- safe / blocked
- block reason
- AIOS recommendation
- current position
- realized P/L
- unrealized P/L
- exit plan status
- auto-exit ready / blocked
- secret bridge present / missing
- broker bridge armed / blocked
- next action
- SOS if needed

Outputs must be source-backed and sanitized. Missing source evidence must not be rendered as success.

## Allowed Visual Modules

- live watchlist using licensed/broker-permitted data
- single-pair chart window
- read-only machine-room/control-room visualization
- worker status lights
- gate status lights
- P/L panel
- risk panel
- exit brain panel

Live watchlists and charts must use data permitted by the relevant provider terms. TradingView data must not be used for automated trading unless explicitly licensed. Broker or OANDA data may be used only according to provider terms and only after separate approved integration work.

## Hidden By Default

- raw telemetry
- reconciliation internals
- broker adapter internals
- orchestration internals
- queue routing
- packet planning
- validator details
- backend governance noise

Hidden diagnostics may exist as read-only drilldown views in a future approved design, but the default operator view must stay compact, decision-oriented, and beginner-readable.

## Never Display

- API keys
- tokens
- account IDs
- endpoint secrets
- raw broker payloads
- private order identifiers unless explicitly approved

Secret and private-data safety is not a style preference. It is a hard dashboard boundary.

## Safety And Trading Boundary

This contract does not authorize:

- broker API calls
- OANDA integration
- live orders
- real webhooks
- secret access
- environment variable reads
- account lookups
- runtime connector changes
- dashboard-triggered APPLY actions
- validator changes
- staging, committing, pushing, PR creation, or merging

Future dashboard implementation must fail closed when safety, risk, P/L truth, auto-exit readiness, secret-safe runtime handling, or broker bridge status is missing.

## Success Criteria

The dashboard succeeds when the Human Owner can understand:

- can AIOS trade?
- what pair is best?
- what is the risk?
- what position is open?
- what is P/L?
- is auto-exit ready?
- why is AIOS blocked?
- what one action is needed?

The dashboard also succeeds when the Human Owner does not need to inspect raw backend machinery for routine operation.

## Stop Conditions

Stop dashboard expansion if:

- the dashboard would create truth instead of displaying truth
- secret or private data could be exposed
- broker/API behavior would be introduced without approval
- live trading would be implied or enabled without approval
- raw telemetry becomes the default operator surface
- advanced diagnostics crowd the simple operator view
- P/L truth cannot be displayed safely
- auto-exit readiness cannot be sourced
- provider data terms are unclear
- a future implementation packet lacks allowed paths, forbidden paths, validator chain, approval authority, or stop point

