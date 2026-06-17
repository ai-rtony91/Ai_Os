# AIOS Forex Builder OANDA Paper/Demo Mapping

This packet identifies OANDA as the broker target already referenced by repo governance and adds an OANDA-shaped paper/demo mapping layer.

This is not an OANDA API client. It does not import an OANDA SDK, connect to OANDA, read broker credentials, read `.env`, call an OANDA endpoint, access a live account, route a real-money order, or place live orders.

## Broker Target

Repo evidence identifies OANDA as the existing broker target reference:

- `README.md` blocks OANDA integration in the paper-only Trading Lab boundary.
- `RISK_POLICY.md` blocks OANDA or live order execution by default.
- `docs/forex/AIOS_FOREX_DELIVERY_GOVERNED_PACKET.md` references the existing Forex and OANDA boundary.
- `Reports/forex_delivery/AIOS_FOREX_DELIVERY_GOVERNED_APPLY_V2_REPORT.md` records that no OANDA integration was added in the governed readiness packet.

## Contracts Added

- OANDA paper/demo interface requirements
- OANDA paper/demo configuration validation
- OANDA-shaped account-state mapping
- OANDA-shaped market-data mapping
- OANDA-shaped order-state mapping
- OANDA-shaped fill-state mapping
- OANDA-shaped evidence mapping
- Fail-closed live execution rejection
- Fail-closed unsupported action rejection

The separate OANDA demo authentication handoff readiness contract lives in `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_AUTH_HANDOFF.md` and `automation/forex_engine/oanda_demo_auth_handoff.py`. That layer validates sanitized external auth handoff metadata only and still forbids repo-stored credentials, account identifiers, broker requests, network calls, and live execution.

## Configuration Model

The paper/demo configuration model allows only:

- `broker_id: OANDA`
- `account_mode: PRACTICE_DEMO` or `PAPER_DEMO`
- `environment: PRACTICE_REFERENCE_ONLY`
- external auth reference present as a boolean readiness flag
- no repo-stored auth material
- no broker SDK permission
- no network/API permission
- no broker request permission
- no live execution permission

The model fails closed when external auth readiness is missing, when account mode is unsupported, when any live mode is requested, or when sensitive fields are supplied.

## Mapping Boundary

The mapper converts the existing local paper/demo adapter outputs into OANDA-shaped reference records:

- account state
- market data
- order state
- fill state
- evidence

All mapped records remain sanitized and local. They are reference-only contracts for future review, not broker requests.

## Stop Point

Stop at OANDA-shaped paper/demo mapping readiness.

Live broker integration, live account access, repo-stored credentials, OANDA endpoint calls, real-money routing, and live orders remain blocked.
